"""Test configuration and fixtures."""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture
def sample_contract_text():
    """Sample contract text for testing."""
    return """
    CONTRACT AGREEMENT
    
    1. CONFIDENTIALITY
    The receiving party agrees to maintain in strict confidence all Confidential 
    Information disclosed by the disclosing party.
    
    2. TERM AND TERMINATION
    This Agreement shall commence on the Effective Date and continue for one year.
    
    3. PAYMENT TERMS
    Client agrees to pay all fees within thirty days of invoice receipt.
    """


@pytest.fixture
def sample_standard_clauses():
    """Sample standard clauses for testing."""
    return [
        {
            "category": "Confidentiality",
            "title": "Non-Disclosure",
            "text": "The party shall maintain confidential information in strict confidence."
        },
        {
            "category": "Payment",
            "title": "Payment Terms",
            "text": "Payment shall be made within 30 days of invoice."
        },
        {
            "category": "Liability",
            "title": "Limitation of Liability",
            "text": "Neither party shall be liable for indirect or consequential damages."
        }
    ]
