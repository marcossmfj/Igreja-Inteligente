from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from ..models import models

class PositionCreate(BaseModel):
    name: str
    type: str

class PositionSchema(PositionCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class MemberSchema(BaseModel):
    id: int
    name: str
    whatsapp: Optional[str] = None
    status: Optional[str] = None
    endereco: Optional[str] = None
    data_batismo: Optional[datetime] = None
    consecutive_refusals: int = 0
    positions: List[PositionSchema]

    model_config = ConfigDict(from_attributes=True)

class MemberCreateWithPositions(BaseModel):
    name: str
    whatsapp: str
    status: models.MemberStatus
    endereco: Optional[str] = None
    data_batismo: Optional[datetime] = None
    position_ids: List[int]

class MemberUpdateSchema(BaseModel):
    name: Optional[str] = None
    whatsapp: Optional[str] = None
    status: Optional[models.MemberStatus] = None
    endereco: Optional[str] = None
    data_batismo: Optional[datetime] = None
    position_ids: Optional[List[int]] = None

class MemberPromoteSchema(BaseModel):
    cargo_id: int
    funcao_ids: List[int]
