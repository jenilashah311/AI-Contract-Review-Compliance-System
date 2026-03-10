# Contract Compliance Checker

An end-to-end web application for analyzing contract compliance against a standard clause library using AI-powered text analysis and vector embeddings.

## Features

- **PDF Contract Upload**: Upload contract PDFs for automated analysis
- **Intelligent Clause Extraction**: Automatic clause identification using rule-based parsing
- **Semantic Similarity Matching**: Compare contract clauses against standard library using embeddings
- **Compliance Analysis**: Identify missing clauses, conflicting terms, and compliance issues
- **Risk Scoring**: Automated risk assessment (0-100 scale) based on compliance gaps
- **Interactive Dashboard**: Modern UI for viewing analysis results with side-by-side comparisons
- **Standard Clause Management**: CRUD interface for managing your clause library

## Architecture

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with pgvector extension
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **PDF Processing**: PyMuPDF
- **ORM**: SQLAlchemy with Alembic migrations

### Frontend
- **Framework**: Next.js 14 (React, TypeScript)
- **Styling**: CSS Modules
- **API Client**: Axios

### Key Components

```
 backend/
    app/
       main.py              # FastAPI application
       models.py            # Database models
       schemas.py           # Pydantic schemas
       routers/             # API endpoints
       services/            # Business logic
       utils/               # PDF processing & embeddings
    alembic/                 # Database migrations
    tests/                   # Unit & integration tests
    seed_data.py             # Sample clause seeder
 frontend/
    src/
        app/                 # Next.js pages
        lib/                 # API client
 docker-compose.yml           # Container orchestration
```

## Quick Start

### Prerequisites

- Docker & Docker Compose (recommended)
- OR Python 3.11+, Node.js 18+, PostgreSQL 15+ with pgvector

### Option 1: Docker (Recommended)

```bash
# Clone the repository
cd "AI Contract Review & Compliance System"

# Start all services
make up

# The application will be available at:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

#### 1. Setup PostgreSQL with pgvector

```bash
# Install PostgreSQL and pgvector extension
# macOS with Homebrew:
brew install postgresql pgvector

# Start PostgreSQL
brew services start postgresql

# Create database
createdb contract_compliance

# Enable pgvector extension
psql contract_compliance -c "CREATE EXTENSION vector;"
```

#### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
alembic upgrade head

# Seed database with sample clauses
python seed_data.py

# Start backend server
uvicorn app.main:app --reload
```

Backend will run at http://localhost:8000

#### 3. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.local.example .env.local

# Start development server
npm run dev
```

Frontend will run at http://localhost:3000

## Usage

### 1. Upload a Contract

1. Navigate to http://localhost:3000
2. Click "Upload Contract"
3. Select a PDF file
4. Wait for analysis to complete

### 2. View Analysis Results

The document detail page shows:
- **Risk Score**: Overall compliance risk (0-100)
- **Summary Statistics**: Counts of passed, missing, and review-needed clauses
- **Clause-by-Clause Analysis**: Side-by-side comparison of standard vs found clauses
- **Similarity Scores**: Semantic similarity percentage for each match
- **Status Indicators**: OK (green), Missing (red), Review (yellow)

### 3. Manage Standard Clauses

1. Click "Manage Clauses"
2. View clauses organized by category
3. Add new standard clauses with category, title, and text
4. Delete outdated clauses

## Testing

```bash
# Run all backend tests
make test

# Or manually
cd backend
pytest tests/ -v

# Run specific test file
pytest tests/test_embeddings.py -v
```

Test coverage includes:
- PDF text extraction and clause chunking
- Embedding generation and similarity computation
- Risk scoring logic
- Conflict detection
- API endpoints

## Configuration

### Backend Environment Variables

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/contract_compliance
UPLOAD_DIR=./uploads
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
SIMILARITY_THRESHOLD=0.75
MISSING_WEIGHT=10
CONFLICT_WEIGHT=5
```

