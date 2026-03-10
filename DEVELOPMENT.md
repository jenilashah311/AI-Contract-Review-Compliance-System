# Development Guide

## Adding New Features

### Adding a New Standard Clause Category

1. **Backend** - No code changes needed! Categories are dynamic.
2. **Frontend** - Works automatically based on database content.
3. **Simply add clauses** with new category names through the API or UI.

### Adding a New Embedding Model

To switch from sentence-transformers to OpenAI or other providers:

**backend/app/utils/embeddings.py**
```python
# Add new function
def generate_embedding_openai(text: str) -> List[float]:
    # Your OpenAI integration here
    pass

# Update generate_embedding to use new function
def generate_embedding(text: str) -> List[float]:
    if settings.use_openai:
        return generate_embedding_openai(text)
    else:
        return generate_embedding_local(text)
```

**backend/app/config.py**
```python
class Settings(BaseSettings):
    use_openai: bool = False
    openai_api_key: str = ""
```

### Adding S3 Storage

Replace local file storage with S3:

**backend/app/services/document_processor.py**
```python
async def save_uploaded_file(file: UploadFile) -> str:
    if settings.use_s3:
        # Upload to S3
        s3_key = f"contracts/{uuid.uuid4()}/{file.filename}"
        s3_client.upload_fileobj(file.file, settings.s3_bucket, s3_key)
        return s3_key
    else:
        # Existing local storage logic
        ...
```

### Customizing Risk Scoring

**backend/app/services/analyzer.py**
```python
def calculate_risk_score(total: int, missing: int, review: int) -> float:
    # Customize weights
    missing_weight = settings.missing_weight  # Default: 10
    conflict_weight = settings.conflict_weight  # Default: 5
    
    # Add new factors
    critical_missing = count_critical_missing()
    
    raw_score = (
        missing * missing_weight +
        review * conflict_weight +
        critical_missing * 20  # New factor
    )
    
    # Your custom normalization
    return normalize_score(raw_score, total)
```

## Testing Strategy

### Unit Tests

Test individual functions in isolation:

```python
# tests/test_embeddings.py
def test_cosine_similarity():
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]
    assert cosine_similarity(vec1, vec2) == 1.0
```

### Integration Tests

Test API endpoints:

```python
# tests/test_integration.py
def test_upload_document():
    with open("test_contract.pdf", "rb") as f:
        response = client.post(
            "/documents/upload",
            files={"file": f}
        )
    assert response.status_code == 200
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific file
pytest tests/test_embeddings.py -v

# With coverage
pytest tests/ --cov=app --cov-report=html

# Stop on first failure
pytest tests/ -x
```

## Monitoring & Debugging

### View Logs

```bash
# Docker logs
make logs

# Or specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Database Queries

```bash
# Connect to database
docker exec -it contract_db psql -U contract_user -d contract_compliance

# Or locally
psql contract_compliance

# Check tables
\dt

# View standard clauses
SELECT id, category, title FROM standard_clauses;

# View documents
SELECT id, original_filename, risk_score FROM documents;

# Check analysis results
SELECT 
    ca.status,
    COUNT(*) as count
FROM clause_analyses ca
GROUP BY ca.status;
```

### API Testing with curl

```bash
# List documents
curl http://localhost:8000/documents/

# Get document detail
curl http://localhost:8000/documents/1

# Create standard clause
curl -X POST http://localhost:8000/clauses/ \
  -H "Content-Type: application/json" \
  -d '{
    "category": "Testing",
    "title": "Test Clause",
    "text": "This is a test clause for development."
  }'

# List standard clauses
curl http://localhost:8000/clauses/
```

## Database Migrations

### Create New Migration

```bash
cd backend

# Auto-generate from model changes
alembic revision --autogenerate -m "Add new field to documents"

# Create blank migration
alembic revision -m "Custom migration"
```

### Edit Migration

```python
# alembic/versions/xxx_add_field.py
def upgrade():
    op.add_column('documents', 
        sa.Column('new_field', sa.String(100))
    )

def downgrade():
    op.drop_column('documents', 'new_field')
```

### Apply Migrations

```bash
# Apply all pending
alembic upgrade head

# Apply specific version
alembic upgrade abc123

# Rollback one version
alembic downgrade -1

