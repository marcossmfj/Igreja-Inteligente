from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from ..models import models, database
from ..core import deps
from typing import List
from ..schemas.member import MemberSchema, MemberUpdateSchema, MemberPromoteSchema
from datetime import datetime

router = APIRouter(prefix="/visitors", tags=["Gestão de Visitantes"])

@router.get("/", response_model=List[MemberSchema])
def list_visitors(
    db: Session = Depends(database.get_db),
    church_id: int = Depends(deps.get_current_church_id)
):
    """Lista todos os visitantes ativos da igreja"""
    return db.query(models.Member).filter(
        models.Member.church_id == church_id,
        models.Member.status == models.MemberStatus.VISITANTE
    ).order_by(models.Member.created_at.desc()).all()

@router.post("/", response_model=MemberSchema)
def add_visitor(
    data: MemberUpdateSchema,
    db: Session = Depends(database.get_db),
    church_id: int = Depends(deps.get_current_church_id)
):
    """Registra um novo visitante e inicia o fluxo de boas-vindas"""
    new_visitor = models.Member(
        name=data.name,
        whatsapp=data.whatsapp,
        status=models.MemberStatus.VISITANTE,
        endereco=data.endereco,
        church_id=church_id,
        created_at=datetime.utcnow()
    )
    db.add(new_visitor)
    db.commit()
    db.refresh(new_visitor)
    
    # Nota: O robô de automação (tasks.py) detectará este novo 
    # visitante e enviará as boas-vindas automaticamente amanhã.
    
    return new_visitor

@router.patch("/{visitor_id}/promote")
def promote_to_member(
    visitor_id: int,
    data: MemberPromoteSchema,
    db: Session = Depends(database.get_db),
    church_id: int = Depends(deps.get_current_church_id)
):
    """Transforma um visitante em membro ativo, vinculando cargos e funções"""
    visitor = db.query(models.Member).filter(
        models.Member.id == visitor_id,
        models.Member.church_id == church_id
    ).first()
    
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitante não encontrado")

    # 1. Atualiza Status
    visitor.status = models.MemberStatus.ATIVO
    visitor.data_batismo = datetime.utcnow() # Assume data de hoje se não informada
    
    # 2. Vincula Cargos e Funções selecionados no Modal de Promoção
    all_pos_ids = [data.cargo_id] + (data.funcao_ids or [])
    positions = db.query(models.Position).filter(
        models.Position.id.in_(all_pos_ids),
        models.Position.church_id == church_id
    ).all()
    
    visitor.positions = positions
    
    db.commit()
    db.refresh(visitor)
    return {"message": f"{visitor.name} agora é um Membro Ativo!", "member": visitor}

@router.delete("/{visitor_id}")
def delete_visitor(
    visitor_id: int,
    db: Session = Depends(database.get_db),
    church_id: int = Depends(deps.get_current_church_id)
):
    """Remove um registro de visitante"""
    visitor = db.query(models.Member).filter(
        models.Member.id == visitor_id,
        models.Member.church_id == church_id
    ).first()
    
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitante não encontrado")
        
    db.delete(visitor)
    db.commit()
    return {"message": "Visitante removido"}
