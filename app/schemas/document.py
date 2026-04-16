from pydantic import BaseModel
from typing import Optional

class DocumentCreate(BaseModel):
    title: str
    file_type: str
    member_id: Optional[int] = None
