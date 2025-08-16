from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ..database.db import get_db
from typing import List, Optional, Dict, Any
from ..services.report_generator import WeeklyNPSReportGenerator
from ..services.intelligent_report import IntelligentReportGenerator
from ..models.weekly_report import WeeklyNPSReport, WeeklyNPSReportInDB
from ..services.enhanced_rag import EnhancedRAGService
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

@router.get("/weekly", response_model=WeeklyNPSReportInDB)
async def get_weekly_report(
    course_id: str, 
    week_number: int, 
    db: Session = Depends(get_db)
):
    """
    Get a comprehensive weekly NPS intelligence report with emotion analysis
    """
    # Query the database for an existing report
    report = db.query(WeeklyNPSReport).filter(
        WeeklyNPSReport.course_id == course_id,
        WeeklyNPSReport.week_number == week_number
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weekly report for course {course_id}, week {week_number} not found"
        )
    
    return report

@router.post("/generate", response_model=WeeklyNPSReportInDB)
async def generate_report(
    course_id: str,
    week_number: int,
    force_regenerate: bool = Query(False, description="Force regeneration even if a report already exists"),
    db: Session = Depends(get_db)
):
    """
    Generate a new weekly report on demand
    """
    # Check if report already exists
    existing_report = db.query(WeeklyNPSReport).filter(
        WeeklyNPSReport.course_id == course_id,
        WeeklyNPSReport.week_number == week_number
    ).first()
    
    if existing_report and not force_regenerate:
        return existing_report
    
    # Generate a new report
    report_generator = WeeklyNPSReportGenerator(db)
    report = await report_generator.generate_comprehensive_report(course_id, week_number)
    
    return report
    
@router.get("/ai-insights")
async def get_ai_powered_insights(
    course_id: str,
    week_number: int,
    db: Session = Depends(get_db)
):
    """
    Get AI-powered insights for a specific course and week
    """
    # First, get the weekly report data
    report = db.query(WeeklyNPSReport).filter(
        WeeklyNPSReport.course_id == course_id,
        WeeklyNPSReport.week_number == week_number
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weekly report for course {course_id}, week {week_number} not found"
        )
    
    # Initialize the intelligent report generator
    intelligent_report_generator = IntelligentReportGenerator(db)
    
    # Convert the report to a dictionary
    weekly_data = {
        "course_id": report.course_id,
        "week_number": report.week_number,
        "nps_score": report.nps_score,
        "emotion_metrics": {
            "avg_frustration": report.avg_frustration,
            "avg_engagement": report.avg_engagement,
            "avg_confidence": report.avg_confidence,
            "avg_satisfaction": report.avg_satisfaction,
            "avg_emotional_temperature": report.avg_emotional_temperature
        },
        "risk_metrics": {
            "high_risk_students": report.high_risk_students,
            "critical_risk_students": report.critical_risk_students
        }
    }
    
    # Generate AI-powered insights
    insights = await intelligent_report_generator.generate_ai_powered_insights(weekly_data)
    
    return insights
    
@router.get("/recommendations")
async def get_dynamic_recommendations(
    course_id: str,
    week_number: int,
    db: Session = Depends(get_db)
):
    """
    Get dynamic recommendations based on AI insights
    """
    # First, get the weekly report data
    report = db.query(WeeklyNPSReport).filter(
        WeeklyNPSReport.course_id == course_id,
        WeeklyNPSReport.week_number == week_number
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weekly report for course {course_id}, week {week_number} not found"
        )
    
    # Initialize the intelligent report generator
    intelligent_report_generator = IntelligentReportGenerator(db)
    
    # Convert the report to a dictionary
    weekly_data = {
        "course_id": report.course_id,
        "week_number": report.week_number,
        "nps_score": report.nps_score,
        "emotion_metrics": {
            "avg_frustration": report.avg_frustration,
            "avg_engagement": report.avg_engagement,
            "avg_confidence": report.avg_confidence,
            "avg_satisfaction": report.avg_satisfaction,
            "avg_emotional_temperature": report.avg_emotional_temperature
        },
        "risk_metrics": {
            "high_risk_students": report.high_risk_students,
            "critical_risk_students": report.critical_risk_students
        }
    }
    
    # Generate AI-powered insights first
    insights = await intelligent_report_generator.generate_ai_powered_insights(weekly_data)
    
    # Then create dynamic recommendations based on those insights
    current_resources = {"staff_hours": 40, "max_interventions": 10}  # Example resource constraints
    recommendations = await intelligent_report_generator.create_dynamic_recommendations(insights, current_resources)
    
    return recommendations
    
