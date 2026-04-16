from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, Boolean, Table, Index
from sqlalchemy.orm import relationship
from .database import Base
import enum
import datetime

# ... (rest of imports and enums)

class MemberStatus(str, enum.Enum):
    ATIVO = "Ativo"
    EXCLUIDO = "Excluído"
    VISITANTE = "Visitante"
    TRANSFERIDO = "Transferido"
    AFASTADO = "Afastado"

class PositionType(str, enum.Enum):
    CARGO = "Cargo" # Obreiro, Diácono, Pastor
    FUNCAO = "Função" # Guitarrista, Sonoplasta, Professor

member_positions = Table(
    "member_positions",
    Base.metadata,
    Column("member_id", ForeignKey("members.id"), primary_key=True),
    Column("position_id", ForeignKey("positions.id"), primary_key=True)
)

from ..core.config import settings

class Church(Base):
    __tablename__ = "churches"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    slug = Column(String, unique=True, index=True)
    logo_path = Column(String, nullable=True)
    schedule_template_path = Column(String, nullable=True)
    evolution_api_url = Column(String, default=settings.EVOLUTION_API_URL)
    evolution_api_key = Column(String, default=settings.EVOLUTION_API_KEY)
    evolution_instance_name = Column(String, nullable=True)
    subscription_status = Column(String, default="active")
    subscription_expires_at = Column(DateTime, nullable=True)
    
    # Relacionamentos com cascade delete
    members = relationship("Member", back_populates="church", cascade="all, delete-orphan")
    users = relationship("User", back_populates="church", cascade="all, delete-orphan")
    positions = relationship("Position", back_populates="church", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="church", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="church", cascade="all, delete-orphan")
    absences = relationship("MemberAbsence", back_populates="church", cascade="all, delete-orphan")
    templates = relationship("ServiceTemplate", back_populates="church", cascade="all, delete-orphan")
    notification_logs = relationship("NotificationLog", back_populates="church", cascade="all, delete-orphan")

class MultiTenantMixin:
    church_id = Column(Integer, ForeignKey("churches.id", ondelete="CASCADE"), nullable=False, index=True)

class Position(Base, MultiTenantMixin):
    __tablename__ = "positions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(Enum(PositionType), default=PositionType.FUNCAO)
    church = relationship("Church", back_populates="positions")

class User(Base, MultiTenantMixin):
    __tablename__ = "users"
    __table_args__ = (Index('idx_user_church_email', 'church_id', 'email'),)
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    whatsapp = Column(String, nullable=True) # Added for alerts
    is_admin = Column(Boolean, default=False)
    is_master = Column(Boolean, default=False)
    church_id = Column(Integer, ForeignKey("churches.id", ondelete="CASCADE"), nullable=True, index=True)
    church = relationship("Church", back_populates="users")

class Member(Base, MultiTenantMixin):
    __tablename__ = "members"
    __table_args__ = (Index('idx_member_church_status', 'church_id', 'status'),)
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    whatsapp = Column(String, nullable=False)
    birth_date = Column(DateTime, nullable=True)
    status = Column(Enum(MemberStatus), default=MemberStatus.VISITANTE)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Campos Profissionais
    endereco = Column(String, nullable=True)
    data_batismo = Column(DateTime, nullable=True)
    consecutive_refusals = Column(Integer, default=0)

    positions = relationship("Position", secondary=member_positions)
    church = relationship("Church", back_populates="members")

class MemberAbsence(Base, MultiTenantMixin):
    __tablename__ = "member_absences"
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    reason = Column(String, nullable=True)
    
    member = relationship("Member")
    church = relationship("Church", back_populates="absences")

class Document(Base, MultiTenantMixin):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    file_type = Column(String, nullable=True)
    file_path = Column(String, nullable=False)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    member = relationship("Member")
    church = relationship("Church", back_populates="documents")

class ServiceTemplate(Base, MultiTenantMixin):
    __tablename__ = "service_templates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    church = relationship("Church", back_populates="templates")
    positions = relationship("TemplatePosition", back_populates="template", cascade="all, delete-orphan")

class TemplatePosition(Base):
    __tablename__ = "template_positions"
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("service_templates.id", ondelete="CASCADE"), nullable=False)
    position_id = Column(Integer, ForeignKey("positions.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, default=1)
    template = relationship("ServiceTemplate", back_populates="positions")
    position = relationship("Position")

class NotificationLog(Base, MultiTenantMixin):
    __tablename__ = "notification_logs"
    id = Column(Integer, primary_key=True, index=True)
    target_phone = Column(String, nullable=False)
    message_type = Column(String, nullable=False) # 'invite', 'reminder', 'welcome', 'birthday'
    reference_id = Column(Integer, nullable=True) # ID da escala ou membro
    sent_at = Column(DateTime, default=datetime.datetime.utcnow)
    church = relationship("Church", back_populates="notification_logs")

class Schedule(Base, MultiTenantMixin):
    __tablename__ = "schedules"
    __table_args__ = (Index('idx_schedule_church_date', 'church_id', 'event_date'),)
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    position_id = Column(Integer, ForeignKey("positions.id", ondelete="SET NULL"), nullable=True)
    template_id = Column(Integer, ForeignKey("service_templates.id", ondelete="SET NULL"), nullable=True)
    event_name = Column(String, nullable=False)
    event_date = Column(DateTime, nullable=False)
    confirmed = Column(Boolean, default=False)
    rejected = Column(Boolean, default=False)
    notified = Column(Boolean, default=False)
    card_path = Column(String, nullable=True)
    member = relationship("Member")
    position = relationship("Position")
    template = relationship("ServiceTemplate")
    church = relationship("Church", back_populates="schedules")
