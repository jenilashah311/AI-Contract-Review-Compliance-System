# Quick Start Guide

## 🚀 Fastest Way to Run

```bash
# 1. Make sure Docker is installed and running
docker --version

# 2. Start the application
make up

# 3. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

That's it! The application will:
- Start PostgreSQL with pgvector
- Run database migrations
- Seed 20 sample standard clauses
- Start the FastAPI backend
- Start the Next.js frontend

## 📋 Quick Commands

```bash
make up      # Start everything
make down    # Stop everything
make logs    # View logs
make restart # Restart services
make clean   # Clean up temp files
```

## 🎯 First Steps

1. **Go to** http://localhost:3000
2. **Click** "Upload Contract"
3. **Upload** any PDF contract
4. **View** the compliance analysis

## 🧪 Test with Sample Clause

The system comes pre-seeded with 20 standard clauses. Your uploaded contracts will be compared against clauses like:

- Confidentiality and non-disclosure
- Payment terms
- Term and termination
- Liability limitations
- Intellectual property
- And more...

## 🔍 What to Look For

After uploading a contract, you'll see:

- **Risk Score**: 0-100 (lower is better)
- **Green (OK)**: Clause found and matches well
- **Yellow (REVIEW)**: Clause found but needs review
- **Red (MISSING)**: Required clause not found

## 🛠️ Local Development (Without Docker)

If you prefer running locally:

```bash
# Terminal 1 - Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Setup PostgreSQL database first
alembic upgrade head
python seed_data.py
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

## 📚 More Information

See [README.md](README.md) for complete documentation.
