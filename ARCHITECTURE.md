# System Architecture Overview

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                             │
│                     http://localhost:3000                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ HTTP/REST API
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                      NEXT.JS FRONTEND                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Home Page   │  │ Upload Page  │  │ Detail Page  │          │
│  │ (Doc List)   │  │ (File Upload)│  │ (Analysis)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌──────────────┐  ┌─────────────────────────────────┐         │
│  │Clause Mgmt   │  │      API Client (Axios)         │         │
│  └──────────────┘  └─────────────┬───────────────────┘         │
└────────────────────────────────────┼─────────────────────────────┘
                                     │
                                     │ REST API Calls
                                     │
┌────────────────────────────────────▼─────────────────────────────┐
│                    FASTAPI BACKEND                                │
│                  http://localhost:8000                            │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    API ROUTERS                           │    │
│  │  ┌──────────────────┐  ┌──────────────────────────┐    │    │
│  │  │ /documents/*     │  │ /clauses/*               │    │    │
│  │  │ - POST /upload   │  │ - GET, POST, PUT, DELETE │    │    │
│  │  │ - GET, DELETE    │  │ - Manage library         │    │    │
│  │  └──────────────────┘  └──────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                     SERVICES                             │    │
│  │  ┌──────────────────┐  ┌──────────────────────────┐    │    │
│  │  │Document Processor│  │   Analyzer Service       │    │    │
│  │  │- Save PDF        │  │- Match clauses           │    │    │
│  │  │- Extract text    │  │- Detect conflicts        │    │    │
│  │  │- Chunk clauses   │  │- Calculate risk score    │    │    │
│  │  │- Generate embeds │  │- Store analysis          │    │    │
│  │  └──────────────────┘  └──────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                      UTILITIES                           │    │
│  │  ┌──────────────────┐  ┌──────────────────────────┐    │    │
│  │  │  PDF Processor   │  │  Embeddings Generator    │    │    │
│  │  │- PyMuPDF extract │  │- sentence-transformers   │    │    │
│  │  │- Rule-based chunk│  │- Cosine similarity       │    │    │
│  │  │- Position tracking│ │- Best match finder       │    │    │
│  │  └──────────────────┘  └──────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   DATABASE ACCESS                        │    │
│  │                   (SQLAlchemy ORM)                       │    │
│  └───────────────────────────┬─────────────────────────────┘    │
└────────────────────────────────┼─────────────────────────────────┘
                                 │
                                 │ SQL + Vector Queries
                                 │
┌────────────────────────────────▼─────────────────────────────────┐
│              POSTGRESQL + pgvector DATABASE                       │
│                   localhost:5432                                  │
│                                                                   │
│  ┌────────────────────┐  ┌─────────────────────────────────┐   │
│  │    documents       │  │    standard_clauses             │   │
│  │ ──────────────────│  │ ────────────────────────────────│   │
│  │ id                 │  │ id                              │   │
│  │ filename           │  │ category                        │   │
│  │ file_path          │  │ title                           │   │
│  │ extracted_text     │  │ text                            │   │
│  │ risk_score         │  │ embedding (vector(384))         │   │
│  │ uploaded_at        │  │ created_at                      │   │
│  └────────────────────┘  └─────────────────────────────────┘   │
│                                                                   │
│  ┌────────────────────┐  ┌─────────────────────────────────┐   │
│  │ extracted_clauses  │  │    clause_analyses              │   │
│  │ ──────────────────│  │ ────────────────────────────────│   │
│  │ id                 │  │ id                              │   │
│  │ document_id        │  │ document_id                     │   │
│  │ clause_number      │  │ standard_clause_id              │   │
│  │ text               │  │ extracted_clause_id             │   │
│  │ embedding          │  │ similarity_score                │   │
│  │ start_position     │  │ status (OK/MISSING/REVIEW)      │   │
│  │ end_position       │  │ notes                           │   │
│  └────────────────────┘  └─────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow - Document Upload & Analysis

```
1. USER ACTION
   │
   ├─→ Selects PDF contract
   └─→ Clicks "Upload and Analyze"
       │
       ▼

2. FRONTEND (Next.js)
   │
   ├─→ Creates FormData with file
   ├─→ POST request to /documents/upload
   └─→ Shows loading state
       │
       ▼

3. BACKEND (FastAPI) - Upload Endpoint
   │
   ├─→ Validates PDF file type
   ├─→ Saves file to disk/storage
   └─→ Calls Document Processor
       │
       ▼

4. DOCUMENT PROCESSOR
   │
   ├─→ Extract text with PyMuPDF
   │   └─→ Returns full contract text
   │
   ├─→ Chunk into clauses
   │   └─→ Rule-based parsing
   │       ├─→ Find numbered sections
   │       ├─→ Detect headings
   │       └─→ Track positions
   │
   ├─→ Generate embeddings (batch)
   │   └─→ sentence-transformers
   │       └─→ 384-dim vectors
   │
   └─→ Save to database
       ├─→ Document record
       └─→ ExtractedClause records
       │
       ▼

5. ANALYZER SERVICE
   │
   ├─→ Load standard clauses from DB
   │   └─→ With pre-computed embeddings
   │
   ├─→ For each standard clause:
   │   │
   │   ├─→ Compare with all extracted clauses
   │   │   └─→ Cosine similarity
   │   │
   │   ├─→ Find best match
   │   │   └─→ Highest similarity score
   │   │
   │   ├─→ Determine status
   │   │   ├─→ similarity >= 0.75 → Check conflicts
   │   │   │   ├─→ No conflict → OK
   │   │   │   └─→ Conflict → REVIEW
   │   │   └─→ similarity < 0.75 → MISSING
   │   │
   │   └─→ Create ClauseAnalysis record
   │
   ├─→ Calculate risk score
   │   └─→ (missing × 10) + (review × 5)
   │       └─→ Normalized to 0-100
   │
   └─→ Update document risk_score
       │
       ▼

6. RESPONSE TO FRONTEND
   │
   └─→ JSON response with:
       ├─→ Document metadata
       ├─→ Analysis summary
       │   ├─→ Total clauses checked
       │   ├─→ Matched count
       │   ├─→ Missing count
       │   ├─→ Review count
       │   └─→ Risk score
       └─→ Success message
       │
       ▼

7. FRONTEND DISPLAY
   │
   ├─→ Show success notification
   └─→ Redirect to document detail page
       │
       ▼

8. DOCUMENT DETAIL PAGE
   │
   ├─→ Fetch full analysis
   │   └─→ GET /documents/{id}
   │
   └─→ Display:
       ├─→ Risk score with visual indicator
       ├─→ Summary statistics
       └─→ Clause-by-clause comparison
           ├─→ Standard clause text
           ├─→ Matched clause text (if found)
           ├─→ Similarity percentage
           └─→ Status badge (OK/MISSING/REVIEW)
```

## 🧠 Embedding & Similarity Flow

```
┌──────────────────────────────────────────────────────────────┐
│               TEXT TO VECTOR TRANSFORMATION                   │
└──────────────────────────────────────────────────────────────┘

Standard Clause Text:
"The receiving party shall maintain in strict confidence..."
                    │
                    ▼
        ┌───────────────────────┐
        │ sentence-transformers │
        │  (all-MiniLM-L6-v2)  │
        └───────────────────────┘
                    │
                    ▼
Embedding Vector (384 dimensions):
[0.123, -0.456, 0.789, ..., 0.321]
                    │
                    ▼
        Stored in PostgreSQL
        with pgvector extension


┌──────────────────────────────────────────────────────────────┐
│                  SIMILARITY COMPUTATION                       │
└──────────────────────────────────────────────────────────────┘

Standard Clause Embedding         Extracted Clause Embedding
[0.123, -0.456, ...]       vs.    [0.145, -0.432, ...]
        │                                  │
        └──────────────┬───────────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │  Cosine Similarity   │
            │                      │
            │  cos(θ) = A·B        │
            │          ─────       │
            │          |A||B|      │
            └──────────────────────┘
                       │
                       ▼
              Similarity Score
                   0.87
                    │
                    ▼
           ┌────────────────────┐
           │ Threshold Check    │
           │   >= 0.75?         │
           └────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
       YES                     NO
        │                       │
        ▼                       ▼
    Potential Match        MISSING Clause
        │
        ▼
   Conflict Check
        │
   ┌────┴────┐
  OK       REVIEW
```

## 📦 Component Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND LAYERS                          │
└─────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────┐
    │          FastAPI Application             │
    │              (main.py)                   │
    │  - CORS configuration                    │
    │  - Router registration                   │
    │  - OpenAPI docs                          │
    └────────────────┬─────────────────────────┘
                     │
         ┌───────────┴────────────┐
         │                        │
         ▼                        ▼
┌─────────────────┐      ┌─────────────────┐
│  Documents API  │      │   Clauses API   │
│  (routers/)     │      │   (routers/)    │
└────────┬────────┘      └────────┬────────┘
         │                        │
         └───────────┬────────────┘
                     │
                     ▼
    ┌────────────────────────────────────┐
    │      Business Logic Services       │
    │  - document_processor.py           │
    │  - analyzer.py                     │
    └────────────────┬───────────────────┘
                     │
         ┌───────────┴────────────┐
         │                        │
         ▼                        ▼
┌─────────────────┐      ┌─────────────────┐
│  PDF Processor  │      │   Embeddings    │
│  (utils/)       │      │   (utils/)      │
└─────────────────┘      └─────────────────┘
                     │
                     ▼
    ┌────────────────────────────────────┐
    │      Database Layer (ORM)          │
    │  - models.py (SQLAlchemy)          │
    │  - database.py (Session)           │
    └────────────────┬───────────────────┘
                     │
                     ▼
    ┌────────────────────────────────────┐
    │    PostgreSQL + pgvector           │
    └────────────────────────────────────┘
```

## 🎨 Frontend Component Tree

```
App (layout.tsx)
│
├── Home Page (/)
│   ├── Header
│   ├── Action Buttons
│   │   ├── Upload Button → /upload
│   │   └── Manage Clauses → /clauses
│   └── Document Grid
│       └── Document Cards
│           ├── Title
│           ├── Risk Badge
│           ├── Metadata
│           └── Actions (View/Delete)
│
├── Upload Page (/upload)
│   ├── Header with Back Button
│   ├── File Upload Area
│   ├── File Info Display
│   ├── Progress Indicator
│   └── Upload Button
│
├── Document Detail (/documents/[id])
│   ├── Header with Back Button
│   ├── Summary Card
│   │   ├── Risk Score Circle
│   │   └── Statistics Grid
│   ├── Filter Buttons (All/OK/Review/Missing)
│   └── Analysis Table
│       └── Analysis Rows
│           ├── Category & Title
│           ├── Status & Similarity
│           └── Clause Comparison
│               ├── Standard Clause Box
│               └── Extracted Clause Box
│
└── Clauses Page (/clauses)
    ├── Header with Back Button
    ├── Add Clause Button
    ├── Add Clause Form (conditional)
    └── Category Sections
        └── Clause Cards
            ├── Title
            ├── Text
            ├── Metadata
            └── Delete Button
```

## 🔌 API Endpoints Map

```
BASE URL: http://localhost:8000

Health & Info:
├── GET  /                    → API info
└── GET  /health              → Health check

Documents:
├── POST   /documents/upload  → Upload & analyze PDF
├── GET    /documents/        → List all documents
├── GET    /documents/{id}    → Get document details + analysis
└── DELETE /documents/{id}    → Delete document

Standard Clauses:
├── POST   /clauses/                → Create clause
├── GET    /clauses/                → List clauses (+ filter)
├── GET    /clauses/{id}            → Get specific clause
├── PUT    /clauses/{id}            → Update clause
├── DELETE /clauses/{id}            → Delete clause
└── GET    /clauses/categories/list → List categories

OpenAPI Docs:
├── GET /docs                 → Swagger UI
└── GET /redoc                → ReDoc
```

---

**This architecture provides:**
- ✅ Clean separation of concerns
- ✅ Modular, testable components  
- ✅ Scalable design
- ✅ Easy to extend and maintain
- ✅ Production-ready structure
