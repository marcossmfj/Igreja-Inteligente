from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from ..models import database, models
from ..core import security
from ..schemas.auth import ChurchRegister

router = APIRouter(prefix="/auth", tags=["Autenticação e Registro SaaS"])

@router.post("/register")
def register_church(data: ChurchRegister, db: Session = Depends(database.get_db)):
    """Rota de Onboarding: Cria a Igreja e o seu primeiro usuário Administrador"""
    
    # Verifica se a igreja ou o email já existem
    if db.query(models.Church).filter(models.Church.name == data.church_name).first():
        raise HTTPException(status_code=400, detail="Nome de Igreja já cadastrado")
    if db.query(models.User).filter(models.User.email == data.admin_email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    # 1. Cria a Igreja (Tenant)
    new_church = models.Church(name=data.church_name)
    db.add(new_church)
    db.commit()
    db.refresh(new_church)

    # 2. Cria o Usuário vinculando-o à Igreja recém-criada
    hashed_pwd = security.get_password_hash(data.admin_password)
    new_user = models.User(
        email=data.admin_email,
        name=data.admin_name,
        hashed_password=hashed_pwd,
        church_id=new_church.id,
        is_admin=True
    )
    db.add(new_user)
    
    # 3. Criar Cargos e Funções Padrão (Essencial para o funcionamento do sistema)
    cargos_nomes = [
        "Membro", "Novo Convertido", "Congregado", "Cooperador(a)", 
        "Diácono / Diaconisa", "Presbítero", "Evangelista", 
        "Missionário(a)", "Pastor(a)", "Bispo(a)", "Apóstolo(a)", "Reverendo(a)"
    ]
    funcoes_nomes = [
        "Líder de Louvor", "Vocal / Backing", "Guitarra", "Violão", "Teclado / Piano", 
        "Baixo", "Bateria / Percussão", "Saxofone / Metais", "Sonoplastia (Som)", 
        "Projeção (Mídia)", "Transmissão (Live)", "Social Media / Design", 
        "Fotografia / Vídeo", "Recepção / Boas-vindas", "Acolhimento / Consolidação", 
        "Ministério Infantil (Kids)", "Berçário", "Ministério de Juniores", 
        "Ministério de Adolescentes", "Ministério de Jovens", "Ministério de Casais", 
        "Ministério de Homens", "Ministério de Mulheres", "Terceira Idade", 
        "Intercessão / Oração", "Discipulado", "Evangelismo", "Missões", 
        "Teatro / Dança", "Limpeza / Zeladoria", "Manutenção", "Segurança / Ordem", 
        "Estacionamento", "Cozinha / Cantina", "Tesouraria", "Secretaria"
    ]
    
    for n in cargos_nomes:
        db.add(models.Position(name=n, type=models.PositionType.CARGO, church_id=new_church.id))
    for n in funcoes_nomes:
        db.add(models.Position(name=n, type=models.PositionType.FUNCAO, church_id=new_church.id))

    db.commit()
    db.refresh(new_church)

    return {"message": "Sua Igreja foi registrada com sucesso no SaaS!", "church_id": new_church.id}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    """Login para todos os usuários do SaaS (Pastores, Secretários)"""
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Payload contém sub (user_id) e church_id (O Segredo do Multi-tenant)
    access_token = security.create_access_token(
        data={"sub": str(user.id), "church_id": str(user.church_id)}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "church_id": user.church_id,
        "user_name": user.name,
        "church_name": user.church.name if user.church else "SaaS Master",
        "is_master": user.is_master
    }
