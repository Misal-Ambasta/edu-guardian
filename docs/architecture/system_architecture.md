# Edu-Guardian System Architecture

## Overview

The Edu-Guardian system is designed as a comprehensive emotion intelligence platform for educational institutions. This document outlines the system architecture, component interactions, and data flow.

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Applications                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Web Frontend │  │ Mobile App  │  │ Admin Dashboard         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                          API Gateway                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Auth Service │  │ Rate Limiter│  │ Request Validation      │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                       FastAPI Backend                           │
│                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────────────────┐   │
│  │ Emotion Analysis    │  │ Historical Pattern Service      │   │
│  │ Engine              │  │                                 │   │
│  │ ┌─────────────────┐ │  │ ┌─────────────────────────┐    │   │
│  │ │ Frustration     │ │  │ │ Pattern Matching        │    │   │
│  │ │ Analysis        │ │  │ └─────────────────────────┘    │   │
│  │ └─────────────────┘ │  │ ┌─────────────────────────┐    │   │
│  │ ┌─────────────────┐ │  │ │ Outcome Prediction      │    │   │
│  │ │ Urgency         │ │  │ └─────────────────────────┘    │   │
│  │ │ Detection       │ │  └─────────────────────────────────┘   │
│  │ └─────────────────┘ │  ┌─────────────────────────────────┐   │
│  │ ┌─────────────────┐ │  │ Trajectory Predictor           │   │
│  │ │ Hidden          │ │  │                                 │   │
│  │ │ Dissatisfaction │ │  │ ┌─────────────────────────┐    │   │
│  │ └─────────────────┘ │  │ │ Emotion Trajectory      │    │   │
│  │ ┌─────────────────┐ │  │ │ Prediction              │    │   │
│  │ │ Emotional       │ │  │ └─────────────────────────┘    │   │
│  │ │ Temperature     │ │  │ ┌─────────────────────────┐    │   │
│  │ └─────────────────┘ │  │ │ Intervention Window     │    │   │
│  └─────────────────────┘  │ │ Optimization            │    │   │
│  ┌─────────────────────┐  │ └─────────────────────────┘    │   │
│  │ Intervention        │  └─────────────────────────────────┘   │
│  │ Tracker             │  ┌─────────────────────────────────┐   │
│  │                     │  │ Report Generator               │   │
│  │ ┌─────────────────┐ │  │                                 │   │
│  │ │ Effectiveness   │ │  │ ┌─────────────────────────┐    │   │
│  │ │ Measurement     │ │  │ │ Weekly NPS Reports      │    │   │
│  │ └─────────────────┘ │  │ └─────────────────────────┘    │   │
│  │ ┌─────────────────┐ │  │ ┌─────────────────────────┐    │   │
│  │ │ Template        │ │  │ │ Executive Summaries     │    │   │
│  │ │ Performance     │ │  │ └─────────────────────────┘    │   │
│  │ └─────────────────┘ │  │ ┌─────────────────────────┐    │   │
│  └─────────────────────┘  │ │ Recommendation Engine   │    │   │
│                           │ └─────────────────────────┘    │   │
│                           └─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Data Layer                                │
│                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────────────────┐   │
│  │ NeonDB              │  │ ChromaDB                        │   │
│  │ (PostgreSQL)        │  │ (Vector Database)               │   │
│  │                     │  │                                 │   │
│  │ ┌─────────────────┐ │  │ ┌─────────────────────────┐    │   │
│  │ │ Student Journeys│ │  │ │ Emotion Vectors         │    │   │
│  │ └─────────────────┘ │  │ └─────────────────────────┘    │   │
│  │ ┌─────────────────┐ │  │ ┌─────────────────────────┐    │   │
│  │ │ Weekly Reports  │ │  │ │ Historical Patterns     │    │   │
│  │ └─────────────────┘ │  │ └─────────────────────────┘    │   │
│  │ ┌─────────────────┐ │  └─────────────────────────────────┘   │
│  │ │ Student Outcomes│ │  ┌─────────────────────────────────┐   │
│  │ └─────────────────┘ │  │ Redis Cache                     │   │
│  │ ┌─────────────────┐ │  │                                 │   │
│  │ │ Interventions   │ │  │ ┌─────────────────────────┐    │   │
│  │ └─────────────────┘ │  │ │ Query Cache             │    │   │
│  │ ┌─────────────────┐ │  │ └─────────────────────────┘    │   │
│  │ │ Historical      │ │  │ ┌─────────────────────────┐    │   │
│  │ │ Patterns        │ │  │ │ Vector Cache            │    │   │
│  │ └─────────────────┘ │  │ └─────────────────────────┘    │   │
│  └─────────────────────┘  └─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                       External Services                         │
│                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────────────────┐   │
│  │ Google Gemini AI    │  │ Email Notification Service      │   │
│  └─────────────────────┘  └─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Component Descriptions

### Client Applications

- **Web Frontend**: React + TypeScript application for users to interact with the system
- **Mobile App**: Future mobile application for on-the-go access
- **Admin Dashboard**: Administrative interface for system configuration and monitoring

