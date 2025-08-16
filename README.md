# Edu-Guardian

## Student Intelligence System with Advanced Emotion Analysis

Edu-Guardian is an AI-powered intelligence system that combines aspect-based tracking with historical pattern matching and advanced emotion classification to predict student dropouts, deliver targeted interventions, and measure actual outcomes.

## Features

- Advanced emotion classification system that detects:
  - Frustration levels and types
  - Hidden dissatisfaction with confidence scores
  - Emotional temperature and volatility
  - Urgency levels for intervention

- Historical pattern matching to identify at-risk students
- Targeted interventions based on emotional profiles
- Comprehensive weekly emotional intelligence reports
- CSV data upload for batch processing of student feedback

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy
- ChromaDB (Vector Database)
- PostgreSQL (NeonDB)
- JWT Authentication

### Frontend
- React with TypeScript
- Vite
- Tailwind CSS

## Getting Started

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate
# Unix/MacOS
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run database migrations:
```bash
python run_migrations.py
```

6. Start the backend server:
```bash
uvicorn app.main:app --reload
```

For more information, refer to the [Backend README](backend/README.md).

## Documentation

- [Product Requirements Document](PRD.md)
- [Implementation Plan](todo.md)