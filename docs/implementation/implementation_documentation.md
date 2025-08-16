# Edu-Guardian Implementation Documentation

## Overview

This document provides a comprehensive overview of the Edu-Guardian system implementation, including the technologies, components, and architecture used to build the RAG-Powered Historical Intelligence System with Advanced Emotion Analysis.

## Technology Stack

### Backend

- **Framework:** FastAPI
- **Database:** NeonDB (PostgreSQL)
- **Vector Database:** ChromaDB
- **AI Models:** Google Gemini 2.5 Flash
- **Background Tasks:** Celery
- **Caching:** Redis

### Frontend

- **Framework:** React + TypeScript
- **Visualization:** Recharts + D3
- **State Management:** React Context API
- **UI Components:** Custom emotion-focused components
- **Real-time Updates:** WebSocket

## Core Components

### Document Loaders

The system uses custom CSV loaders to import student feedback and NPS data:

```python
class EnhancedCSVLoader:
    def __init__(self, file_path, emotion_field_mapping=None):
        self.file_path = file_path
        self.emotion_field_mapping = emotion_field_mapping or {}
        
    def load(self):
        # Load CSV data with emotion field mapping
        # Returns processed documents with emotion metadata
```

### Embedding Models

The system uses the following embedding models:

1. **Text Embeddings:** Google's text-embedding-gecko model for general text embedding

```python
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(
    model="text-embedding-gecko",
    google_api_key=os.environ["GOOGLE_API_KEY"],
    task_type="retrieval_document"
)
```

2. **Emotion-Specific Embeddings:** Custom emotion-focused embedding model

```python
class EmotionEmbeddingModel:
    def __init__(self, base_embeddings):
        self.base_embeddings = base_embeddings
        
    def embed_documents(self, texts):
        # Enhance base embeddings with emotion-specific features
        base_embeddings = self.base_embeddings.embed_documents(texts)
        # Add emotion-specific embedding enhancements
        return enhanced_embeddings
```

### Vector Database

The system uses ChromaDB for storing and retrieving vector embeddings:

```python
from langchain_community.vectorstores import Chroma

chroma_db = Chroma(
    collection_name="emotion_patterns",
    embedding_function=embeddings,
    persist_directory=os.environ["CHROMA_DB_PATH"]
)
```

### Retrievers

The system implements several custom retrievers:

1. **EmotionSimilarityRetriever:** Finds similar emotion patterns

```python
class EmotionSimilarityRetriever:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        
    def get_relevant_documents(self, query, emotion_filter=None, k=5):
        # Retrieve documents with similar emotion patterns
        # Apply emotion-specific filters
        return filtered_docs
```

2. **HistoricalPatternRetriever:** Retrieves historical patterns with similar outcomes

```python
class HistoricalPatternRetriever:
    def __init__(self, vector_store, pattern_db):
        self.vector_store = vector_store
        self.pattern_db = pattern_db
        
    def get_similar_patterns(self, emotion_profile, k=5):
        # Find historical patterns similar to the current emotion profile
        # Return patterns with outcome information
        return similar_patterns
```

### LLM

The system uses Google's Gemini 2.5 Flash model for advanced emotion analysis:

```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.environ["GOOGLE_API_KEY"],
    temperature=0.2,
    top_p=0.95,
    convert_system_message_to_human=True
)
```

### Core Services

#### Emotion Analysis Engine

The `AdvancedEmotionAnalyzer` class provides multi-layer emotion analysis:

```python
class AdvancedEmotionAnalyzer:
    def __init__(self, llm):
        self.llm = llm
        
    def analyze_text(self, text):
        # Perform multi-layer emotion analysis
        # Extract frustration, urgency, hidden dissatisfaction
        return EmotionProfile(...)
        
    def detect_hidden_dissatisfaction(self, text):
        # Specialized analysis for detecting hidden dissatisfaction
        # Returns confidence score and indicators
        
    def calculate_emotional_temperature(self, texts):
        # Calculate overall emotional temperature and volatility
        # Based on multiple feedback points
```

#### Historical Pattern Service

The `HistoricalPatternService` identifies and matches historical patterns:

