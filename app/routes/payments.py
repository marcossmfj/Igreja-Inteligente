from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import models, database
from ..core import deps
from datetime import datetime, timedelta
import uuid

router = APIRouter(prefix="/payments", tags=["SaaS Pagamentos"])

@router.post("/checkout")
def generate_checkout_link(church_id: int = Depends(deps.get_current_church_id)):
    """Gera um link de pagamento único para a Igreja assinar o plano."""
    # Aqui entraria a integração real com a API da Stripe ou Asaas
    fake_session_id = str(uuid.uuid4())
    return {
        "message": "Link de checkout gerado com sucesso.",
        "checkout_url": f"https://pay.stripe.com/checkout/{fake_session_id}",
        "warning": "Simulação: Para ativar o plano, chame o Webhook de sucesso enviando o church_id"
    }

@router.post("/webhook-success")
def webhook_payment_success(church_id: int, db: Session = Depends(database.get_db)):
    """A Stripe/Asaas chamará essa rota quando o cartão for aprovado."""
    church = db.query(models.Church).filter(models.Church.id == church_id).first()
    
    if not church:
        raise HTTPException(status_code=404, detail="Igreja não encontrada")
    
    # Ativa a assinatura por 30 dias
    church.subscription_status = "active"
    church.subscription_expires_at = datetime.utcnow() + timedelta(days=30)
    db.commit()
    
    return {"message": "Pagamento confirmado! O SaaS está liberado para sua igreja."}