@router.get("/executive-summary")
async def get_executive_summary(
    course_id: str,
    week_number: int,
    db: Session = Depends(get_db)
):
    """
    Get an AI-generated executive summary for a specific course and week
    """
    # First, get the weekly report data
    report = db.query(WeeklyNPSReport).filter(
        WeeklyNPSReport.course_id == course_id,
        WeeklyNPSReport.week_number == week_number
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weekly report for course {course_id}, week {week_number} not found"
        )
    
    # Return the executive summary from the report
    return {
        "executive_summary": report.executive_summary,
        "report_confidence": report.report_confidence,
        "data_quality_score": report.data_quality_score
    }
    
@router.get("/enhanced-rag/similar-patterns")
async def get_similar_emotion_patterns(
    student_id: str,
    course_id: str,
    week_number: int,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """
    Find similar emotion patterns using the enhanced RAG implementation
    """
    try:
        # Get API key from environment
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="GOOGLE_API_KEY environment variable not set"
            )
        
        # Initialize RAG service
        rag_service = EnhancedRAGService(api_key=api_key)
        await rag_service.initialize_vector_stores()
        
        # Get the student's emotion profile from the database
        from ..models.student_journey import StudentJourney
        from ..emotion_analysis.analyzer import EmotionProfile
        
        # Query the database for the student's latest journey entry
        student_journey = db.query(StudentJourney).filter(
            StudentJourney.student_id == student_id,
            StudentJourney.course_id == course_id
        ).order_by(StudentJourney.week_number.desc()).first()
        
        if not student_journey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student journey not found for student {student_id} in course {course_id}"
            )
        
        # Create an EmotionProfile from the StudentJourney data
        emotion_profile = EmotionProfile(
            frustration_level=student_journey.frustration_level or 0.5,
            engagement_level=student_journey.engagement_level or 0.5,
            confidence_level=student_journey.confidence_level or 0.5,
            satisfaction_level=student_journey.satisfaction_level or 0.5,
            frustration_type=student_journey.frustration_type or "mixed",
            frustration_intensity=student_journey.frustration_intensity or "moderate",
            frustration_trend=student_journey.frustration_trend or "stable",
            urgency_level=student_journey.urgency_level or "low",
            urgency_signals=student_journey.urgency_signals or [],
            response_urgency=student_journey.response_urgency or "routine",
            emotional_temperature=student_journey.emotional_temperature or 0.5,
            emotional_volatility=student_journey.emotional_volatility or 0.5,
            emotional_trajectory=student_journey.emotional_trajectory or "neutral",
            hidden_dissatisfaction_flag=student_journey.hidden_dissatisfaction_flag or False,
            hidden_dissatisfaction_confidence=student_journey.hidden_dissatisfaction_confidence or 0.1,
            hidden_signals=student_journey.hidden_signals or [],
            politeness_mask_level=student_journey.politeness_mask_level or 0.3,
            dropout_risk_emotions=student_journey.dropout_risk_emotions or [],
            positive_recovery_indicators=student_journey.positive_recovery_indicators or [],
            emotional_triggers=student_journey.emotional_triggers or [],
            emotion_coherence=student_journey.emotion_coherence or 0.5,
            sentiment_authenticity=student_journey.sentiment_authenticity or 0.5,
            emotional_complexity=student_journey.emotional_complexity or "simple"
        )
        
        # Find similar patterns
        similar_patterns = await rag_service.find_similar_emotion_patterns(
            emotion_profile=emotion_profile,
            k=limit,
            exclude_student_id=student_id
        )
        
        return similar_patterns
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error finding similar patterns: {str(e)}"
        )

@router.get("/enhanced-rag/recommended-interventions")
async def get_recommended_interventions(
    student_id: str,
    course_id: str,
    week_number: int,
    db: Session = Depends(get_db)
):
    """
    Get recommended interventions using the enhanced RAG implementation
    """
    try:
        # Get API key from environment
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="GOOGLE_API_KEY environment variable not set"
            )
        
        # Initialize RAG service
        rag_service = EnhancedRAGService(api_key=api_key)
        await rag_service.initialize_vector_stores()
        
        # Get recommended interventions
        recommendations = await rag_service.get_recommended_interventions(
            student_id=student_id,
            course_id=course_id,
            week_number=week_number
        )
        
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting recommended interventions: {str(e)}"
        )