```python
class HistoricalPatternService:
    def __init__(self, vector_db_service, db):
        self.vector_db_service = vector_db_service
        self.db = db
        
    def find_similar_patterns(self, emotion_profile):
        # Find historical patterns similar to current emotion profile
        
    def store_pattern(self, pattern):
        # Store new pattern in vector database and relational DB
        
    def get_pattern_outcomes(self, pattern_id):
        # Get historical outcomes for a specific pattern
```

#### Trajectory Predictor

The `EmotionTrajectoryPredictor` predicts future emotional states:

```python
class EmotionTrajectoryPredictor:
    def __init__(self, llm, historical_service):
        self.llm = llm
        self.historical_service = historical_service
        
    def predict_trajectory(self, student_id, weeks_ahead=2):
        # Predict emotional trajectory for specified weeks ahead
        # Based on historical patterns and current state
        
    def identify_optimal_intervention_window(self, trajectory):
        # Identify the optimal time window for intervention
        # Based on predicted trajectory
```

#### Intervention Tracker

The `EmotionBasedInterventionTracker` tracks intervention effectiveness:

```python
class EmotionBasedInterventionTracker:
    def __init__(self, db, emotion_analyzer):
        self.db = db
        self.emotion_analyzer = emotion_analyzer
        
    def track_intervention(self, intervention_id):
        # Track the effectiveness of an intervention
        # Compare before/after emotional states
        
    def calculate_success_rates(self, filters=None):
        # Calculate success rates for interventions
        # Can be filtered by type, emotion, etc.
```

#### Report Generator

The `WeeklyNPSReportGenerator` generates comprehensive weekly reports:

```python
class WeeklyNPSReportGenerator:
    def __init__(self, db, emotion_analyzer, trajectory_predictor, intervention_tracker):
        self.db = db
        self.emotion_analyzer = emotion_analyzer
        self.trajectory_predictor = trajectory_predictor
        self.intervention_tracker = intervention_tracker
        
    def generate_report(self, course_id, week):
        # Generate comprehensive weekly report
        # Including emotion analysis, predictions, and recommendations
```

### Performance Optimization

#### Caching Service

The system uses Redis-based caching for frequent operations:

```python
class CacheService:
    def __init__(self, redis_url, ttl=3600):
        self.redis_client = redis.from_url(redis_url)
        self.ttl = ttl
        
    def cached(self, key_prefix):
        # Decorator for caching function results
        
    def invalidate_cache(self, key_prefix):
        # Invalidate cache for specific prefix
```

#### Vector Cache

The system implements an in-memory vector cache for optimized vector search:

```python
class VectorCache:
    def __init__(self, max_size=1000):
        self.cache = {}
        self.max_size = max_size
        
    def get(self, key):
        # Get vector from cache
        
    def set(self, key, vector):
        # Store vector in cache
```

#### Batch Processor

The system uses batch processing for heavy computations:

```python
class BatchProcessor:
    def __init__(self, batch_size=50):
        self.batch_size = batch_size
        
    def process_batch(self, items, process_func):
        # Process items in batches
        # Combine results
```

#### Async Service

The system implements asynchronous processing for non-blocking operations:

```python
class AsyncService:
    def __init__(self, max_workers=10):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
    def async_to_sync(self, async_func):
        # Convert async function to sync
        
    def sync_to_async(self, sync_func):
        # Convert sync function to async
```

## Database Schema

### Student Journeys

