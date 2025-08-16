
"""Emotion module for the application.

This module provides functionality related to emotion.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from langchain_core.documents import Document

from app.utils.pattern_utils import create_historical_pattern
from app.utils.trajectory_utils import get_emotion_trajectory_prediction
from ..database.db import get_db
from ..services.vector_db_factory import VectorDBFactory
from ..services.historical_pattern import HistoricalPatternService
from ..emotion_analysis.analyzer import EmotionProfile
from ..models.historical_pattern import HistoricalPattern, EmotionPatternMatch
from ..services.trajectory_predictor import EmotionTrajectoryPredictor
from ..models.emotion_trajectory import EmotionTrajectoryPrediction, StudentEmotionHistory
router = APIRouter()

# Initialize services
vector_db_service = VectorDBFactory.create_vector_db_service()
historical_pattern_service = HistoricalPatternService()

@router.get("/analyze")
async def analyze_emotion(text: str, db: Session = Depends(get_db)):
    """
    Analyze emotion in text and return comprehensive emotion profile
    """
    # Initialize the emotion analyzer
    from ..emotion_analysis.analyzer import AdvancedEmotionAnalyzer
    analyzer = AdvancedEmotionAnalyzer()

    # Analyze the text
    emotion_profile = analyzer.analyze_text(text)

    # Return the emotion profile as a dictionary
    return {"analysis": emotion_profile.model_dump()}


@router.post("/batch-analyze")
async def batch_analyze_emotions(texts: List[str], db: Session = Depends(get_db)):
    """
    Analyze emotions in a batch of texts
    """
    # Initialize the emotion analyzer
    from ..emotion_analysis.analyzer import AdvancedEmotionAnalyzer
    analyzer = AdvancedEmotionAnalyzer()

    # Process each text in the batch
    results = []
    for text in texts:
        # Analyze the text
        emotion_profile = analyzer.analyze_text(text)

        # Add the result to the list
        results.append({
            "text": text,
            "analysis": emotion_profile.model_dump()
        })

    return {"results": results}


@router.get("/similar-patterns/{student_id}")
async def find_similar_emotion_patterns(
    student_id: str,
    course_id: str,
    week_number: int,
    limit: Optional[int] = 5,
    db: Session = Depends(get_db)
):
    """
    Find students with similar emotion patterns using vector database with LangChain
    """
    try:
        # Get similar patterns using the vector database service
        result = vector_db_service.find_emotion_similar_students(
            student_id=student_id,
            course_id=course_id,
            week_number=week_number,
            limit=limit
        )

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )

        # Convert the results to LangChain Documents and then to EmotionPatternMatch objects
        documents = []
        scores = []
        for pattern in result:
            # Create a Document from the pattern
            doc = Document(
                page_content=pattern["emotion_profile"],
                metadata=pattern["metadata"]
            )
            documents.append(doc)
            scores.append(pattern["distance"])

        # Create a HistoricalPattern from the documentsawait create_historical_pattern(student_id=student_id, course_id=course_id, week_number=week_number, documents=documents, scores=scores)

        return historical_pattern
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/trajectory-prediction/{student_id}")
async def predict_emotion_trajectory(
    student_id: str,
    course_id: str,
    db: Session = Depends(get_db)
):
    """
    Predict the evolution of student emotions over time based on historical data
    """
    try:
        prediction = await get_emotion_trajectory_prediction(student_id=student_id, course_id=course_id, db=db)
        return prediction
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error predicting emotion trajectory: {str(e)}"
        )

@router.get("/multi-week-prediction/{student_id}")
async def predict_multi_week_emotions(
    student_id: str,
    course_id: str,
    weeks_ahead: int = 2,
    db: Session = Depends(get_db)
):
    """
    Predict student emotions for multiple weeks ahead
    """
    try:
        prediction = await get_emotion_trajectory_prediction(student_id=student_id, course_id=course_id, db=db)

        # Return only the risk escalations part
        return prediction.risk_escalations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error predicting risk escalation: {str(e)}"
        )

@router.get("/intervention-window/{student_id}")
async def get_optimal_intervention_window(
    student_id: str,
    course_id: str,
    db: Session = Depends(get_db)
):
    """
    Get optimal intervention windows for a student
    """
    try:
        prediction = await get_emotion_trajectory_prediction(student_id=student_id, course_id=course_id, db=db)

        # Return only the optimal intervention windows part
        return prediction.optimal_intervention_windows
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error finding optimal intervention window: {str(e)}"
        )

@router.post("/store-emotion-vector")
async def store_emotion_vector(
    student_id: str,
    course_id: str,
    week_number: int,
    emotion_profile: EmotionProfile,
    metadata: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
):
    """
    Store an emotion vector in the vector database using LangChain
    """
    try:
        # Create a LangChain Document from the emotion profile
        import json

        # Convert emotion profile to JSON string
        emotion_json = json.dumps(emotion_profile.dict())

        # Prepare metadata
        doc_metadata = metadata or {}
        doc_metadata["student_id"] = student_id
        doc_metadata["course_id"] = course_id
        doc_metadata["week_number"] = week_number

        # Create a unique ID
        document_id = f"{student_id}_{course_id}_{week_number}"

        # Create a Document
        document = Document(
            page_content=emotion_json,
            metadata=doc_metadata,
            id=document_id
        )

        # Store the emotion vector using the service
        document_id = vector_db_service.store_emotion_pattern(
            student_id=student_id,
            course_id=course_id,
            week_number=week_number,
            emotion_profile=emotion_profile,
            additional_metadata=metadata
        )

        return {"document_id": document_id, "status": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error storing emotion vector: {str(e)}"
        )

@router.get("/recommended-interventions/{student_id}")
async def get_recommended_interventions(
    student_id: str,
    course_id: str,
    week_number: int,
    db: Session = Depends(get_db)
):
    """Get recommended interventions for a student based on historical patterns using LangChain"""
    # First find similar emotion patterns using LangChain
    similar_patterns = vector_db_service.find_emotion_similar_students(
        student_id=student_id,
        course_id=course_id,
        week_number=week_number,
        limit=5
    )

    # Get recommended interventions based on these patterns
    interventions = await historical_pattern_service.get_recommended_interventions(
        student_id=student_id,
        course_id=course_id,
        week_number=week_number,
        similar_patterns=similar_patterns
    )
    return interventions

@router.get("/historical-patterns/{student_id}")
async def recognize_historical_patterns(
    student_id: str,
    course_id: str,
    week_number: int,
    db: Session = Depends(get_db)
):
    """Recognize historical patterns in a student's emotion data"""
    try:
        # Use the historical pattern service to recognize patterns
        patterns = await historical_pattern_service.recognize_historical_patterns(
            student_id=student_id,
            course_id=course_id,
            week_number=week_number
        )

        return patterns
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recognizing historical patterns: {str(e)}"
        )

