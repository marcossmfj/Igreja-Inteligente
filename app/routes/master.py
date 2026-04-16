from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import models, database
from ..core import security, deps
import os
import shutil
import requests
from typing import Optional

router = APIRouter(
    prefix="/master", 
    tags=["Super Admin"],
    dependencies=[Depends(deps.get_current_master_user)]
)

@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(database.get_db),
    church_id: int = Depends(deps.get_current_church_id)
):
    """Retorna estatísticas para o Dashboard Pastoral"""
    # Se for Master e não tiver igreja, retorna estatísticas globais
    query_base = db.query(models.Member).filter(models.Member.status != models.MemberStatus.EXCLUIDO)
    if church_id > 0:
        query_base = query_base.filter(models.Member.church_id == church_id)

    total_members = query_base.count()
    ativos = query_base.filter(models.Member.status == models.MemberStatus.ATIVO).count()
    visitantes = query_base.filter(models.Member.status == models.MemberStatus.VISITANTE).count()

    conv_rate = (ativos / (ativos + visitantes) * 100) if (ativos + visitantes) > 0 else 0

    return {
        "total_members": total_members,
        "total_visitors": visitantes,
        "conversion_rate": round(conv_rate, 2)
    }

@router.post("/register-church")
async def register_new_tenant(
    church_name: str = Form(...),
    slug: str = Form(...),
    pastor_email: str = Form(...),
    pastor_password: str = Form(...),
    evolution_api_url: Optional[str] = Form(None),
    evolution_api_key: Optional[str] = Form(None),
    logo: Optional[UploadFile] = File(None),
    schedule_template: Optional[UploadFile] = File(None),
    db: Session = Depends(database.get_db)
):
    # Rest of the function...
    # 1. Validações prévias
    if db.query(models.Church).filter(models.Church.slug == slug).first():
        raise HTTPException(status_code=400, detail="Este subdomínio (slug) já está em uso.")
    
    if db.query(models.Church).filter(models.Church.name == church_name).first():
        raise HTTPException(status_code=400, detail="Este nome de igreja já está em uso.")
        
    if db.query(models.User).filter(models.User.email == pastor_email).first():
        raise HTTPException(status_code=400, detail="Este e-mail de administrador já está em uso.")

    # 2. Criação da estrutura de arquivos
    church_dir = f"assets/tenants/{slug}"
    os.makedirs(church_dir, exist_ok=True)
    
    logo_path = f"{church_dir}/logo.png"
    template_path = f"{church_dir}/template_escala.png"
    
    try:
        if logo:
            with open(logo_path, "wb") as buffer: shutil.copyfileobj(logo.file, buffer)
        if schedule_template:
            with open(template_path, "wb") as buffer: shutil.copyfileobj(schedule_template.file, buffer)

        # 3. Criação dos registros no banco (em uma única transação)
        instance_name = f"instancia_{slug}"
        new_church = models.Church(
            name=church_name, slug=slug, logo_path=logo_path,
            schedule_template_path=template_path, evolution_instance_name=instance_name,
            evolution_api_url=evolution_api_url, evolution_api_key=evolution_api_key
        )
        db.add(new_church)
        db.flush() # Para obter o ID sem commitar ainda

        hashed_pwd = security.get_password_hash(pastor_password)
        admin_user = models.User(
            email=pastor_email, name=f"Admin {church_name}",
            hashed_password=hashed_pwd, church_id=new_church.id, is_admin=True
        )
        db.add(admin_user)

        # 4. Criar Cargos e Funções Padrão
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

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno ao criar igreja: {str(e)}")

    return {"message": "Igreja criada com sucesso!"}

@router.patch("/update-church/{church_id}")
async def update_church(
    church_id: int,
    church_name: Optional[str] = Form(None),
    pastor_email: Optional[str] = Form(None),
    pastor_password: Optional[str] = Form(None),
    evolution_api_url: Optional[str] = Form(None),
    evolution_api_key: Optional[str] = Form(None),
    logo: Optional[UploadFile] = File(None),
    schedule_template: Optional[UploadFile] = File(None),
    db: Session = Depends(database.get_db)
):
    """EDICAO DE CLIENTE: Atualiza dados e artes da igreja selecionada"""
    church = db.query(models.Church).filter(models.Church.id == church_id).first()
    if not church: raise HTTPException(status_code=404, detail="Igreja não encontrada")

    if church_name: church.name = church_name
    if evolution_api_url: church.evolution_api_url = evolution_api_url
    if evolution_api_key: church.evolution_api_key = evolution_api_key
    
    # Atualizar artes se enviadas
    if logo:
        with open(church.logo_path, "wb") as buffer: shutil.copyfileobj(logo.file, buffer)
    if schedule_template:
        with open(church.schedule_template_path, "wb") as buffer: shutil.copyfileobj(schedule_template.file, buffer)

    # Atualizar Pastor se dados enviados
    if pastor_email or pastor_password:
        user = db.query(models.User).filter(models.User.church_id == church.id, models.User.is_admin == True).first()
        if user:
            if pastor_email: user.email = pastor_email
            if pastor_password: user.hashed_password = security.get_password_hash(pastor_password)

    db.commit()
    return {"message": "Igreja atualizada com sucesso!"}

@router.get("/tenants")
def list_tenants(
    db: Session = Depends(database.get_db)
):
    # Retorna as igrejas, o email do pastor admin e a contagem de pessoas
    tenants = db.query(models.Church).all()
    result = []
    for t in tenants:
        pastor = db.query(models.User).filter(models.User.church_id == t.id, models.User.is_admin == True).first()
        people_count = db.query(models.Member).filter(models.Member.church_id == t.id).count()
        result.append({
            "id": t.id, "name": t.name, "slug": t.slug, 
            "evolution_instance_name": t.evolution_instance_name,
            "evolution_api_url": t.evolution_api_url,
            "evolution_api_key": t.evolution_api_key,
            "subscription_status": t.subscription_status,
            "pastor_email": pastor.email if pastor else "",
            "total_people": people_count
        })
    return result

@router.delete("/delete-church/{church_id}")
def delete_church(
    church_id: int, 
    db: Session = Depends(database.get_db)
):
    """Exclui uma igreja e todos os seus dados (Cascata configurada no models.py)"""
    church = db.query(models.Church).filter(models.Church.id == church_id).first()
    if not church: raise HTTPException(status_code=404, detail="Igreja não encontrada")
    
    # Excluir diretório de assets
    church_dir = f"assets/tenants/{church.slug}"
    if os.path.exists(church_dir):
        shutil.rmtree(church_dir)
        
    db.delete(church)
    db.commit()
    return {"message": "Igreja e todos os seus dados foram excluídos permanentemente."}

@router.patch("/toggle-status/{church_id}")
def toggle_church_status(
    church_id: int, 
    db: Session = Depends(database.get_db)
):
    """Bloqueia ou Desbloqueia o uso da plataforma para uma igreja"""
    church = db.query(models.Church).filter(models.Church.id == church_id).first()
    if not church: raise HTTPException(status_code=404, detail="Igreja não encontrada")
    
    church.subscription_status = "blocked" if church.subscription_status == "active" else "active"
    db.commit()
    return {"message": f"Status da igreja alterado para {church.subscription_status}"}
