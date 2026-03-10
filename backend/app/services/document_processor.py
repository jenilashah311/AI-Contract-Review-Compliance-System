"""Document processing service."""
import os
import shutil
from pathlib import Path
from typing import List
from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.models import Document, ExtractedClause
from app.utils.pdf_processor import extract_text_from_pdf, chunk_into_clauses
from app.utils.embeddings import generate_embeddings_batch
from app.config import get_settings

settings = get_settings()


async def save_uploaded_file(file: UploadFile) -> str:
    """
    Save uploaded file to disk.
    
    Args:
        file: Uploaded file
        
    Returns:
        Path to saved file
    """
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    filename = f"{file.filename}"
    file_path = upload_dir / filename
    
    # Handle duplicate filenames
    counter = 1
    while file_path.exists():
        name_parts = file.filename.rsplit('.', 1)
        if len(name_parts) == 2:
            filename = f"{name_parts[0]}_{counter}.{name_parts[1]}"
        else:
            filename = f"{file.filename}_{counter}"
        file_path = upload_dir / filename
        counter += 1
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return str(file_path)


def process_document(db: Session, file_path: str, original_filename: str) -> Document:
    """
    Process uploaded document:
    1. Extract text from PDF
    2. Chunk into clauses
    3. Generate embeddings
    4. Save to database
    
    Args:
        db: Database session
        file_path: Path to saved file
        original_filename: Original filename
        
    Returns:
        Created Document instance
    """
    # Extract text
    extracted_text = extract_text_from_pdf(file_path)
    
    # Create document record
    document = Document(
        filename=os.path.basename(file_path),
        original_filename=original_filename,
        file_path=file_path,
        extracted_text=extracted_text
    )
    db.add(document)
    db.flush()  # Get document ID
    
    # Chunk into clauses
    clause_data = chunk_into_clauses(extracted_text)
    
    if not clause_data:
        db.commit()
        return document
    
    # Generate embeddings in batch
    clause_texts = [text for _, text, _, _ in clause_data]
    embeddings = generate_embeddings_batch(clause_texts)
    
    # Create extracted clause records
    extracted_clauses = []
    for (clause_num, text, start, end), embedding in zip(clause_data, embeddings):
        clause = ExtractedClause(
            document_id=document.id,
            clause_number=clause_num,
            text=text,
            embedding=embedding,
            start_position=start,
            end_position=end
        )
        extracted_clauses.append(clause)
    
    db.bulk_save_objects(extracted_clauses)
    db.commit()
    db.refresh(document)
    
    return document
