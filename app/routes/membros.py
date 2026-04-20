from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from ..models import models
from ..core import deps
from fpdf import FPDF
from fastapi.responses import Response
from typing import List
from ..schemas.member import (
    PositionCreate, PositionSchema, MemberSchema, MemberCreateWithPositions, 
    MemberUpdateSchema, MemberPromoteSchema
)

router = APIRouter(prefix="/members", tags=["Membros & Cargos"])

@router.post("/", response_model=MemberSchema)
def create_member_basic(
    data: MemberUpdateSchema, # Reaproveitamos o schema de update que tem os campos opcionais
    db: Session = Depends(deps.get_db),
    church_id: int = Depends(deps.get_current_church_id)
):
    """Cria um membro básico (como visitantes)"""
    new_member = models.Member(
        name=data.name,
        whatsapp=data.whatsapp,
        status=data.status or models.MemberStatus.VISITANTE,
        endereco=data.endereco,
        data_batismo=data.data_batismo,
        church_id=church_id
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member

@router.get("/export-pdf")
def export_members_pdf(
    db: Session = Depends(deps.get_db),
    church_id: int = Depends(deps.get_current_church_id)
):
    members = db.query(models.Member).filter(
        models.Member.church_id == church_id,
        models.Member.status != models.MemberStatus.EXCLUIDO
    ).all()

    pdf = FPDF(orientation='L', unit='mm', format='A4') # Paisagem para caber mais colunas
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    
    # Garantir que o texto seja compatível com latin-1 para evitar erros no FPDF2 com fontes padrão
    title = "Relatório Geral de Membros e Visitantes - Igreja Inteligente"
    pdf.cell(277, 10, title.encode('latin-1', 'replace').decode('latin-1'), ln=True, align="C")
    pdf.ln(10)

    # Header da Tabela
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(60, 10, "Nome", border=1, fill=True)
    pdf.cell(35, 10, "WhatsApp", border=1, fill=True)
    pdf.cell(30, 10, "Status", border=1, fill=True)
    pdf.cell(90, 10, "Endereco", border=1, fill=True)
    pdf.cell(30, 10, "Batismo", border=1, fill=True, ln=True)

    # Dados
    pdf.set_font("Helvetica", "", 9)
    for m in members:
        name = m.name[:30].encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(60, 8, name, border=1)
        pdf.cell(35, 8, m.whatsapp, border=1)
        pdf.cell(30, 8, m.status.value, border=1)
        endereco = (m.endereco or "---")[:50].encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(90, 8, endereco, border=1)
        batismo = m.data_batismo.strftime("%d/%m/%Y") if m.data_batismo else "---"
        pdf.cell(30, 8, batismo, border=1, ln=True)

    pdf_bytes = pdf.output()
    return Response(
        content=bytes(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=relatorio_membros.pdf"}
    )

@router.get("/positions", response_model=List[PositionSchema])
def list_positions(
    db: Session = Depends(deps.get_db),
    church_id: int = Depends(deps.get_current_church_id)
):
    """Retorna todos os Cargos e Funções cadastrados para a igreja"""
    return db.query(models.Position).filter(models.Position.church_id == church_id).all()

@router.post("/positions", response_model=PositionSchema)
def create_position(
    data: PositionCreate, 
    db: Session = Depends(deps.get_db),
    church_id: int = Depends(deps.get_current_church_id)
):
    """Cria um novo cargo ou função para a igreja"""
    new_pos = models.Position(
        name=data.name,
        type=data.type,
        church_id=church_id
    )
    db.add(new_pos)
    db.commit()
    db.refresh(new_pos)
    return new_pos

@router.delete("/positions/{position_id}")
def delete_position(
    position_id: int,
    db: Session = Depends(deps.get_db),
    church_id: int = Depends(deps.get_current_church_id)
):
    """Remove um cargo ou função"""
    db_pos = db.query(models.Position).filter(
        models.Position.id == position_id, 
        models.Position.church_id == church_id
    ).first()
    if not db_pos: raise HTTPException(status_code=404, detail="Cargo não encontrado")
    
    db.delete(db_pos)
    db.commit()
    return {"message": "Removido com sucesso"}

@router.post("/create-with-positions", response_model=MemberSchema)
def create_member_complex(
    data: MemberCreateWithPositions,
    db: Session = Depends(deps.get_db),
    church_id: int = Depends(deps.get_current_church_id)
):
    """Cria um membro vinculando-o a múltiplos Cargos e Funções"""
    new_member = models.Member(
        name=data.name,
        whatsapp=data.whatsapp,
        status=data.status,
        endereco=data.endereco,
        data_batismo=data.data_batismo,
        church_id=church_id
    )
    
    if data.position_ids:
        positions = db.query(models.Position).filter(
            models.Position.id.in_(data.position_ids),
            models.Position.church_id == church_id
        ).all()
        new_member.positions = positions

    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member

@router.put("/{member_id}", response_model=MemberSchema)
def update_member(
    member_id: int,
    data: MemberUpdateSchema,
    db: Session = Depends(deps.get_db),
    church_id: int = Depends(deps.get_current_church_id)
):
    """Atualiza dados de um membro existente"""
    db_member = db.query(models.Member).filter(
        models.Member.id == member_id, 
        models.Member.church_id == church_id
    ).first()
    if not db_member: raise HTTPException(status_code=404, detail="Membro não encontrado")
    
    if data.name is not None: db_member.name = data.name
    if data.whatsapp is not None: db_member.whatsapp = data.whatsapp
    if data.status is not None: db_member.status = data.status
    if data.endereco is not None: db_member.endereco = data.endereco
    if data.data_batismo is not None: db_member.data_batismo = data.data_batismo
    
    if data.position_ids is not None:
        positions = db.query(models.Position).filter(
            models.Position.id.in_(data.position_ids),
            models.Position.church_id == church_id
        ).all()
        db_member.positions = positions

    db.commit()
    db.refresh(db_member)
    return db_member

@router.delete("/{member_id}")
def delete_member(
    member_id: int,
    db: Session = Depends(deps.get_db),
    church_id: int = Depends(deps.get_current_church_id)
):
    """Remove um membro (soft delete alterando status para EXCLUIDO)"""
    db_member = db.query(models.Member).filter(
        models.Member.id == member_id, 
        models.Member.church_id == church_id
    ).first()
    if not db_member: raise HTTPException(status_code=404, detail="Membro não encontrado")
    
    db_member.status = models.MemberStatus.EXCLUIDO
    db.commit()
    return {"message": "Membro removido com sucesso"}

@router.get("/", response_model=List[MemberSchema])
def list_members(
    db: Session = Depends(deps.get_db),
    church_id: int = Depends(deps.get_current_church_id)
):
    """Lista membros com seus respectivos Cargos e Funções"""
    return db.query(models.Member).options(
        joinedload(models.Member.positions)
    ).filter(
        models.Member.church_id == church_id,
        models.Member.status != models.MemberStatus.EXCLUIDO
    ).all()

@router.patch("/{member_id}/promote")
def promote_visitor(
    member_id: int, 
    data: MemberPromoteSchema,
    db: Session = Depends(deps.get_db),
    church_id: int = Depends(deps.get_current_church_id)
):
    db_member = db.query(models.Member).filter(
        models.Member.id == member_id, 
        models.Member.church_id == church_id
    ).first()
    if not db_member: raise HTTPException(status_code=404, detail="Membro não encontrado")
    
    # 1. Mudar status
    db_member.status = models.MemberStatus.ATIVO
    
    # 2. Vincular Cargos e Funções
    all_pos_ids = [data.cargo_id] + data.funcao_ids
    positions = db.query(models.Position).filter(
        models.Position.id.in_(all_pos_ids),
        models.Position.church_id == church_id
    ).all()
    
    db_member.positions = positions
    
    db.commit()
    return {"message": "Promovido com sucesso!"}
