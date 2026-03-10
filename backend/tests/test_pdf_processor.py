"""Tests for PDF processing utilities."""
import pytest
from app.utils.pdf_processor import chunk_into_clauses


def test_chunk_into_clauses_with_numbered_sections():
    """Test chunking with numbered sections."""
    text = """1. DEFINITIONS
This agreement defines the following terms.

2. CONFIDENTIALITY
All information shall remain confidential.

3. TERM
This agreement is valid for one year."""
    
    clauses = chunk_into_clauses(text)
    
    assert len(clauses) > 0
    # Check that we have clause numbers
    clause_numbers = [clause[0] for clause in clauses]
    assert any('1.' in num or 'DEFINITIONS' in num for num in clause_numbers)


def test_chunk_into_clauses_with_short_text():
    """Test chunking with short text."""
    text = "This is a very short contract."
    
    clauses = chunk_into_clauses(text)
    
    # Should create at least one clause
    assert len(clauses) >= 1
    assert clauses[0][1] == text


def test_chunk_into_clauses_empty():
    """Test chunking with empty text."""
    text = ""
    
    clauses = chunk_into_clauses(text)
    
    # Should handle empty text gracefully
    assert len(clauses) >= 0


def test_chunk_into_clauses_positions():
    """Test that start and end positions are valid."""
    text = """Section 1
First section content here.

Section 2
Second section content here."""
    
    clauses = chunk_into_clauses(text)
    
    for clause_num, clause_text, start, end in clauses:
        # Positions should be valid
        assert start >= 0
        assert end > start
        assert end <= len(text)
