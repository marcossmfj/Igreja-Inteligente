from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session, joinedload
from ..models import database, models
from . import security
from typing import Optional
import logging

# Configuração de log para diagnóstico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importamos o get_db centralizado
from ..models.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

def get_current_user(request: Request, db: Session = Depends(get_db)):
    # 1. Tentar pegar do header Authorization
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]
    else:
        # 2. Se não estiver no header, tentar pegar do query parameter 'token'
        token = request.query_params.get("token")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        logger.warning("Token não fornecido na requisição")
        raise credentials_exception

    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        user_id: str = payload.get("sub")
        # church_id pode ser None para Master Users recém criados sem igreja vinculada
        if user_id is None:
            logger.warning("Token decodificado mas 'sub' está ausente")
            raise credentials_exception
    except JWTError as e:
        logger.error(f"Erro ao decodificar JWT: {str(e)}")
        raise credentials_exception
        
    user = db.query(models.User).options(
        joinedload(models.User.church)
    ).filter(models.User.id == int(user_id)).first()
    
    if user is None:
        logger.warning(f"Usuário ID {user_id} não encontrado no banco")
        raise credentials_exception

    # Se não for Master e a igreja estiver bloqueada, impede acesso
    if not user.is_master:
        if user.church and user.church.subscription_status == "blocked":
            logger.info(f"Acesso negado: Igreja {user.church.name} está BLOQUEADA")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="O acesso a esta igreja está bloqueado. Entre em contato com o suporte."
            )

    return user

def get_current_master_user(current_user: models.User = Depends(get_current_user)) -> models.User:
    """Dependency para garantir que o usuário é um Master Admin"""
    if not current_user.is_master:
        logger.warning(f"Acesso negado ao Master Panel: Usuário {current_user.email} não é Master")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: Requer privilégios de Master Admin"
        )
    return current_user

def get_current_church_id(current_user: models.User = Depends(get_current_user)) -> int:
    """Dependency para extrair magicamente o church_id e isolar dados (Multitenancy)"""
    # Se for Master e não tiver igreja, retorna 0 ou None (depende de como as rotas master lidam)
    return current_user.church_id or 0