### API Gateway

- **Auth Service**: Handles authentication and authorization
- **Rate Limiter**: Prevents API abuse
- **Request Validation**: Validates incoming requests

### FastAPI Backend

#### Emotion Analysis Engine

The core of the system, responsible for analyzing student feedback and detecting emotional states:

- **Frustration Analysis**: Detects frustration levels, types, and intensity
- **Urgency Detection**: Identifies urgency levels and estimates response times
- **Hidden Dissatisfaction**: Detects dissatisfaction masked by polite language
- **Emotional Temperature**: Calculates overall emotional state and volatility

#### Historical Pattern Service

Identifies and matches historical patterns to predict outcomes:

- **Pattern Matching**: Matches current emotion profiles with historical patterns
- **Outcome Prediction**: Predicts likely outcomes based on historical data

#### Trajectory Predictor

Predicts future emotional states and optimal intervention timing:

- **Emotion Trajectory Prediction**: Forecasts emotional states over time
- **Intervention Window Optimization**: Identifies optimal timing for interventions

#### Intervention Tracker

Tracks and analyzes intervention effectiveness:

- **Effectiveness Measurement**: Measures the impact of interventions on emotional states
- **Template Performance**: Analyzes the performance of different intervention templates

#### Report Generator

Generates comprehensive reports and insights:

- **Weekly NPS Reports**: Creates detailed weekly reports with emotion analysis
- **Executive Summaries**: Generates concise summaries for leadership
- **Recommendation Engine**: Provides actionable recommendations

### Data Layer

#### NeonDB (PostgreSQL)

Relational database for structured data:

- **Student Journeys**: Stores student feedback and emotion analysis
- **Weekly Reports**: Stores generated weekly reports
- **Student Outcomes**: Tracks final outcomes for students
- **Interventions**: Records applied interventions and their results
- **Historical Patterns**: Stores identified historical patterns

#### ChromaDB (Vector Database)

Vector database for similarity search:

- **Emotion Vectors**: Stores vector embeddings of emotion profiles
- **Historical Patterns**: Stores vector representations of historical patterns

#### Redis Cache

In-memory cache for performance optimization:

- **Query Cache**: Caches frequent database queries
- **Vector Cache**: Caches vector embeddings for faster similarity search

### External Services

- **Google Gemini AI**: Provides advanced AI capabilities for emotion analysis
- **Email Notification Service**: Sends notifications and reports to stakeholders

## Data Flow

### Student Feedback Processing

1. Student feedback is collected through the frontend or imported via CSV
2. The Emotion Analysis Engine processes the feedback to extract emotional states
3. The processed data is stored in the Student Journeys table
4. Vector embeddings are generated and stored in ChromaDB
5. The Historical Pattern Service checks for matches with known patterns
6. If a match is found, the system predicts potential outcomes and recommends interventions

### Intervention Process

1. The system recommends interventions based on emotional analysis and historical patterns
2. Administrators apply interventions through the frontend
3. The Intervention Tracker records the intervention details
4. The system monitors subsequent feedback to measure intervention effectiveness
5. The results are used to update intervention success rates and template performance metrics

### Weekly Report Generation

1. The Report Generator collects data from all sources at the end of each week
2. The Emotion Analysis Engine provides aggregated emotion analysis
3. The Historical Pattern Service contributes pattern matching insights
4. The Trajectory Predictor forecasts future emotional states
5. The Intervention Tracker provides intervention effectiveness metrics
6. The Report Generator compiles all information into a comprehensive weekly report
7. The report is distributed to stakeholders via email and made available in the dashboard

## Scalability and Performance

### Horizontal Scaling

The system is designed for horizontal scaling:

- Stateless API servers can be scaled out behind a load balancer
- Database read replicas can be added for read-heavy workloads
- Vector search can be distributed across multiple nodes

### Performance Optimizations

The system includes several performance optimizations:

- **Caching**: Redis-based caching for frequent operations
- **Vector Cache**: In-memory cache for vector embeddings
- **Batch Processing**: Batch processing for heavy computations
- **Asynchronous Processing**: Background tasks for non-blocking operations
- **Database Indexing**: Optimized indexes for frequent queries

## Security Architecture

### Authentication and Authorization

- JWT-based authentication for API access
- Role-based access control for different user types
- Secure password storage with bcrypt hashing

### Data Protection

- Encryption of sensitive data at rest
- HTTPS for all API communications
- Input validation to prevent injection attacks
- Rate limiting to prevent brute force attacks

## Monitoring and Logging

- Comprehensive logging of system activities
- Performance monitoring for all components
- Error tracking and alerting
- Regular health checks for all services

## Disaster Recovery

- Regular database backups
- Point-in-time recovery capability
- Automated failover for critical components
- Documented recovery procedures

## Conclusion

The Edu-Guardian system architecture is designed to provide a robust, scalable, and secure platform for emotion intelligence in educational settings. The modular design allows for easy extension and maintenance, while the performance optimizations ensure efficient operation even with large datasets.