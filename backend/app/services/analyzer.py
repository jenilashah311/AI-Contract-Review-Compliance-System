"""Clause analysis and risk scoring logic."""
from typing import List, Tuple
from sqlalchemy.orm import Session
from app.models import StandardClause, ExtractedClause, ClauseAnalysis, Document, ClauseStatus
from app.utils.embeddings import cosine_similarity, find_best_match
from app.config import get_settings

settings = get_settings()


def _is_missing_embedding(embedding) -> bool:
    """Return True when embedding is None or empty."""
    if embedding is None:
        return True
    try:
        return len(embedding) == 0
    except TypeError:
        return False


def detect_keyword_conflict(standard_text: str, extracted_text: str) -> bool:
    """
    Simple heuristic to detect potential conflicts.
    
    Checks for negation words or contradictory terms.
    
    Args:
        standard_text: Standard clause text
        extracted_text: Extracted clause text
        
    Returns:
        True if potential conflict detected
    """
    conflict_indicators = [
        "not", "no", "never", "except", "excluding", "without",
        "prohibited", "forbidden", "restrict"
    ]
    
    standard_lower = standard_text.lower()
    extracted_lower = extracted_text.lower()
    
    # Simple heuristic: if one has negation and other doesn't
    standard_has_negation = any(word in standard_lower for word in conflict_indicators)
    extracted_has_negation = any(word in extracted_lower for word in conflict_indicators)
    
    return standard_has_negation != extracted_has_negation


def analyze_document_clauses(
    db: Session,
    document_id: int
) -> dict:
    """
    Analyze document clauses against standard clause library.
    
    For each standard clause:
    1. Find best matching extracted clause
    2. Compute similarity score
    3. Determine status (OK/MISSING/REVIEW)
    4. Detect potential conflicts
    
    Args:
        db: Database session
        document_id: Document ID to analyze
        
    Returns:
        Analysis summary dict
    """
    # Get document and its extracted clauses
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise ValueError(f"Document {document_id} not found")
    
    extracted_clauses = db.query(ExtractedClause).filter(
        ExtractedClause.document_id == document_id
    ).all()
    
    # Get all standard clauses
    standard_clauses = db.query(StandardClause).all()
    
    if not standard_clauses:
        return {
            "total_standard_clauses": 0,
            "matched": 0,
            "missing": 0,
            "review": 0,
            "risk_score": 0
        }
    
    # Prepare embeddings
    extracted_embeddings = [clause.embedding for clause in extracted_clauses]
    
    analyses = []
    missing_count = 0
    review_count = 0
    matched_count = 0
    
    for standard_clause in standard_clauses:
        if _is_missing_embedding(standard_clause.embedding):
            continue
        
        # Find best matching extracted clause with keyword enhancement
        extracted_texts = [clause.text for clause in extracted_clauses]
        best_idx, similarity = find_best_match(
            standard_clause.embedding,
            extracted_embeddings,
            query_text=standard_clause.text,
            candidate_texts=extracted_texts,
            keyword_bonus=getattr(settings, 'keyword_match_bonus', 0.05)
        )
        
        # Determine status
        if similarity < settings.similarity_threshold:
            status = ClauseStatus.MISSING
            missing_count += 1
            best_clause = None
            notes = f"No matching clause found (best similarity: {similarity:.2f})"
        else:
            best_clause = extracted_clauses[best_idx]
            
            # Check for conflicts
            has_conflict = detect_keyword_conflict(
                standard_clause.text,
                best_clause.text
            )
            
            if has_conflict and similarity < 0.90:
                status = ClauseStatus.REVIEW
                review_count += 1
                notes = "Potential conflict detected - review required"
            else:
                status = ClauseStatus.OK
                matched_count += 1
                notes = f"Match found (similarity: {similarity:.2f})"
        
        # Create analysis record
        analysis = ClauseAnalysis(
            document_id=document_id,
            standard_clause_id=standard_clause.id,
            extracted_clause_id=best_clause.id if best_clause else None,
            similarity_score=similarity,
            status=status,
            notes=notes
        )
        analyses.append(analysis)
    
    # Bulk insert analyses
    db.bulk_save_objects(analyses)
    db.commit()
    
    # Calculate risk score
    risk_score = calculate_risk_score(
        total=len(standard_clauses),
        missing=missing_count,
        review=review_count
    )
    
    # Update document risk score
    document.risk_score = risk_score
    db.commit()
    
    return {
        "total_standard_clauses": len(standard_clauses),
        "matched": matched_count,
        "missing": missing_count,
        "review": review_count,
        "risk_score": risk_score
    }


def calculate_risk_score(total: int, missing: int, review: int) -> float:
    """
    Calculate normalized risk score (0-100).
    
    Higher score = higher risk
    Missing clauses are high risk (10 points each)
    Review clauses are low risk (1 point each) - they exist but need verification
    
    Args:
        total: Total number of standard clauses
        missing: Number of missing clauses
        review: Number of clauses needing review
        
    Returns:
        Risk score (0-100)
    """
    if total == 0:
        return 0.0
    
    # Weighted score - review items are low risk since they were found
    raw_score = (
        missing * settings.missing_weight +
        review * 1  # Low weight for review items (they exist, just need verification)
    )
    
    # Normalize to 0-100 scale
    max_possible = total * settings.missing_weight
    if max_possible == 0:
        return 0.0
    
    score = (raw_score / max_possible) * 100
    return min(100.0, round(score, 2))