@router.get("/pattern-signature")
async def generate_pattern_signature(
    emotion_profile: EmotionProfile,
    db: Session = Depends(get_db)
):
    """Generate a signature for an emotion pattern"""
    try:
        # Use the historical pattern service to generate a signature
        signature = await historical_pattern_service.generate_pattern_signature(emotion_profile)

        return {"signature": signature}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating pattern signature: {str(e)}"
        )

@router.post("/calculate-similarity")
async def calculate_pattern_similarity(
    pattern1: EmotionProfile,
    pattern2: EmotionProfile,
    db: Session = Depends(get_db)
):
    """Calculate similarity between two emotion patterns"""
    try:
        # Use the historical pattern service to calculate similarity
        similarity = await historical_pattern_service.calculate_pattern_similarity(
            pattern1, pattern2)

        return {"similarity_score": similarity}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating pattern similarity: {str(e)}"
        )

@router.get("/successful-interventions")
async def identify_successful_interventions(
    student_id: str,
    course_id: str,
    week_number: int,
    limit: Optional[int] = 5,
    db: Session = Depends(get_db)
):
    """Identify successful interventions from historical pattern matches"""
    try:
        # First get similar patterns
        result = vector_db_service.find_emotion_similar_students(
            student_id=student_id,
            course_id=course_id,
            week_number=week_number,
            limit=limit
        )

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )

        # Identify successful interventions
        interventions = await historical_pattern_service.identify_successful_interventions(result)

        return {"successful_interventions": interventions}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error identifying successful interventions: {str(e)}"
        )