```sql
CREATE TABLE student_journeys (
    id UUID PRIMARY KEY,
    student_id VARCHAR(255) NOT NULL,
    week_number INTEGER NOT NULL,
    feedback_text TEXT,
    nps_score INTEGER,
    
    -- Emotion fields
    frustration_level VARCHAR(50),
    frustration_type VARCHAR(50),
    frustration_intensity FLOAT,
    urgency_level VARCHAR(50),
    response_time_hours FLOAT,
    hidden_dissatisfaction BOOLEAN,
    hidden_dissatisfaction_confidence FLOAT,
    emotional_temperature FLOAT,
    emotional_volatility FLOAT,
    
    -- Risk analysis
    dropout_risk_level VARCHAR(50),
    intervention_recommended BOOLEAN,
    
    -- Historical comparison
    historical_pattern_match UUID REFERENCES historical_patterns(id),
    pattern_match_confidence FLOAT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Weekly NPS Reports

```sql
CREATE TABLE weekly_nps_reports (
    id UUID PRIMARY KEY,
    course_id VARCHAR(255) NOT NULL,
    week_number INTEGER NOT NULL,
    average_nps FLOAT,
    response_rate FLOAT,
    
    -- Emotion analysis
    average_frustration_level FLOAT,
    frustration_distribution JSONB,
    average_urgency_level FLOAT,
    urgency_distribution JSONB,
    hidden_dissatisfaction_rate FLOAT,
    average_emotional_temperature FLOAT,
    
    -- Risk analysis
    at_risk_student_count INTEGER,
    at_risk_student_ids JSONB,
    
    -- Intervention tracking
    interventions_applied INTEGER,
    intervention_success_rate FLOAT,
    
    report_generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(course_id, week_number)
);
```

### Student Outcomes

```sql
CREATE TABLE student_outcomes (
    id UUID PRIMARY KEY,
    student_id VARCHAR(255) NOT NULL,
    final_status VARCHAR(50) NOT NULL, -- "Graduated", "Dropped", "Transferred", etc.
    final_grade VARCHAR(10),
    weeks_to_completion INTEGER,
    
    -- Emotion journey
    emotion_journey JSONB, -- Array of weekly emotion states
    peak_frustration_level VARCHAR(50),
    peak_frustration_week INTEGER,
    hidden_dissatisfaction_detected BOOLEAN,
    hidden_dissatisfaction_week INTEGER,
    
    -- Intervention effectiveness
    interventions_applied INTEGER,
    intervention_success_rate FLOAT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id)
);
```

### Interventions

```sql
CREATE TABLE interventions (
    id UUID PRIMARY KEY,
    student_id VARCHAR(255) NOT NULL,
    intervention_type VARCHAR(255) NOT NULL,
    
    -- Emotion-based targeting
    target_emotion VARCHAR(50),
    emotional_urgency_level VARCHAR(50),
    intervention_urgency VARCHAR(50),
    
    recommended_week INTEGER,
    applied_week INTEGER,
    intervention_details JSONB,
    
    -- Enhanced outcome tracking
    success_metrics JSONB,
    emotion_improvement JSONB,
    outcome_status VARCHAR(50),
    
    -- Timing analysis
    response_time_hours FLOAT,
    intervention_to_improvement_days INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Historical Patterns

```sql
CREATE TABLE historical_patterns (
    id UUID PRIMARY KEY,
    pattern_name VARCHAR(255) NOT NULL,
    pattern_type VARCHAR(50) NOT NULL,
    detection_rules JSONB NOT NULL,
    confidence_threshold FLOAT,
    
    -- Emotion intelligence metrics
    emotion_signatures JSONB,
    early_warning_indicators JSONB,
    
    -- Efficacy tracking
    success_rate FLOAT,
    false_positive_rate FLOAT,
    avg_detection_week FLOAT,
    
    -- Risk assessment
    business_impact VARCHAR(50),
    student_impact VARCHAR(50),
    typical_outcome VARCHAR(50),
    
    -- Intervention efficacy
    recommended_interventions JSONB,
    avg_intervention_efficacy FLOAT,
    
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Structure

The API is organized into the following routers:

### Authentication Router

Handles user registration, login, and token management.

### Emotion Router

Provides endpoints for emotion analysis, including:
- Text analysis for emotion detection
- Batch processing of feedback
- Emotion trajectory prediction
- Hidden dissatisfaction detection

### Reports Router

Manages the generation and retrieval of weekly intelligence reports.

### Interventions Router

Handles the creation and tracking of emotion-based interventions.

### Students Router

Provides endpoints for student management and emotional journey tracking.

## Deployment Configuration

### Environment Variables

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

## Conclusion

This implementation documentation provides a comprehensive overview of the Edu-Guardian system's components, architecture, and configuration. The system leverages advanced AI models, vector databases, and efficient data processing to deliver a powerful emotion intelligence platform for educational institutions.