"""Tests for embedding utilities."""
import pytest
from app.utils.embeddings import (
    generate_embedding,
    generate_embeddings_batch,
    cosine_similarity,
    find_best_match
)


def test_generate_embedding():
    """Test single embedding generation."""
    text = "This is a test contract clause."
    embedding = generate_embedding(text)
    
    # Should return a list of floats
    assert isinstance(embedding, list)
    assert len(embedding) == 384  # all-MiniLM-L6-v2 dimension
    assert all(isinstance(x, float) for x in embedding)


def test_generate_embeddings_batch():
    """Test batch embedding generation."""
    texts = [
        "First clause text",
        "Second clause text",
        "Third clause text"
    ]
    embeddings = generate_embeddings_batch(texts)
    
    assert len(embeddings) == 3
    assert all(len(emb) == 384 for emb in embeddings)


def test_cosine_similarity():
    """Test cosine similarity calculation."""
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]
    
    similarity = cosine_similarity(vec1, vec2)
    
    # Identical vectors should have similarity of 1.0
    assert abs(similarity - 1.0) < 0.001
    
    # Orthogonal vectors
    vec3 = [0.0, 1.0, 0.0]
    similarity2 = cosine_similarity(vec1, vec3)
    assert abs(similarity2) < 0.001  # Should be close to 0


def test_cosine_similarity_similar_texts():
    """Test similarity between similar texts."""
    text1 = "The party agrees to maintain confidentiality."
    text2 = "The party shall keep information confidential."
    text3 = "Payment is due within 30 days."
    
    emb1 = generate_embedding(text1)
    emb2 = generate_embedding(text2)
    emb3 = generate_embedding(text3)
    
    sim_similar = cosine_similarity(emb1, emb2)
    sim_different = cosine_similarity(emb1, emb3)
    
    # Similar texts should have higher similarity than different texts
    assert sim_similar > sim_different
    assert sim_similar > 0.5  # Should be reasonably similar


def test_find_best_match():
    """Test finding best matching clause."""
    query_text = "Confidentiality agreement"
    
    candidates = [
        "Payment terms and conditions",
        "Confidential information protection",
        "Termination clause details"
    ]
    
    query_emb = generate_embedding(query_text)
    candidate_embs = generate_embeddings_batch(candidates)
    
    best_idx, best_score = find_best_match(query_emb, candidate_embs)
    
    # Should match the confidentiality-related clause (index 1)
    assert best_idx == 1
    assert 0 <= best_score <= 1


def test_find_best_match_empty():
    """Test finding best match with empty candidates."""
    query_emb = generate_embedding("test")
    
    best_idx, best_score = find_best_match(query_emb, [])
    
    assert best_idx == -1
    assert best_score == 0.0
