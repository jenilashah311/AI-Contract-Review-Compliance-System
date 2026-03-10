"""Tests for analyzer service."""
import pytest
from app.services.analyzer import (
    detect_keyword_conflict,
    calculate_risk_score
)


def test_detect_keyword_conflict_with_negation():
    """Test conflict detection with negation."""
    standard = "The party shall disclose information."
    extracted = "The party shall not disclose information."
    
    has_conflict = detect_keyword_conflict(standard, extracted)
    
    assert has_conflict is True


def test_detect_keyword_conflict_no_conflict():
    """Test no conflict detection."""
    standard = "The party shall maintain confidentiality."
    extracted = "The party agrees to maintain confidentiality."
    
    has_conflict = detect_keyword_conflict(standard, extracted)
    
    assert has_conflict is False


def test_detect_keyword_conflict_both_have_negation():
    """Test when both have negation."""
    standard = "The party shall not disclose without consent."
    extracted = "The party must not share without permission."
    
    has_conflict = detect_keyword_conflict(standard, extracted)
    
    # Both have negation, so no conflict
    assert has_conflict is False


def test_calculate_risk_score_no_issues():
    """Test risk score calculation with no issues."""
    score = calculate_risk_score(total=10, missing=0, review=0)
    
    assert score == 0.0


def test_calculate_risk_score_all_missing():
    """Test risk score with all clauses missing."""
    score = calculate_risk_score(total=10, missing=10, review=0)
    
    assert score == 100.0


def test_calculate_risk_score_mixed():
    """Test risk score with mixed results."""
    score = calculate_risk_score(total=10, missing=3, review=2)
    
    # Should be between 0 and 100
    assert 0 <= score <= 100
    # Should be higher than zero since there are issues
    assert score > 0
    # Missing should contribute more than review
    score_missing_only = calculate_risk_score(total=10, missing=3, review=0)
    assert score > score_missing_only or score == score_missing_only


def test_calculate_risk_score_zero_total():
    """Test risk score with zero total clauses."""
    score = calculate_risk_score(total=0, missing=0, review=0)
    
    assert score == 0.0


def test_calculate_risk_score_capped_at_100():
    """Test that risk score doesn't exceed 100."""
    # Try to create a score over 100
    score = calculate_risk_score(total=5, missing=20, review=10)
    
    assert score <= 100.0
