"""Database models."""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import enum
from app.database import Base


class ClauseStatus(str, enum.Enum):
    """Clause comparison status."""
    OK = "OK"
    MISSING = "MISSING"
    REVIEW = "REVIEW"


class Document(Base):
    """Contract document model."""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    extracted_text = Column(Text)
    risk_score = Column(Float, default=0.0)
    
    # Relationships
    clauses = relationship("ExtractedClause", back_populates="document", cascade="all, delete-orphan")
    analyses = relationship("ClauseAnalysis", back_populates="document", cascade="all, delete-orphan")


class StandardClause(Base):
    """Standard clause library model."""
    __tablename__ = "standard_clauses"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    text = Column(Text, nullable=False)
    embedding = Column(Vector(384))  # all-MiniLM-L6-v2 produces 384-dim vectors
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    analyses = relationship("ClauseAnalysis", back_populates="standard_clause")


class ExtractedClause(Base):
    """Extracted clause from contract."""
    __tablename__ = "extracted_clauses"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    clause_number = Column(String(255))
    text = Column(Text, nullable=False)
    embedding = Column(Vector(384))
    start_position = Column(Integer)
    end_position = Column(Integer)
    
    # Relationships
    document = relationship("Document", back_populates="clauses")


class ClauseAnalysis(Base):
    """Analysis result comparing standard clause to extracted clause."""
    __tablename__ = "clause_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    standard_clause_id = Column(Integer, ForeignKey("standard_clauses.id"), nullable=False)
    extracted_clause_id = Column(Integer, ForeignKey("extracted_clauses.id", ondelete="CASCADE"), nullable=True)
    similarity_score = Column(Float, default=0.0)
    status = Column(SQLEnum(ClauseStatus), nullable=False)
    notes = Column(Text)
    
    # Relationships
    document = relationship("Document", back_populates="analyses")
    standard_clause = relationship("StandardClause", back_populates="analyses")
    extracted_clause = relationship("ExtractedClause")
