# Edu-Guardian API Documentation

## Overview

The Edu-Guardian API provides a comprehensive set of endpoints for emotion analysis, student tracking, intervention management, and report generation. This document outlines all available endpoints, their parameters, and response formats.

## Base URL

All API endpoints are relative to the base URL: `http://localhost:8000/api`

## Authentication

Most endpoints require authentication using JWT tokens.

### Authentication Endpoints

#### POST /auth/register

Register a new user.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "full_name": "string"
}
```

**Response:**
```json
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "full_name": "string"
}
```

#### POST /auth/login

Authenticate a user and receive a JWT token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

## Core Emotional Intelligence

### GET /students/{id}/emotion-analysis

Get comprehensive emotion analysis for a specific student.

**Path Parameters:**
- `id` (string): Student ID

**Query Parameters:**
- `time_period` (string, optional): Time period for analysis (e.g., "week", "month", "all")

**Response:**
```json
{
  "student_id": "string",
  "frustration": {
    "level": "string",
    "type": "string",
    "intensity": "float"
  },
  "urgency": {
    "level": "string",
    "response_time_hours": "float"
  },
  "hidden_dissatisfaction": {
    "detected": "boolean",
    "confidence": "float",
    "indicators": ["string"]
  },
  "emotional_temperature": {
    "value": "float",
    "volatility": "float"
  }
}
```

### GET /students/{id}/hidden-dissatisfaction-check

Check for hidden dissatisfaction in a student's feedback.

**Path Parameters:**
- `id` (string): Student ID

**Response:**
```json
{
  "student_id": "string",
  "detected": "boolean",
  "confidence": "float",
  "indicators": ["string"],
  "recommended_actions": ["string"]
}
```

### GET /students/{id}/emotion-trajectory-prediction

Predict the emotional trajectory for a student.

**Path Parameters:**
- `id` (string): Student ID

**Query Parameters:**
- `weeks_ahead` (integer, optional): Number of weeks to predict ahead (default: 2)

**Response:**
```json
{
  "student_id": "string",
  "predictions": [
    {
      "week": "integer",
      "frustration_level": "string",
      "emotional_temperature": "float",
      "risk_level": "string",
      "potential_crisis": "boolean"
    }
  ],
  "optimal_intervention_window": {
    "start_week": "integer",
    "end_week": "integer",
    "urgency": "string"
  }
}
```

### POST /students/{id}/emotion-intervention-recommend

Get recommended interventions based on emotional analysis.

**Path Parameters:**
- `id` (string): Student ID

**Response:**
```json
{
  "student_id": "string",
  "recommended_interventions": [
    {
      "intervention_type": "string",
      "target_emotion": "string",
      "urgency_level": "string",
      "success_probability": "float",
      "historical_success_rate": "float"
    }
  ],
  "optimal_timing": {
    "within_hours": "float",
    "optimal_day": "string"
  }
}
```

## Advanced Emotion Analytics

### GET /emotions/frustration-analysis/{course_id}

Get frustration analysis for an entire course.

**Path Parameters:**
- `course_id` (string): Course ID

**Response:**
```json
{
  "course_id": "string",
  "overall_frustration_level": "string",
  "frustration_distribution": {
    "high": "float",
    "medium": "float",
    "low": "float"
  },
  "frustration_hotspots": [
    {
      "week": "integer",
      "intensity": "float",
      "affected_students": "integer"
    }
  ],
  "at_risk_students": [
    {
      "student_id": "string",
      "frustration_level": "string",
      "days_at_high_level": "integer"
    }
  ]
}
```

### GET /emotions/urgency-distribution/{course_id}

Get urgency distribution for a course.

**Path Parameters:**
- `course_id` (string): Course ID

**Response:**
```json
{
  "course_id": "string",
  "urgency_distribution": {
    "critical": "float",
    "high": "float",
    "medium": "float",
    "low": "float"
  },
  "average_response_time_hours": "float",
  "students_needing_immediate_response": [
    {
      "student_id": "string",
      "urgency_level": "string",
      "hours_since_feedback": "float"
    }
  ]
}
```

### GET /emotions/hidden-dissatisfaction-patterns/{course_id}

Get hidden dissatisfaction patterns for a course.

**Path Parameters:**
- `course_id` (string): Course ID

**Response:**
```json
{
  "course_id": "string",
  "hidden_dissatisfaction_rate": "float",
  "common_indicators": ["string"],
  "affected_students": [
    {
      "student_id": "string",
      "confidence": "float",
      "specific_indicators": ["string"]
    }
  ],
  "recommended_course_adjustments": ["string"]
}
```

### POST /emotions/emotional-crisis-prediction

Predict potential emotional crises across students.

**Request Body:**
```json
{
  "course_id": "string",
  "prediction_window_days": "integer"
}
```

**Response:**
```json
{
  "course_id": "string",
  "prediction_window_days": "integer",
  "potential_crises": [
    {
      "student_id": "string",
      "crisis_probability": "float",
      "estimated_days_until_crisis": "integer",
      "contributing_factors": ["string"],
      "recommended_preventive_actions": ["string"]
    }
  ],
  "overall_emotional_health": "string"
}
```

## Weekly Emotional Intelligence Reports

### GET /reports/weekly-emotion-intelligence/{course_id}/{week}

Get weekly emotional intelligence report for a course.

**Path Parameters:**
- `course_id` (string): Course ID
- `week` (integer): Week number

**Response:**
```json
{
  "course_id": "string",
  "week": "integer",
  "executive_summary": "string",
  "emotion_analysis": {
    "frustration_analysis": {},
    "urgency_analysis": {},
    "hidden_dissatisfaction_analysis": {},
    "emotional_temperature_analysis": {}
  },
  "risk_prediction": {
    "at_risk_students": [],
    "historical_patterns": [],
    "predictive_insights": []
  },
  "intervention_tracking": {
    "interventions_this_week": [],
    "success_rate": "float",
    "template_performance": {}
  },
  "recommendations": {
    "immediate_actions": [],
    "strategic_initiatives": []
  }
}
```

### POST /reports/generate-emotion-report

Generate a new emotional intelligence report.

**Request Body:**
```json
{
  "course_id": "string",
  "week": "integer",
  "include_predictions": "boolean",
  "include_recommendations": "boolean"
}
```

**Response:**
```json
{
  "report_id": "string",
  "course_id": "string",
  "week": "integer",
  "generation_status": "string",
  "report_url": "string"
}
```

### GET /reports/emotion-report-history/{course_id}

Get history of emotional intelligence reports for a course.

**Path Parameters:**
- `course_id` (string): Course ID

**Response:**
```json
{
  "course_id": "string",
  "reports": [
    {
      "report_id": "string",
      "week": "integer",
      "generation_date": "string",
      "report_url": "string"
    }
  ]
}
```

## Emotion-Based Interventions

### POST /interventions/emotion-targeted

Create a new emotion-targeted intervention.

**Request Body:**
```json
{
  "student_id": "string",
  "intervention_type": "string",
  "target_emotion": "string",
  "emotional_urgency_level": "string",
  "intervention_details": {}
}
```

**Response:**
```json
{
  "id": "uuid",
  "student_id": "string",
  "intervention_type": "string",
  "target_emotion": "string",
  "emotional_urgency_level": "string",
  "created_at": "string"
}
```

### GET /interventions/emotion-success-rates

Get success rates for emotion-targeted interventions.

**Query Parameters:**
- `intervention_type` (string, optional): Filter by intervention type
- `target_emotion` (string, optional): Filter by target emotion

**Response:**
```json
{
  "overall_success_rate": "float",
  "by_emotion": {
    "frustration": "float",
    "hidden_dissatisfaction": "float",
    "urgency": "float"
  },
  "by_intervention_type": {
    "mentor_meeting": "float",
    "additional_resources": "float",
    "deadline_extension": "float"
  },
  "most_effective_combinations": [
    {
      "emotion": "string",
      "intervention": "string",
      "success_rate": "float"
    }
  ]
}
```

### GET /templates/emotion-specific-templates

Get emotion-specific intervention templates.

**Query Parameters:**
- `target_emotion` (string, optional): Filter by target emotion

**Response:**
```json
{
  "templates": [
    {
      "template_id": "string",
      "name": "string",
      "target_emotion": "string",
      "description": "string",
      "success_rate": "float",
      "average_response_time": "float"
    }
  ]
}
```

## Health Check

### GET /health

Check the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "service": "edu-guardian-api"
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Error message describing the issue with the request"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```