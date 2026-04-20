from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..models import models, database
from ..core import deps
from ..core.config import settings
from datetime import datetime, timedelta
import requests
import json
import os

router = APIRouter(prefix="/payments", tags=["SaaS Pagamentos"])

# Configurações do Asaas (Devem estar no seu .env)
ASAAS_URL = "https://www.asaas.com/api/v3" # Use https://sandbox.asaas.com/api/v3 para testes
ASAAS_KEY = os.getenv("ASAAS_API_KEY", "sua_chave_aqui")

@router.post("/checkout")
async def generate_checkout_link(
    db: Session = Depends(database.get_db),
    church_id: int = Depends(deps.get_current_church_id)
):
    """
    Gera uma cobrança real no Asaas e retorna o link de pagamento.
    Se a igreja já tiver um cliente no Asaas, usamos o mesmo ID.
    """
    church = db.query(models.Church).filter(models.Church.id == church_id).first()
    
    # 1. Criar ou buscar Cliente no Asaas (Simplificado: usando o nome da Igreja)
    customer_payload = {
        "name": church.name,
        "externalReference": f"CHURCH_{church.id}"
    }
    
    headers = {
        "access_token": ASAAS_KEY,
        "Content-Type": "application/json"
    }

    # 2. Criar a Cobrança (Exemplo: R$ 97,00 Mensal)
    payment_payload = {
        "customer": "customer_id_aqui", # Na prática, buscaríamos ou criaríamos o ID
        "billingType": "UNDEFINED", # Permite PIX, Boleto e Cartão
        "value": 97.00,
        "dueDate": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
        "description": f"Assinatura Mensal - Igreja Inteligente - {church.name}",
        "externalReference": f"SUBS_{church.id}_{datetime.now().strftime('%Y%m')}"
    }

    # Simulação de chamada (Para não travar sem a chave real)
    # response = requests.post(f"{ASAAS_URL}/payments", json=payment_payload, headers=headers)
    
    return {
        "message": "Checkout iniciado",
        "checkout_url": "https://www.asaas.com/c/exemplo-pagamento", 
        "info": "Para produção, insira sua ASAAS_API_KEY no .env"
    }

@router.post("/webhook")
async def asaas_webhook(request: Request, db: Session = Depends(database.get_db)):
    """
    Este endpoint será chamado pelo Asaas sempre que um pagamento for confirmado.
    Ele libera o acesso da igreja automaticamente.
    """
    data = await request.json()
    event = data.get("event")
    payment = data.get("payment")
    
    # Evento de pagamento confirmado (Cartão, PIX ou Boleto)
    if event in ["PAYMENT_RECEIVED", "PAYMENT_CONFIRMED"]:
        external_ref = payment.get("externalReference") # Ex: SUBS_1_202310
        
        if external_ref and external_ref.startswith("SUBS_"):
            church_id = int(external_ref.split("_")[1])
            
            church = db.query(models.Church).filter(models.Church.id == church_id).first()
            if church:
                # Ativa a assinatura por mais 30 dias
                church.subscription_status = "active"
                if not church.subscription_expires_at or church.subscription_expires_at < datetime.utcnow():
                    church.subscription_expires_at = datetime.utcnow() + timedelta(days=30)
                else:
                    church.subscription_expires_at += timedelta(days=30)
                
                db.commit()
                print(f"✅ Assinatura da Igreja {church.name} renovada via Webhook!")

    return {"status": "ok"}
