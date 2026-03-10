"""Pydantic schemas for request/response models."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ClauseStatusEnum(str, Enum):
    """Clause comparison status."""
    OK = "OK"
    MISSING = "MISSING"
    REVIEW = "REVIEW"


# Standard Clause Schemas
class StandardClauseBase(BaseModel):
    category: str
    title: str
    text: str


class StandardClauseCreate(StandardClauseBase):
    pass


class StandardClauseUpdate(BaseModel):
    category: Optional[str] = None
    title: Optional[str] = None
    text: Optional[str] = None


class StandardClauseResponse(StandardClauseBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Document Schemas
class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    uploaded_at: datetime
    risk_score: float
    
    class Config:
        from_attributes = True


class ExtractedClauseResponse(BaseModel):
    id: int
    clause_number: Optional[str]
    text: str
    start_position: Optional[int]
    end_position: Optional[int]
    
    class Config:
        from_attributes = True


class ClauseAnalysisResponse(BaseModel):
    id: int
    standard_clause: StandardClauseResponse
    extracted_clause: Optional[ExtractedClauseResponse]
    similarity_score: float
    status: ClauseStatusEnum
    notes: Optional[str]
    
    class Config:
        from_attributes = True


class DocumentDetailResponse(DocumentResponse):
    extracted_text: Optional[str]
    clauses: List[ExtractedClauseResponse]
    analyses: List[ClauseAnalysisResponse]
    
    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    document: DocumentResponse
    message: str
    analysis_summary: dict


class AnalysisSummary(BaseModel):
    total_standard_clauses: int
    matched_clauses: int
    missing_clauses: int
    review_clauses: int
    risk_score: float
