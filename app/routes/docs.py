from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from ..models import models, database
from ..core import deps
import os
import shutil
import uuid

router = APIRouter(prefix="/docs", tags=["Documentos"])

# Pasta para armazenar documentos reais
DOCS_DIR = "assets/documents"
if not os.path.exists(DOCS_DIR):
    os.makedirs(DOCS_DIR)

@router.get("/")
def list_documents(
    db: Session = Depends(database.get_db),
    church_id: int = Depends(deps.get_current_church_id)
):
    """Lista todos os documentos da igreja"""
    return db.query(models.Document).filter(models.Document.church_id == church_id).all()

@router.post("/")
async def upload_document(
    title: str = Form(...),
    member_id: int = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    church_id: int = Depends(deps.get_current_church_id)
):
    """Realiza o upload real de um documento e salva o caminho no banco de dados"""
    
    # Gerar nome único para o arquivo para evitar colisões
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(DOCS_DIR, unique_filename)
    
    # Salvar o arquivo no disco
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo: {e}")
    
    # Criar registro no banco de dados
    new_doc = models.Document(
        title=title,
        file_type=file.content_type,
        file_path=f"assets/documents/{unique_filename}", # Caminho relativo para servir via estáticos
        member_id=member_id,
        church_id=church_id
    )
    
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    
    return new_doc

@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    db: Session = Depends(database.get_db),
    church_id: int = Depends(deps.get_current_church_id)
):
    """Remove um documento e apaga o arquivo físico"""
    doc = db.query(models.Document).filter(
        models.Document.id == doc_id, 
        models.Document.church_id == church_id
    ).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    
    # Remover arquivo físico
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)
        
    db.delete(doc)
    db.commit()
    return {"message": "Documento removido com sucesso"}
