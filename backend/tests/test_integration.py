"""Integration tests for document upload and analysis."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.main import app
from app.database import Base, get_db
from app.models import StandardClause
from app.utils.embeddings import generate_embedding

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="function")
def test_db():
    """Create test database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def seed_standard_clauses(test_db):
    """Seed database with standard clauses."""
    db = TestingSessionLocal()
    
    clause = StandardClause(
        category="Confidentiality",
        title="Non-Disclosure",
        text="The party shall maintain confidential information.",
        embedding=generate_embedding("The party shall maintain confidential information.")
    )
    
    db.add(clause)
    db.commit()
    db.close()


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_list_documents_empty(test_db):
    """Test listing documents when none exist."""
    response = client.get("/documents/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_standard_clause(test_db):
    """Test creating a standard clause."""
    clause_data = {
        "category": "Payment",
        "title": "Payment Terms",
        "text": "Payment is due within 30 days."
    }
    
    response = client.post("/clauses/", json=clause_data)
    assert response.status_code == 201
    data = response.json()
    assert data["category"] == clause_data["category"]
    assert data["title"] == clause_data["title"]
    assert "id" in data


def test_list_standard_clauses(test_db, seed_standard_clauses):
    """Test listing standard clauses."""
    response = client.get("/clauses/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["category"] == "Confidentiality"


def test_get_standard_clause_not_found(test_db):
    """Test getting non-existent clause."""
    response = client.get("/clauses/9999")
    assert response.status_code == 404


def test_delete_standard_clause(test_db, seed_standard_clauses):
    """Test deleting a standard clause."""
    # First get the clause
    response = client.get("/clauses/")
    clause_id = response.json()[0]["id"]
    
    # Delete it
    response = client.delete(f"/clauses/{clause_id}")
    assert response.status_code == 200
    
    # Verify it's gone
    response = client.get(f"/clauses/{clause_id}")
    assert response.status_code == 404
