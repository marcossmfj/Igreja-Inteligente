from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from sqlalchemy import extract
from ..models import database, models
from .whatsapp_service import WhatsAppService
from .image_gen import gerar_card_aniversariantes
from datetime import datetime, timedelta
import os

def log_notification(db: Session, phone: str, msg_type: str, ref_id: int, church_id: int):
    log = models.NotificationLog(
        target_phone=phone,
        message_type=msg_type,
        reference_id=ref_id,
        church_id=church_id
    )
    db.add(log)
    db.commit()

def check_reminder_24h():
    """Lembrete de escala para o dia seguinte"""
    db = database.SessionLocal()
    tomorrow = (datetime.now() + timedelta(days=1)).date()
    
    schedules = db.query(models.Schedule).filter(
        models.Schedule.event_date >= tomorrow,
        models.Schedule.event_date < tomorrow + timedelta(days=1),
        models.Schedule.confirmed == False # Apenas não confirmados? Ou todos? Vamos enviar para todos como lembrete.
    ).all()

    for sch in schedules:
        # Verifica se já enviamos lembrete hoje
        already_sent = db.query(models.NotificationLog).filter(
            models.NotificationLog.message_type == 'reminder',
            models.NotificationLog.reference_id == sch.id,
            models.NotificationLog.sent_at >= datetime.now().replace(hour=0, minute=0, second=0)
        ).first()

        if not already_sent:
            church = sch.church
            ws = WhatsAppService(church)
            pos_name = sch.position.name if sch.position else "Voluntário"
            msg = f"Olá {sch.member.name}, passando para lembrar seu compromisso amanhã na escala de *{pos_name}*. Contamos com você! 🙏"
            if ws.send_text(sch.member.whatsapp, msg):
                log_notification(db, sch.member.whatsapp, 'reminder', sch.id, church.id)
    db.close()

def check_welcome_visitors():
    """Boas-vindas para quem se cadastrou ontem"""
    db = database.SessionLocal()
    yesterday = (datetime.now() - timedelta(days=1)).date()
    
    visitors = db.query(models.Member).filter(
        models.Member.status == models.MemberStatus.VISITANTE,
        models.Member.created_at >= yesterday,
        models.Member.created_at < yesterday + timedelta(days=1)
    ).all()

    for v in visitors:
        church = v.church
        ws = WhatsAppService(church)
        msg = f"Olá {v.name}! Foi uma alegria ter você connosco ontem na {church.name}. Esperamos vê-lo novamente em breve! 🙏✨"
        if ws.send_text(v.whatsapp, msg):
            log_notification(db, v.whatsapp, 'welcome', v.id, church.id)
    db.close()

def check_birthdays_daily():
    """Parabéns aos aniversariantes do dia"""
    db = database.SessionLocal()
    today = datetime.now()
    
    # Filtra membros que fazem aniversário hoje (dia e mês)
    bday_members = db.query(models.Member).filter(
        models.Member.status == models.MemberStatus.ATIVO,
        extract('day', models.Member.birth_date) == today.day,
        extract('month', models.Member.birth_date) == today.month
    ).all()

    for b in bday_members:
        church = b.church
        ws = WhatsAppService(church)
        card_path = f"assets/birthdays/{b.id}_{today.strftime('%Y%m%d')}.png"
        image_gen.generate_birthday_card(b.name, card_path)
        
        msg = f"🎂 Parabéns {b.name}! A {church.name} deseja-lhe um dia abençoado e cheio de alegria!"
        if ws.send_image(b.whatsapp, msg, card_path):
            log_notification(db, b.whatsapp, 'birthday', b.id, church.id)
    db.close()

def check_birthdays_weekly():
    """Gera e envia card de aniversariantes da semana para o Pastor"""
    db = database.SessionLocal()
    churches = db.query(models.Church).all()
    
    today = datetime.now()
    start_week = today.date()
    end_week = (today + timedelta(days=7)).date()

    for church in churches:
        # Busca aniversariantes da semana
        birthdays = db.query(models.Member).filter(
            models.Member.church_id == church.id,
            models.Member.status == models.MemberStatus.ATIVO,
            models.Member.birth_date.isnot(None)
        ).all()

        aniv_lista = []
        for m in birthdays:
            # Lógica simplificada de "está na semana" (ignora ano)
            m_date = m.birth_date.replace(year=today.year)
            if start_week <= m_date.date() <= end_week:
                aniv_lista.append((m.name, m.birth_date.day))

        if aniv_lista:
            output_path = f"assets/aniv_{church.slug}_{today.strftime('%Y%W')}.png"
            gerar_card_aniversariantes(aniv_lista, "Semana", output_path)
            
            # Enviar para o Pastor (Primeiro admin da igreja)
            pastor = db.query(models.User).filter(models.User.church_id == church.id, models.User.is_admin == True).first()
            if pastor:
                ws = WhatsAppService(church)
                # Como User não tem WhatsApp cadastrado no modelo, vamos buscar um membro com cargo de Pastor ou usar o email como fallback se for numero
                # Para este MVP, vamos assumir que o sistema envia para o primeiro admin se houver telefone ou logamos no console.
                # Melhor: enviar para o grupo da igreja se cadastrado na Church.
                print(f"Card de aniversariantes gerado para {church.name}: {output_path}")
                # ws.send_image("NUMERO_DO_GRUPO_OU_PASTOR", "Aqui estão os aniversariantes da semana! 🎉", output_path)

    db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    # 1. Lembrete de Escala (Todo dia às 09:00)
    scheduler.add_job(check_reminder_24h, 'cron', hour=9, minute=0)
    # 2. Boas-vindas Visitantes (Todo dia às 10:00)
    scheduler.add_job(check_welcome_visitors, 'cron', hour=10, minute=0)
    # 3. Aniversariantes do Dia (Todo dia às 08:30)
    scheduler.add_job(check_birthdays_daily, 'cron', hour=8, minute=30)
    # 4. Aniversariantes da Semana (Segunda-feira às 08:00)
    scheduler.add_job(check_birthdays_weekly, 'cron', day_of_week='mon', hour=8, minute=0)
    
    scheduler.start()
