from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import models, database
from ..automation import whatsapp_service
from datetime import datetime

router = APIRouter(prefix="/webhooks", tags=["WhatsApp Webhooks"])

@router.post("/evolution")
async def evolution_webhook(request: Request, db: Session = Depends(database.get_db)):
    data = await request.json()
    
    try:
        remote_jid = data.get('data', {}).get('key', {}).get('remoteJid', '')
        if not remote_jid:
            return {"status": "ignored"}
            
        phone = remote_jid.split('@')[0]
        text = data.get('data', {}).get('message', {}).get('conversation', '').strip()
        
        member = db.query(models.Member).filter(models.Member.whatsapp.contains(phone)).first()
        if not member:
            return {"status": "member_not_found"}

        church = db.query(models.Church).filter(models.Church.id == member.church_id).first()
        ws = None
        if church.evolution_api_url and church.evolution_instance_name:
            ws = whatsapp_service.WhatsAppService(church)

        schedule = db.query(models.Schedule).filter(
            models.Schedule.member_id == member.id,
            models.Schedule.confirmed == False,
            models.Schedule.rejected == False
        ).order_by(models.Schedule.event_date.desc()).first()
        
        if not schedule:
            return {"status": "no_pending_schedule"}

        if text == "1":
            schedule.confirmed = True
            member.consecutive_refusals = 0 # Zera contador ao confirmar
            db.commit()
            if ws:
                ws.send_text(member.whatsapp, "✅ Sua presença foi confirmada! Deus te abençoe.")

        elif text == "2":
            schedule.rejected = True
            member.consecutive_refusals += 1 # Incrementa recusas
            db.commit()
            
            # 1. Lógica de Cuidado Pastoral
            if member.consecutive_refusals >= 3:
                # Alerta Pastor (Primeiro admin da igreja)
                pastor = db.query(models.User).filter(
                    models.User.church_id == member.church_id,
                    models.User.is_admin == True
                ).first()
                
                if pastor and ws and pastor.whatsapp:
                    alert_msg = f"⚠️ *ALERTA PASTORAL*: O membro {member.name} recusou a {member.consecutive_refusals}ª escala consecutiva. Recomendamos um contacto pessoal."
                    ws.send_text(pastor.whatsapp, alert_msg)
            
            if ws:
                ws.send_text(member.whatsapp, "❌ Sua recusa foi registrada. O Pastor será notificado.")

            # 2. Lógica de Substituição Inteligente
            if schedule.position_id:
                substitute = db.query(models.Member).join(models.Member.positions).filter(
                    models.Position.id == schedule.position_id,
                    models.Member.id != member.id,
                    models.Member.status == models.MemberStatus.ATIVO,
                    models.Member.church_id == member.church_id
                ).outerjoin(models.Schedule, (models.Schedule.member_id == models.Member.id) & (models.Schedule.confirmed == True)).order_by(
                    models.Schedule.event_date.asc().nulls_first()
                ).first()

                if substitute:
                    # Encontrar o Pastor para enviar a sugestão
                    pastor = db.query(models.User).filter(
                        models.User.church_id == member.church_id,
                        models.User.is_admin == True
                    ).first()

                    if pastor and ws and pastor.whatsapp:
                        sub_msg = f"🚨 *Substituição Necessária*: {member.name} recusou para {schedule.event_name}.\n\n*Sugestão:* {substitute.name} (está há mais tempo sem servir)."
                        ws.send_text(pastor.whatsapp, sub_msg)

    except Exception as e:
        print(f"Erro processando webhook: {e}")
        
    return {"status": "success"}