### Frontend Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Database Schema

### Tables

- **documents**: Uploaded contracts metadata
- **standard_clauses**: Standard clause library with embeddings
- **extracted_clauses**: Clauses extracted from uploaded contracts
- **clause_analyses**: Comparison results between standard and extracted clauses

### Vector Store

Uses pgvector extension with 384-dimensional embeddings from all-MiniLM-L6-v2 model.

## API Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

```
POST   /documents/upload          Upload and analyze contract PDF
GET    /documents/                List all documents
GET    /documents/{id}            Get document with full analysis
DELETE /documents/{id}            Delete document

POST   /clauses/                  Create standard clause
GET    /clauses/                  List standard clauses
GET    /clauses/{id}              Get specific clause
PUT    /clauses/{id}              Update clause
DELETE /clauses/{id}              Delete clause
```

## How It Works

### Analysis Pipeline

1. **PDF Upload**: User uploads contract PDF
2. **Text Extraction**: PyMuPDF extracts text from PDF
3. **Clause Chunking**: Rule-based parser splits text into clauses
   - Detects numbered sections (1., 1.1, a.)
   - Identifies headings (ALL CAPS)
   - Uses paragraph breaks
4. **Embedding Generation**: Generate 384-dim vectors for each clause
5. **Similarity Matching**: 
   - Compare each standard clause against all extracted clauses
   - Find best match using cosine similarity
   - Threshold: 0.75 (configurable)
6. **Status Assignment**:
   - **OK**: Similarity ≥ threshold, no conflicts
   - **MISSING**: Similarity < threshold
   - **REVIEW**: Medium similarity + keyword conflicts
7. **Risk Scoring**: Weighted formula considering missing and review clauses
8. **Results Storage**: Save analysis to database for later viewing

### Conflict Detection

Simple heuristic checks for negation keywords:
- "not", "no", "never", "except", "without", "prohibited"
- Flags potential conflicts when one clause has negation and the other doesn't

## Future Enhancements

- [ ] OpenAI API integration for embeddings (already abstracted)
- [ ] S3 storage for PDFs (abstracted storage layer)
- [ ] Advanced NLP for clause classification
- [ ] Multi-language support
- [ ] Custom similarity thresholds per category
- [ ] Clause version history
- [ ] Export analysis reports (PDF, Excel)
- [ ] Batch document processing
- [ ] User authentication and multi-tenancy
- [ ] Webhook notifications

## Development Commands

```bash
# Using Makefile
make install    # Install dependencies
make up         # Start with Docker
make down       # Stop Docker services
make test       # Run tests
make migrate    # Run database migrations
make seed       # Seed sample data
make clean      # Clean caches and temp files
make logs       # View Docker logs

# Manual commands
cd backend && uvicorn app.main:app --reload
cd frontend && npm run dev
cd backend && pytest tests/ -v
cd backend && alembic upgrade head
```

## Seeded Standard Clauses

The application comes with 20 sample standard clauses across 8 categories:

- **Confidentiality** (2 clauses)
- **Term and Termination** (3 clauses)
- **Payment** (2 clauses)
- **Liability** (2 clauses)
- **Intellectual Property** (2 clauses)
- **Warranty** (2 clauses)
- **Indemnification** (2 clauses)
- **General Provisions** (3 clauses)
- **Dispute Resolution** (2 clauses)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is provided as-is for educational and commercial use.

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
pg_isready

# Check pgvector extension
psql contract_compliance -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

### Frontend Can't Connect to Backend

- Ensure backend is running on port 8000
- Check NEXT_PUBLIC_API_URL in frontend/.env.local
- Verify CORS settings in backend/app/main.py

### Model Download Issues

First run downloads the sentence-transformers model (~80MB). Ensure internet connection.

## Support

For issues or questions, please open a GitHub issue.

---

**Built using FastAPI, Next.js, and PostgreSQL**
