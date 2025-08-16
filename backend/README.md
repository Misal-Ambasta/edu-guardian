# Edu-Guardian Backend

RAG-Powered Historical Intelligence - Backend Implementation

## Overview

This is the backend component of the Edu-Guardian project, implementing:

- Advanced emotion analysis for student feedback
- Historical pattern matching with vector database
- Predictive analytics for student emotional trajectories
- Weekly intelligence report generation
- Emotion-based intervention tracking

## Tech Stack

- **FastAPI**: Modern, high-performance web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation and settings management
- **ChromaDB**: Vector database for semantic search and pattern matching
- **Google Gemini AI**: Embedding model (gemini-embedding-001) and retrieval LLM (gemini-2.5-flash)
- **PostgreSQL** (via NeonDB): Primary relational database
- **Python 3.9+**: Core programming language
- **Python-Multipart**: For handling file uploads

## Getting Started

### Prerequisites

- Python 3.9 or higher
- PostgreSQL installed locally (for development) or access to NeonDB (for production)

### Setup

1. **Create and activate a virtual environment:**

   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**

   Create a `.env` file in the project root with the following variables:

   ```
   # Database Configuration
   DATABASE_URL=postgresql://postgres:password@localhost:5432/edu_guardian_dev

   # For production, use Neon DB URL:
   # DATABASE_URL=postgres://user:password@ep-some-id.us-east-2.aws.neon.tech/edu_guardian

   # Authentication
   SECRET_KEY=your_secret_key_here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # ChromaDB Configuration
   CHROMA_DB_PATH=./chromadb
   
   # Google Gemini AI Configuration (Required)
   GOOGLE_API_KEY=your_google_api_key_here
   
   # Redis Cache Configuration
   REDIS_URL=redis://localhost:6379/0
   CACHE_TTL=3600
   ```

   > **Note**: The Google API Key is now required. The system will throw an error if it's not provided.

4. **Setup the database:**

   ```bash
   # When alembic migrations are ready
   alembic upgrade head
   ```

5. **Initialize ChromaDB:**

   ```bash
   python -m app.database.init_chroma
   ```

### Running the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000, and the interactive documentation at http://localhost:8000/docs.

## API Endpoints

### Data Upload

#### Upload CSV File

```
POST /api/students/upload-csv
```

Uploads a CSV file containing student feedback data for processing. The file should contain the following columns:
- student_id
- timestamp
- course_id
- week_number
- nps_score
- lms_usability_score
- instructor_quality_score
- content_difficulty_score
- support_quality_score
- course_pace_score
- comments (optional)

The endpoint performs emotion analysis on the comments and saves the data to the database.

#### Process Batch Directory

```
POST /api/students/upload-batch
```

Processes all CSV files in a specified directory. This endpoint is useful for bulk data processing.

## Project Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI application entry point
│   ├── database/                # Database connection and setup
│   ├── models/                  # SQLAlchemy and Pydantic models
│   ├── routers/                 # API route definitions
│   ├── services/                # Business logic
│   ├── emotion_analysis/        # Emotion analysis engine
│   └── utils/                   # Utility functions
├── migrations/                  # Database migrations (Alembic)
├── tests/                       # Test suite
├── requirements.txt             # Project dependencies
└── .env                         # Environment variables (not in version control)
```

## API Endpoints

- **Authentication**: `/api/auth/`
  - Register, login, and user management

- **Emotion Analysis**: `/api/emotion/`
  - Text analysis for emotion detection
  - Batch processing of feedback

- **Weekly Reports**: `/api/reports/`
  - Generate and retrieve weekly intelligence reports

- **Interventions**: `/api/interventions/`
  - Create and track emotion-based interventions

- **Students**: `/api/students/`
  - Student management and emotional journey tracking

## Development

### Adding a New API Endpoint

1. Create or update route in the appropriate router file in `app/routers/`
2. Implement service logic in `app/services/`
3. Add models as needed in `app/models/`
4. Update documentation

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head
```
