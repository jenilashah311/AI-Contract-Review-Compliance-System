"""Embedding generation and similarity computation."""
from sentence_transformers import SentenceTransformer
from typing import List, Optional, Tuple
import numpy as np
from functools import lru_cache
import re
from app.config import get_settings

settings = get_settings()


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Get cached embedding model.
    
    Returns:
        SentenceTransformer model
    """
    return SentenceTransformer(settings.embedding_model)


def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding vector for text.
    
    Args:
        text: Input text
        
    Returns:
        Embedding vector as list of floats
    """
    model = get_embedding_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts in batch.
    
    Args:
        texts: List of input texts
        
    Returns:
        List of embedding vectors
    """
    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return embeddings.tolist()


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Compute cosine similarity between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Similarity score (0-1)
    """
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    
    dot_product = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))


def extract_keywords(text: str) -> set:
    """Extract key terms from text for keyword matching."""
    # Remove common words and extract meaningful terms
    text = text.lower()
    # Extract words 4+ chars, excluding common words
    common_words = {'that', 'this', 'with', 'from', 'have', 'will', 'your', 'their', 
                    'which', 'about', 'would', 'there', 'these', 'other', 'such'}
    words = re.findall(r'\b[a-z]{4,}\b', text)
    return {w for w in words if w not in common_words}


def keyword_similarity(text1: str, text2: str) -> float:
    """Calculate keyword overlap similarity between two texts."""
    keywords1 = extract_keywords(text1)
    keywords2 = extract_keywords(text2)
    
    if not keywords1 or not keywords2:
        return 0.0
    
    intersection = len(keywords1 & keywords2)
    union = len(keywords1 | keywords2)
    
    return intersection / union if union > 0 else 0.0


def find_best_match(
    query_embedding: List[float],
    candidate_embeddings: List[List[float]],
    query_text: Optional[str] = None,
    candidate_texts: Optional[List[str]] = None,
    keyword_bonus: float = 0.05
) -> tuple[int, float]:
    """
    Find best matching candidate for query.
    
    Args:
        query_embedding: Query vector
        candidate_embeddings: List of candidate vectors
        query_text: Optional query text for keyword matching
        candidate_texts: Optional candidate texts for keyword matching
        keyword_bonus: Bonus score for keyword matches (0-0.1)
        
    Returns:
        Tuple of (best_index, similarity_score)
    """
    if candidate_embeddings is None:
        return -1, 0.0

    if isinstance(candidate_embeddings, np.ndarray):
        if candidate_embeddings.size == 0:
            return -1, 0.0
    elif len(candidate_embeddings) == 0:
        return -1, 0.0
    
    best_idx = -1
    best_score = 0.0
    
    for idx, cand in enumerate(candidate_embeddings):
        # Calculate semantic similarity
        score = cosine_similarity(query_embedding, cand)
        
        # Add keyword matching bonus if texts provided
        if query_text and candidate_texts and idx < len(candidate_texts):
            kw_sim = keyword_similarity(query_text, candidate_texts[idx])
            score += kw_sim * keyword_bonus
        
        if score > best_score:
            best_score = score
            best_idx = idx
    
    return best_idx, best_score
