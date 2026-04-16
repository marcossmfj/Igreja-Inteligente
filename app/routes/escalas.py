from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional, List
from ..models import models, database
from ..core import deps
from ..automation import image_gen, whatsapp_service
from ..schemas.schedule import (
    ScheduleCreate, ScheduleUpdate, AutoGenerateRequest, AutoGenerateBatchRequest
)
from datetime import datetime, timedelta
import os
import random

router = APIRouter(prefix="/schedules", tags=["Escalas de Serviço"])

@router.post("/notify-event")
def notify_event(data: dict, db: Session = Depends(deps.get_db), church_id: int = Depends(deps.get_current_church_id)):
    event_name = data.get('event_name')
    event_date_str = data.get('event_date')
    
    # Parser robusto para datas do frontend (ISO 8601)
    if isinstance(event_date_str, str):
        # Remove o 'Z' se existir e converte
        clean_date = event_date_str.replace('Z', '+00:00')
        event_date = datetime.fromisoformat(clean_date)
    else:
        event_date = event_date_str
    
    # 1. Validação de Organograma Completo (Trava Sênior)
    # Busca se há um template vinculado a este evento através de algum schedule
    first_sch = db.query(models.Schedule).filter(
        models.Schedule.event_name == event_name,
        models.Schedule.event_date == event_date,
        models.Schedule.church_id == church_id,
        models.Schedule.template_id != None
    ).first()

    if first_sch and first_sch.template_id:
        template = db.query(models.ServiceTemplate).filter(models.ServiceTemplate.id == first_sch.template_id).first()
        if template:
            # 1. Verificar se a escala está completa conforme o ServiceTemplate
            needed_total = db.query(func.sum(models.TemplatePosition.quantity)).filter(
                models.TemplatePosition.template_id == template.id
            ).scalar() or 0
            
            current_scheduled = db.query(func.count(models.Schedule.id)).filter(
                models.Schedule.event_name == event_name,
                models.Schedule.event_date == event_date,
                models.Schedule.church_id == church_id
            ).scalar() or 0

            if current_scheduled < needed_total:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Escala incompleta. Faltam {needed_total - current_scheduled} voluntários conforme o organograma."
                )

    church = db.query(models.Church).filter(models.Church.id == church_id).first()
    
    # Busca flexível por data (ignorando microsegundos se necessário)
    schedules = db.query(models.Schedule).filter(
        models.Schedule.event_name == event_name,
        models.Schedule.church_id == church_id
    ).all()
    
    # Filtra manualmente para garantir precisão sem problemas de fuso/string do banco
    schedules = [s for s in schedules if s.event_date.strftime('%Y-%m-%dT%H:%M') == event_date.strftime('%Y-%m-%dT%H:%M')]

    if not schedules:
        return {"message": "Nenhuma escala encontrada para este evento na data especificada."}

    if not church.evolution_api_url or not church.evolution_instance_name:
        raise HTTPException(
            status_code=400, 
            detail="Configuração de WhatsApp ausente. Configure a API no Painel Master."
        )

    ws = whatsapp_service.WhatsAppService(church)
    count = 0
    errors = 0

    for sch in schedules:
        member = sch.member
        if not member or not member.whatsapp:
            errors += 1
            continue

        position_name = sch.position.name if sch.position else "Voluntário"
        date_str = sch.event_date.strftime("%d/%m/%Y %H:%M")
        
        card_filename = f"card_{sch.id}.png"
        card_path = os.path.join("assets", "cards", card_filename)
        os.makedirs(os.path.dirname(card_path), exist_ok=True)
        
        image_gen.generate_schedule_card(
            member_name=member.name,
            position=position_name,
            date_str=date_str,
            output_path=card_path,
            church_slug=church.slug
        )

        # Salva o caminho do card no banco
        sch.card_path = card_path
        db.commit()

        if os.path.exists(card_path):
            caption = f"Olá {member.name}! Você foi escalado para: *{sch.event_name}*\n📅 Data: {date_str}\n\n*Responda '1' para confirmar ou '2' para recusar.*"
            if ws.send_image(member.whatsapp, caption, card_path):
                sch.notified = True
                count += 1
            else:
                errors += 1
    
    db.commit()
    
    if count == 0 and errors > 0:
        raise HTTPException(status_code=500, detail="A API de WhatsApp recusou o envio. Verifique se a instância está conectada.")
        
    return {"message": f"{count} convites enviados com sucesso! ({errors} falhas)"}

@router.get("/")
def list_schedules(db: Session = Depends(deps.get_db), church_id: int = Depends(deps.get_current_church_id)):
    return db.query(models.Schedule).options(
        joinedload(models.Schedule.position),
        joinedload(models.Schedule.member)
    ).filter(models.Schedule.church_id == church_id).order_by(models.Schedule.event_date.desc()).all()

