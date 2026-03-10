"""API routes for documents."""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import DocumentResponse, DocumentDetailResponse, UploadResponse
from app.models import Document, ExtractedClause, ClauseAnalysis
from app.services.document_processor import save_uploaded_file, process_document
from app.services.analyzer import analyze_document_clauses

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process a contract PDF.
    
    Steps:
    1. Save PDF to disk
    2. Extract text and chunk into clauses
    3. Generate embeddings
    4. Analyze against standard clauses
    5. Calculate risk score
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Save file
        file_path = await save_uploaded_file(file)
        
        # Process document
        document = process_document(db, file_path, file.filename)
        
        # Analyze clauses
        analysis_summary = analyze_document_clauses(db, document.id)
        
        return {
            "document": document,
            "message": "Document uploaded and analyzed successfully",
            "analysis_summary": analysis_summary
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@router.get("/", response_model=List[DocumentResponse])
def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of all uploaded documents."""
    documents = db.query(Document).order_by(Document.uploaded_at.desc()).offset(skip).limit(limit).all()
    return documents


@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed document information including analysis results."""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Eagerly load relationships
    clauses = db.query(ExtractedClause).filter(ExtractedClause.document_id == document_id).all()
    analyses = db.query(ClauseAnalysis).filter(ClauseAnalysis.document_id == document_id).all()
    
    return document


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Delete a document and its analyses."""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file from disk
    import os
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}
