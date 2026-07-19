from sqlalchemy import Column, Integer, String, Enum as SQLAlchemyEnum, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
import enum
from database import Base

class RoleEnum(str, enum.Enum):
    Admin = "Admin"
    Investigator = "Investigator"
    Analyst = "Analyst"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLAlchemyEnum(RoleEnum), nullable=False, default=RoleEnum.Investigator)

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    suspect_name = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, default="Open")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class NetworkForensic(Base):
    __tablename__ = "network_forensics"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    parsed_data = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class IPReputationCache(Base):
    __tablename__ = "ip_reputation_cache"

    ip_address = Column(String(45), primary_key=True, index=True) # IPv6 can be up to 45 chars
    abuse_confidence_score = Column(Integer, nullable=False, default=0)
    is_malicious = Column(Boolean, nullable=False, default=False)
    last_checked = Column(DateTime(timezone=True), server_default=func.now())

from sqlalchemy import Text

class LegalKnowledge(Base):
    __tablename__ = "legal_knowledge"

    id = Column(Integer, primary_key=True, index=True)
    document_name = Column(String(200), nullable=False)
    section_title = Column(String(200), index=True, nullable=False)
    raw_text = Column(Text, nullable=False)
    keywords = Column(Text, nullable=True)
