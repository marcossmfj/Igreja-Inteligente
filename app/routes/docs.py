from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import models, database
from ..core import deps
from ..schemas.document import DocumentCreate

router = APIRouter(prefix="/docs", tags=["Documentos"])

@router.get("/")
def list_documents(
    db: Session = Depends(deps.get_db),
    church_id: int = Depends(deps.get_current_church_id)
):
    return db.query(models.Document).filter(models.Document.church_id == church_id).all()

@router.post("/")
def create_document(
    doc: DocumentCreate,
    db: Session = Depends(deps.get_db),
    church_id: int = Depends(deps.get_current_church_id)
):
    new_doc = models.Document(
        **doc.dict(),
        file_path="storage/fake_path.pdf", # Simulação de upload
        church_id=church_id
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc
