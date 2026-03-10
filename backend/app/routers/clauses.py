"""API routes for standard clauses."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import StandardClauseResponse, StandardClauseCreate, StandardClauseUpdate
from app.models import StandardClause
from app.utils.embeddings import generate_embedding

router = APIRouter(prefix="/clauses", tags=["standard-clauses"])


@router.post("/", response_model=StandardClauseResponse, status_code=201)
def create_standard_clause(
    clause: StandardClauseCreate,
    db: Session = Depends(get_db)
):
    """Create a new standard clause with embedding."""
    # Generate embedding
    embedding = generate_embedding(clause.text)
    
    # Create clause
    db_clause = StandardClause(
        category=clause.category,
        title=clause.title,
        text=clause.text,
        embedding=embedding
    )
    
    db.add(db_clause)
    db.commit()
    db.refresh(db_clause)
    
    return db_clause


@router.get("/", response_model=List[StandardClauseResponse])
def list_standard_clauses(
    category: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of standard clauses, optionally filtered by category."""
    query = db.query(StandardClause)
    
    if category:
        query = query.filter(StandardClause.category == category)
    
    clauses = query.order_by(StandardClause.category, StandardClause.title).offset(skip).limit(limit).all()
    return clauses


@router.get("/{clause_id}", response_model=StandardClauseResponse)
def get_standard_clause(
    clause_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific standard clause by ID."""
    clause = db.query(StandardClause).filter(StandardClause.id == clause_id).first()
    
    if not clause:
        raise HTTPException(status_code=404, detail="Standard clause not found")
    
    return clause


@router.put("/{clause_id}", response_model=StandardClauseResponse)
def update_standard_clause(
    clause_id: int,
    clause_update: StandardClauseUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing standard clause."""
    db_clause = db.query(StandardClause).filter(StandardClause.id == clause_id).first()
    
    if not db_clause:
        raise HTTPException(status_code=404, detail="Standard clause not found")
    
    # Update fields
    update_data = clause_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_clause, field, value)
    
    # Regenerate embedding if text changed
    if "text" in update_data:
        db_clause.embedding = generate_embedding(db_clause.text)
    
    db.commit()
    db.refresh(db_clause)
    
    return db_clause


@router.delete("/{clause_id}")
def delete_standard_clause(
    clause_id: int,
    db: Session = Depends(get_db)
):
    """Delete a standard clause."""
    db_clause = db.query(StandardClause).filter(StandardClause.id == clause_id).first()
    
    if not db_clause:
        raise HTTPException(status_code=404, detail="Standard clause not found")
    
    db.delete(db_clause)
    db.commit()
    
    return {"message": "Standard clause deleted successfully"}


@router.get("/categories/list", response_model=List[str])
def list_categories(db: Session = Depends(get_db)):
    """Get list of all unique categories."""
    categories = db.query(StandardClause.category).distinct().all()
    return [cat[0] for cat in categories]