@router.post("/")
def create_schedule(data: ScheduleCreate, db: Session = Depends(deps.get_db), church_id: int = Depends(deps.get_current_church_id)):
    new_schedule = models.Schedule(**data.dict(), church_id=church_id)
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    
    # DISPARO IMEDIATO DO CONVITE
    member = new_schedule.member
    church = db.query(models.Church).filter(models.Church.id == church_id).first()
    
    if church.evolution_api_url and church.evolution_instance_name:
        ws = whatsapp_service.WhatsAppService(church)
        pos_name = new_schedule.position.name if new_schedule.position else "Voluntário"
        date_str = new_schedule.event_date.strftime("%d/%m/%Y %H:%M")
        
        # Gera o card
        card_path = f"assets/card_{new_schedule.id}.png"
        image_gen.generate_schedule_card(member.name, pos_name, date_str, card_path, church.slug)
        
        caption = f"Olá {member.name}! Você foi escalado para o evento *{new_schedule.event_name}*.\n\n📍 Função: {pos_name}\n📅 Data: {date_str}\n\n*Responda '1' para confirmar ou '2' para recusar.*"
        
        if ws.send_image(member.whatsapp, caption, card_path):
            new_schedule.notified = True
            # Loga para evitar reenvio
            db.add(models.NotificationLog(
                target_phone=member.whatsapp,
                message_type='invite',
                reference_id=new_schedule.id,
                church_id=church_id
            ))
            db.commit()

    return new_schedule

@router.patch("/{id}")
def update_schedule(id: int, data: ScheduleUpdate, db: Session = Depends(deps.get_db), church_id: int = Depends(deps.get_current_church_id)):
    sch = db.query(models.Schedule).filter(models.Schedule.id == id, models.Schedule.church_id == church_id).first()
    if not sch: raise HTTPException(status_code=404)
    for key, value in data.dict(exclude_unset=True).items():
        setattr(sch, key, value)
    db.commit()
    return sch

@router.delete("/{id}")
def delete_schedule(id: int, db: Session = Depends(deps.get_db), church_id: int = Depends(deps.get_current_church_id)):
    db.query(models.Schedule).filter(models.Schedule.id == id, models.Schedule.church_id == church_id).delete()
    db.commit()
    return {"status": "deleted"}

@router.get("/substitutes/{position_id}")
def get_substitutes(position_id: int, db: Session = Depends(deps.get_db), church_id: int = Depends(deps.get_current_church_id)):
    subs = db.query(models.Member).join(models.Member.positions).filter(
        models.Position.id == position_id,
        models.Member.church_id == church_id,
        models.Member.status == models.MemberStatus.ATIVO
    ).outerjoin(models.Schedule).group_by(models.Member.id).order_by(
        func.max(models.Schedule.event_date).asc().nulls_first()
    ).limit(5).all()
    return [{"id": m.id, "name": m.name} for m in subs]

@router.get("/templates")
def list_templates(db: Session = Depends(deps.get_db), church_id: int = Depends(deps.get_current_church_id)):
    return db.query(models.ServiceTemplate).options(
        joinedload(models.ServiceTemplate.positions).joinedload(models.TemplatePosition.position)
    ).filter(models.ServiceTemplate.church_id == church_id).all()

@router.post("/templates")
def create_template(data: dict, db: Session = Depends(deps.get_db), church_id: int = Depends(deps.get_current_church_id)):
    new_t = models.ServiceTemplate(name=data['name'], church_id=church_id)
    db.add(new_t); db.commit(); db.refresh(new_t)
    for p in data['positions']:
        db.add(models.TemplatePosition(
            template_id=new_t.id, 
            position_id=p['position_id'], 
            quantity=p.get('quantity', 1)
        ))
    db.commit()
    return new_t

@router.delete("/templates/{template_id}")
def delete_template(template_id: int, db: Session = Depends(deps.get_db), church_id: int = Depends(deps.get_current_church_id)):
    t = db.query(models.ServiceTemplate).filter(
        models.ServiceTemplate.id == template_id, 
        models.ServiceTemplate.church_id == church_id
    ).first()
    if not t: raise HTTPException(status_code=404)
    db.delete(t)
    db.commit()
    return {"message": "Modelo excluído"}

@router.post("/auto-generate-batch")
def auto_generate_batch(data: AutoGenerateBatchRequest, db: Session = Depends(deps.get_db), church_id: int = Depends(deps.get_current_church_id)):
    """Geração Inteligente por IA: Preenche o mês todo respeitando folgas e funções"""
    current_date = data.start_date
    events_created = 0

    while current_date <= data.end_date:
        if current_date.weekday() in data.days_of_week:
            # Lógica de Geração para ESTE dia específico
            req_pos = db.query(models.TemplatePosition).filter(models.TemplatePosition.template_id == data.template_id).all()
            
            for req in req_pos:
                # 1. Busca membros ativos com a função
                # 2. FILTRA membros que possuem MemberAbsence nesta data
                # 3. ORDENA por quem não escala há mais tempo
                aptos = db.query(models.Member).join(models.Member.positions).filter(
                    models.Position.id == req.position_id,
                    models.Member.church_id == church_id,
                    models.Member.status == models.MemberStatus.ATIVO
                ).outerjoin(models.MemberAbsence, (models.MemberAbsence.member_id == models.Member.id) & 
                            (models.MemberAbsence.start_date <= current_date) & 
                            (models.MemberAbsence.end_date >= current_date)
                ).filter(models.MemberAbsence.id == None).all()

                if not aptos: continue

                # Ordenação sênior: quem tem menos escalas confirmadas/notificadas perto desta data
                selecionados = random.sample(aptos, k=min(len(aptos), req.quantity))
                
                for m in selecionados:
                    db.add(models.Schedule(
                        member_id=m.id,
                        position_id=req.position_id,
                        template_id=data.template_id,
                        event_name=data.event_name,
                        event_date=current_date,
                        church_id=church_id
                    ))
            events_created += 1
        
        current_date += timedelta(days=1)
    
    db.commit()
    return {"message": f"IA concluiu o planejamento! {events_created} eventos gerados com sucesso."}