@router.get("/enhanced-rag/insights")
async def generate_insights_from_patterns(
    student_id: str,
    course_id: str,
    week_number: int,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """
    Generate insights from similar emotion patterns using the enhanced RAG implementation
    """
    try:
        # Get API key from environment
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="GOOGLE_API_KEY environment variable not set"
            )
        
        # Initialize RAG service
        rag_service = EnhancedRAGService(api_key=api_key)
        await rag_service.initialize_vector_stores()
        
        # Get the student's emotion profile from the database
        from ..models.student_journey import StudentJourney
        from ..emotion_analysis.analyzer import EmotionProfile
        
        # Query the database for the student's latest journey entry
        student_journey = db.query(StudentJourney).filter(
            StudentJourney.student_id == student_id,
            StudentJourney.course_id == course_id
        ).order_by(StudentJourney.week_number.desc()).first()
        
        if not student_journey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student journey not found for student {student_id} in course {course_id}"
            )
        
        # Create an EmotionProfile from the StudentJourney data
        emotion_profile = EmotionProfile(
            frustration_level=student_journey.frustration_level or 0.5,
            engagement_level=student_journey.engagement_level or 0.5,
            confidence_level=student_journey.confidence_level or 0.5,
            satisfaction_level=student_journey.satisfaction_level or 0.5,
            frustration_type=student_journey.frustration_type or "mixed",
            frustration_intensity=student_journey.frustration_intensity or "moderate",
            frustration_trend=student_journey.frustration_trend or "stable",
            urgency_level=student_journey.urgency_level or "low",
            urgency_signals=student_journey.urgency_signals or [],
            response_urgency=student_journey.response_urgency or "routine",
            emotional_temperature=student_journey.emotional_temperature or 0.5,
            emotional_volatility=student_journey.emotional_volatility or 0.5,
            emotional_trajectory=student_journey.emotional_trajectory or "neutral",
            hidden_dissatisfaction_flag=student_journey.hidden_dissatisfaction_flag or False,
            hidden_dissatisfaction_confidence=student_journey.hidden_dissatisfaction_confidence or 0.1,
            hidden_signals=student_journey.hidden_signals or [],
            politeness_mask_level=student_journey.politeness_mask_level or 0.3,
            dropout_risk_emotions=student_journey.dropout_risk_emotions or [],
            positive_recovery_indicators=student_journey.positive_recovery_indicators or [],
            emotional_triggers=student_journey.emotional_triggers or [],
            emotion_coherence=student_journey.emotion_coherence or 0.5,
            sentiment_authenticity=student_journey.sentiment_authenticity or 0.5,
            emotional_complexity=student_journey.emotional_complexity or "simple"
        )
        
        # Find similar patterns
        similar_patterns = await rag_service.find_similar_emotion_patterns(
            emotion_profile=emotion_profile,
            k=limit,
            exclude_student_id=student_id
        )
        
        # Generate insights from patterns
        insights = await rag_service.generate_insights_from_patterns(
            similar_patterns=similar_patterns,
            student_id=student_id,
            course_id=course_id,
            week_number=week_number
        )
        
        return {"insights": insights}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating insights: {str(e)}"
        )

@router.get("/enhanced-rag/query")
async def query_rag_system(
    query: str,
    student_id: str,
    course_id: str,
    week_number: int,
    db: Session = Depends(get_db)
):
    """
    Query the RAG system with a specific question about a student
    """
    try:
        # Get API key from environment
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="GOOGLE_API_KEY environment variable not set"
            )
        
        # Initialize RAG service
        rag_service = EnhancedRAGService(api_key=api_key)
        await rag_service.initialize_vector_stores()
        
        # Query the RAG system
        response = await rag_service.query_with_rag(
            query=query,
            student_id=student_id,
            course_id=course_id,
            week_number=week_number
        )
        
        return {"response": response}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying RAG system: {str(e)}"
        )

@router.post("/enhanced-rag/add-emotion-profile")
async def add_emotion_profile(
    student_id: str,
    course_id: str,
    week_number: int,
    emotion_profile: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Add an emotion profile to the RAG system's vector database
    """
    try:
        # Get API key from environment
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="GOOGLE_API_KEY environment variable not set"
            )
        
        # Initialize RAG service
        rag_service = EnhancedRAGService(api_key=api_key)
        await rag_service.initialize_vector_stores()
        
        # Convert dictionary to EmotionProfile object
        from ..models.emotion import EmotionProfile
        profile_obj = EmotionProfile(**emotion_profile)
        
        # Add emotion profile to vector database
        document_id = await rag_service.add_emotion_profile_to_vector_db(
            emotion_profile=profile_obj,
            student_id=student_id,
            course_id=course_id,
            week_number=week_number
        )
        
        return {"status": "success", "document_id": document_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding emotion profile: {str(e)}"
        )
