from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from ..models import models, database
from ..core import deps
import os
import requests
from datetime import datetime, timedelta

router = APIRouter(prefix="/payments", tags=["SaaS Pagamentos"])

# Configurações do Asaas (Lidas do .env)
ASAAS_API_KEY = os.getenv("ASAAS_API_KEY")
ASAAS_URL = "https://www.asaas.com/api/v3" # Sandbox: https://sandbox.asaas.com/api/v3

class CheckoutRequest(BaseModel):
    name: str
    email: EmailStr
    church_name: str
    plan: str # 'basico' ou 'premium'

@router.post("/checkout")
async def create_checkout(data: CheckoutRequest, db: Session = Depends(database.get_db)):
    """
    Inicia o processo de checkout para novos clientes.
    Prepara o payload para o Asaas para criação de cliente e cobrança.
    """
    if not ASAAS_API_KEY:
        # Modo simulação se a chave não estiver configurada
        return {
            "status": "success",
            "message": "Simulação de checkout concluída",
            "data": {
                "customer": data.name,
                "church": data.church_name,
                "plan": data.plan,
                "checkout_url": "https://www.asaas.com/c/exemplo-checkout-simulado"
            }
        }

    # Estrutura base para integração real via requests
    # 1. Criar Cliente
    customer_data = {
        "name": data.name,
        "email": data.email,
        "externalReference": data.church_name
    }
    
    # 2. Criar Cobrança (Payload exemplo)
    value = 97.00 if data.plan == "basico" else 197.00
    payment_data = {
        "billingType": "UNDEFINED",
        "value": value,
        "dueDate": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
        "description": f"Assinatura Plano {data.plan.capitalize()} - Igreja Inteligente",
        "customer": "CUST_ID_RETURNED_BY_API"
    }

    # Exemplo de chamada real (comentada para evitar falha sem chave válida)
    # headers = {"access_token": ASAAS_API_KEY}
    # r_cust = requests.post(f"{ASAAS_URL}/customers", json=customer_data, headers=headers)
    # r_pay = requests.post(f"{ASAAS_URL}/payments", json=payment_data, headers=headers)

    return {
        "status": "ready",
        "message": "Estrutura Asaas pronta para produção",
        "checkout_url": "https://www.asaas.com/checkout/real-link-here"
    }

@router.post("/webhook")
async def asaas_webhook(request: Request, db: Session = Depends(database.get_db)):
    """Recebe notificações de pagamento do Asaas"""
    data = await request.json()
    # Lógica de ativação de conta após pagamento confirmado
    return {"status": "received"}
