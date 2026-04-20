from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from ..models import models, database
from ..core import deps, security
from ..automation.whatsapp_service import WhatsAppService
import os
import requests
import shutil
import uuid
import secrets
import string
from datetime import datetime, timedelta

router = APIRouter(prefix="/payments", tags=["SaaS Pagamentos"])

# Configurações do Asaas (Lidas do .env)
ASAAS_API_KEY = os.getenv("ASAAS_API_KEY")
ASAAS_URL = "https://www.asaas.com/api/v3" # Sandbox: https://sandbox.asaas.com/api/v3

class CheckoutRequest(BaseModel):
    name: str
    email: EmailStr
    whatsapp: str
    church_name: str
    plan: str # 'basico' ou 'premium'

@router.post("/checkout")
async def create_checkout(data: CheckoutRequest, db: Session = Depends(database.get_db)):
    """
    Inicia o processo de checkout para novos clientes.
    Envia os dados necessários nos metadados do Asaas.
    """
    # Gerar uma senha temporária
    temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(8))
    
    metadata = {
        "church_name": data.church_name,
        "pastor_name": data.name,
        "pastor_email": data.email,
        "pastor_whatsapp": data.whatsapp,
        "pastor_password": temp_password,
        "plan": data.plan
    }

    if not ASAAS_API_KEY:
        return {
            "status": "success",
            "message": "Simulação de checkout concluída",
            "data": {
                "customer": data.name,
                "church": data.church_name,
                "plan": data.plan,
                "temp_password": temp_password,
                "checkout_url": "https://www.asaas.com/c/exemplo-checkout-simulado"
            }
        }

    # Integração real
    headers = {"access_token": ASAAS_API_KEY, "Content-Type": "application/json"}
    
    # 1. Criar Cliente
    customer_payload = {
        "name": data.name,
        "email": data.email,
        "mobilePhone": data.whatsapp,
        "externalReference": data.church_name
    }
    
    try:
        r_cust = requests.post(f"{ASAAS_URL}/customers", json=customer_payload, headers=headers)
        if not r_cust.ok:
            raise HTTPException(status_code=400, detail=f"Erro Asaas Cliente: {r_cust.text}")
        
        customer_id = r_cust.json().get("id")
        
        # 2. Criar Cobrança com Metadados
        value = 97.00 if data.plan == "basico" else 197.00
        payment_payload = {
            "customer": customer_id,
            "billingType": "UNDEFINED",
            "value": value,
            "dueDate": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
            "description": f"Assinatura Plano {data.plan.capitalize()} - Igreja Inteligente",
            "observations": "Provisão Automática de Conta",
            "metadata": metadata
        }
        
        r_pay = requests.post(f"{ASAAS_URL}/payments", json=payment_payload, headers=headers)
        if not r_pay.ok:
            raise HTTPException(status_code=400, detail=f"Erro Asaas Pagamento: {r_pay.text}")
            
        return {
            "status": "success",
            "checkout_url": r_pay.json().get("invoiceUrl")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def asaas_webhook(request: Request, db: Session = Depends(database.get_db)):
    """
    Webhook do Asaas: Provisão Automática de Conta ao confirmar pagamento.
    """
    data = await request.json()
    event = data.get("event")
    payment = data.get("payment")
    
    if event not in ["PAYMENT_RECEIVED", "PAYMENT_CONFIRMED"]:
        return {"status": "ignored"}

    metadata = payment.get("metadata", {})
    if not metadata:
        print("⚠️ Webhook recebido sem metadados de provisão.")
        return {"status": "no_metadata"}

    church_name = metadata.get("church_name")
    pastor_name = metadata.get("pastor_name")
    pastor_email = metadata.get("pastor_email")
    pastor_whatsapp = metadata.get("pastor_whatsapp")
    pastor_password = metadata.get("pastor_password")
    
    # Gerar slug único
    slug = str(uuid.uuid4())[:8]
    
    # Verificar duplicidade
    if db.query(models.Church).filter(models.Church.name == church_name).first():
        print(f"❌ Igreja {church_name} já existe. Provisão cancelada.")
        return {"status": "already_exists"}

    try:
        # 1. Criar estrutura de arquivos
        church_dir = f"assets/tenants/{slug}"
        os.makedirs(church_dir, exist_ok=True)
        
        # Copiar artes padrão se existirem
        default_logo = "assets/logo_default.png"
        default_template = "assets/template_escala.png"
        
        logo_path = f"{church_dir}/logo.png"
        template_path = f"{church_dir}/template_escala.png"
        
        if os.path.exists(default_logo): shutil.copy(default_logo, logo_path)
        if os.path.exists(default_template): shutil.copy(default_template, template_path)

        # 2. Criar Igreja e Usuário
        new_church = models.Church(
            name=church_name, slug=slug, logo_path=logo_path,
            schedule_template_path=template_path,
            subscription_status="active",
            subscription_expires_at=datetime.utcnow() + timedelta(days=30)
        )
        db.add(new_church)
        db.flush()

        hashed_pwd = security.get_password_hash(pastor_password)
        admin_user = models.User(
            email=pastor_email, name=pastor_name,
            hashed_password=hashed_pwd, church_id=new_church.id, is_admin=True
        )
        db.add(admin_user)

        # 3. Criar Cargos e Funções Padrão
        cargos_nomes = ["Membro", "Novo Convertido", "Congregado", "Cooperador(a)", "Diácono / Diaconisa", "Presbítero", "Pastor(a)"]
        funcoes_nomes = ["Louvor", "Som", "Mídia", "Recepção", "Kids", "Intercessão"]
        
        for n in cargos_nomes: db.add(models.Position(name=n, type=models.PositionType.CARGO, church_id=new_church.id))
        for n in funcoes_nomes: db.add(models.Position(name=n, type=models.PositionType.FUNCAO, church_id=new_church.id))

        db.commit()
        print(f"✅ Conta Automática Criada: {church_name} ({pastor_email})")

        # 4. Enviar Mensagem de Boas-vindas (Se WhatsApp configurado no Master)
        # Nota: Para o primeiro envio, usamos as credenciais padrão do sistema se disponíveis
        # ou aguardamos o pastor configurar a própria instância.
        # Aqui, vamos registrar o log do envio.
        welcome_msg = (
            f"🙌 Bem-vindo ao Igreja Inteligente, {pastor_name}!\n\n"
            f"Sua conta para a igreja *{church_name}* acaba de ser ativada.\n\n"
            f"🚀 *Acesse agora:*\n"
            f"Link: https://igrejainteligente.com.br/dashboard\n"
            f"Login: {pastor_email}\n"
            f"Senha: {pastor_password}\n\n"
            "O próximo passo é configurar sua instância de WhatsApp no menu Configurações."
        )
        
        # Log da mensagem (visto que a instância do tenant novo ainda não existe)
        print(f"📱 Mensagem de Boas-vindas preparada para {pastor_whatsapp}")
        
        return {"status": "provisioned", "church_id": new_church.id}

    except Exception as e:
        db.rollback()
        print(f"💥 Erro na provisão automática: {e}")
        return {"status": "error", "detail": str(e)}