# Check current version
alembic current

# View history
alembic history
```

## Frontend Development

### Adding a New Page

1. **Create page file**: `frontend/src/app/newpage/page.tsx`
```typescript
'use client';

export default function NewPage() {
  return (
    <div>
      <h1>New Page</h1>
    </div>
  );
}
```

2. **Add navigation**: Update other pages to link to it
```typescript
<button onClick={() => router.push('/newpage')}>
  Go to New Page
</button>
```

### API Integration

```typescript
// frontend/src/lib/api.ts

// Add new interface
export interface NewDataType {
  id: number;
  name: string;
}

// Add new API function
export const getNewData = async (): Promise<NewDataType[]> => {
  const response = await api.get<NewDataType[]>('/new-endpoint/');
  return response.data;
};
```

### Styling

Use CSS Modules for component-specific styles:

```css
/* page.module.css */
.container {
  max-width: 1200px;
  margin: 0 auto;
}

.button {
  background: #667eea;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
}
```

```typescript
import styles from './page.module.css';

<div className={styles.container}>
  <button className={styles.button}>Click Me</button>
</div>
```

## Common Issues & Solutions

### Issue: "Connection refused" to PostgreSQL

**Solution:**
```bash
# Check if PostgreSQL is running
docker ps
# or
brew services list

# Restart PostgreSQL
docker-compose restart postgres
# or
brew services restart postgresql
```

### Issue: "Module 'pgvector' not found"

**Solution:**
```bash
# Install pgvector extension
psql contract_compliance -c "CREATE EXTENSION vector;"

# Or in Docker
docker exec -it contract_db psql -U contract_user -d contract_compliance \
  -c "CREATE EXTENSION vector;"
```

### Issue: Frontend can't connect to backend

**Solution:**
1. Check backend is running: `curl http://localhost:8000/health`
2. Check CORS settings in `backend/app/main.py`
3. Verify `NEXT_PUBLIC_API_URL` in frontend `.env.local`

### Issue: "Model not found" error

**Solution:**
The sentence-transformers model downloads on first use (~80MB). Ensure internet connection and wait for download to complete.

```bash
# Pre-download model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

### Issue: Tests failing

**Solution:**
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Check imports
python -c "import app.models"

# Run with verbose output
pytest tests/ -v -s
```

## Building for Production

### Backend

```bash
# Build Docker image
docker build -t contract-backend:latest ./backend

# Run with production settings
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend

```bash
# Build optimized production bundle
cd frontend
npm run build

# Test production build locally
npm start

# Build Docker image
docker build -t contract-frontend:latest ./frontend
```

### Docker Compose Production

```yaml
# docker-compose.prod.yml
services:
  backend:
    environment:
      - WORKERS=4
    restart: always
  
  frontend:
    environment:
      - NODE_ENV=production
    restart: always
```

## Security Considerations

1. **Environment Variables**: Never commit `.env` files
2. **File Upload**: Validate file types and sizes (already implemented)
3. **Database**: Use strong passwords, limit connections
4. **API**: Add rate limiting for production
5. **CORS**: Restrict origins in production

## Performance Optimization

### Backend

```python
# Use batch operations
embeddings = generate_embeddings_batch(texts)  # Instead of loop

# Add database indexes
CREATE INDEX idx_document_uploaded ON documents(uploaded_at);
CREATE INDEX idx_clause_category ON standard_clauses(category);

# Cache embeddings
@lru_cache(maxsize=100)
def get_embedding(text: str):
    return generate_embedding(text)
```

### Frontend

```typescript
// Use React.memo for expensive components
const AnalysisRow = React.memo(({ analysis }) => {
  // Component logic
});

// Implement pagination
const [page, setPage] = useState(1);
const documents = await getDocuments({ skip: (page-1)*20, limit: 20 });
```

## Deployment Checklist

- [ ] Update environment variables
- [ ] Run database migrations
- [ ] Seed initial data
- [ ] Configure CORS for production domain
- [ ] Set up file storage (S3)
- [ ] Configure reverse proxy (nginx)
- [ ] Set up SSL certificates
- [ ] Configure monitoring/logging
- [ ] Set up automated backups
- [ ] Test end-to-end functionality
- [ ] Document deployment process

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [sentence-transformers](https://www.sbert.net/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
