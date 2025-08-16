
"""Students module for the application.

This module provides functionality related to students.
"""
from app.utils.trajectory_utils import get_emotion_trajectory_prediction
from fastapi import APIRouter, Depends, HTTPException, status, Body, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from ..database.db import get_db
from typing import List, Optional, Dict, Any
from ..services.trajectory_predictor import EmotionTrajectoryPredictor
from ..models.student_journey import StudentJourney, StudentJourneyCreate, StudentJourneyInDB
from ..emotion_analysis.analyzer import AdvancedEmotionAnalyzer
from ..data_processing.data_ingestion import CSVDataImporter, BatchProcessor
import uuid
import os
import tempfile
from datetime import datetime

router = APIRouter()

# Initialize the emotion analyzer and data importer
emotion_analyzer = AdvancedEmotionAnalyzer()
csv_data_importer = CSVDataImporter(emotion_analyzer=emotion_analyzer)

@router.get("/")
async def get_students(
    course_id: Optional[str] = None,
    risk_level: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get students with optional filtering
    """
    from ..models.student_journey import StudentJourney
    from sqlalchemy import func, distinct

    # Base query to get distinct student IDs
    query = db.query(distinct(StudentJourney.student_id))

    # Apply filters
    if course_id:
        query = query.filter(StudentJourney.course_id == course_id)

    # Get distinct student IDs
    student_ids = [result[0] for result in query.limit(limit).all()]

    # For each student, get their latest journey entry
    students_data = []
    for student_id in student_ids:
        # Get the latest journey entry for this student
        latest_journey = db.query(StudentJourney).filter(
            StudentJourney.student_id == student_id
        ).order_by(StudentJourney.week_number.desc()).first()

        if latest_journey:
            # Determine risk level based on emotional indicators
            calculated_risk_level = "low"
            if latest_journey.frustration_level and latest_journey.frustration_level > 0.7:
                calculated_risk_level = "high"
            elif latest_journey.frustration_level and latest_journey.frustration_level > 0.5:
                calculated_risk_level = "medium"

            # If risk_level filter is applied, skip students that don't match
            if risk_level and calculated_risk_level != risk_level:
                continue

            # Add student data to results
            students_data.append({
                "id": student_id,
                "course_id": latest_journey.course_id,
                "emotional_temperature": latest_journey.emotional_temperature if latest_journey.emotional_temperature else 0.5,
                "frustration_level": latest_journey.frustration_level if latest_journey.frustration_level else 0.0,
                "risk_level": calculated_risk_level,
                "week_number": latest_journey.week_number,
                "engagement_level": latest_journey.engagement_level if latest_journey.engagement_level else 0.5,
                "hidden_dissatisfaction": latest_journey.hidden_dissatisfaction_flag
            })

    return {"students": students_data}

@router.get("/{student_id}/emotional-journey")
async def get_student_emotional_journey(
    student_id: str,
    course_id: Optional[str] = None,
    start_week: Optional[int] = None,
    end_week: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get a student's emotional journey over time
    """
    from ..models.student_journey import StudentJourney
    from datetime import datetime

    # Build query for student journey entries
    query = db.query(StudentJourney).filter(StudentJourney.student_id == student_id)

    # Apply additional filters
    if course_id:
        query = query.filter(StudentJourney.course_id == course_id)
    if start_week is not None:
        query = query.filter(StudentJourney.week_number >= start_week)
    if end_week is not None:
        query = query.filter(StudentJourney.week_number <= end_week)

    # Get journey entries ordered by week
    journey_entries = query.order_by(StudentJourney.week_number).all()

    if not journey_entries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No emotional journey data found for student {student_id}"
        )

    # Format the emotional journey data
    emotional_journey = []
    for entry in journey_entries:
        journey_point = {
            "week": entry.week_number,
            "timestamp": entry.timestamp.isoformat(
                ) if entry.timestamp else datetime.now().isoformat(),
            "emotional_temperature": entry.emotional_temperature if entry.emotional_temperature is not None else 0.5,
            "emotional_volatility": entry.emotional_volatility if entry.emotional_volatility is not None else 0.0,
            "frustration_level": entry.frustration_level if entry.frustration_level is not None else 0.0,
            "frustration_type": entry.frustration_type,
            "frustration_intensity": entry.frustration_intensity,
            "frustration_trend": entry.frustration_trend,
            "engagement_level": entry.engagement_level if entry.engagement_level is not None else 0.5,
            "confidence_level": entry.confidence_level if entry.confidence_level is not None else 0.5,
            "satisfaction_level": entry.satisfaction_level if entry.satisfaction_level is not None else 0.5,
            "urgency_level": entry.urgency_level,
            "hidden_dissatisfaction": {
                "detected": entry.hidden_dissatisfaction_flag if entry.hidden_dissatisfaction_flag is not None else False,
                "confidence": entry.hidden_dissatisfaction_confidence if entry.hidden_dissatisfaction_confidence is not None else 0.0,
                "signals": entry.hidden_signals if entry.hidden_signals else []
            },
            "emotional_trajectory": entry.emotional_trajectory,
            "nps_score": entry.nps_score,
            "aspect_scores": {
                "lms_usability": entry.lms_usability_score,
                "instructor_quality": entry.instructor_quality_score,
                "content_difficulty": entry.content_difficulty_score,
                "support_quality": entry.support_quality_score,
                "course_pace": entry.course_pace_score
            },
            "comments": entry.comments
        }
        emotional_journey.append(journey_point)

    # Calculate journey metrics
    avg_frustration = sum(
        e.frustration_level or 0 for e in journey_entries) / len(
            journey_entries) if journey_entries else 0
    avg_engagement = sum(
        e.engagement_level or 0 for e in journey_entries) / len(
            journey_entries) if journey_entries else 0
    frustration_trend = \
        "increasing" if len(
            journey_entries) >= 2 and journey_entries[-1].frustration_level > journey_entries[0].frustration_level else "stable"


    return {
        "student_id": student_id,
        "course_id": journey_entries[0].course_id if journey_entries else None,
        "weeks_tracked": len(journey_entries),
        "emotional_journey": emotional_journey,
        "journey_metrics": {
            "average_frustration": avg_frustration,
            "average_engagement": avg_engagement,
            "frustration_trend": frustration_trend,
            "hidden_dissatisfaction_detected": any(
                e.hidden_dissatisfaction_flag for e in journey_entries if e.hidden_dissatisfaction_flag)
        }
    }

@router.get("/{student_id}/emotion-trajectory")
async def get_student_emotion_trajectory(
    student_id: str,
    course_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a student's predicted emotion trajectory
    """
    try:
        prediction = await get_emotion_trajectory_prediction(student_id=student_id, course_id=course_id, db=db)

        return {
            "student_id": student_id,
            "course_id": course_id,
            "emotion_trajectory": prediction
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error predicting emotion trajectory: {str(e)}"
        )

@router.get("/{student_id}/risk-assessment")
async def get_student_risk_assessment(
    student_id: str,
    course_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a comprehensive risk assessment for a student
    """
    try:
        prediction = await get_emotion_trajectory_prediction(student_id=student_id, course_id=course_id, db=db)

        # Extract risk-related information
        risk_assessment = {
            "risk_escalations": prediction.risk_escalations,
            "confidence_scores": prediction.confidence_scores,
            "optimal_intervention_windows": prediction.optimal_intervention_windows
        }

        return {
            "student_id": student_id,
            "course_id": course_id,
            "risk_assessment": risk_assessment
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating risk assessment: {str(e)}"
        )

@router.post("/{student_id}/journey")
async def create_student_journey_entry(
    student_id: str,
    journey_data: StudentJourneyCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new student journey entry with emotional analysis
    """
    # Ensure student_id in path matches the one in the request body
    if journey_data.student_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student ID in path must match student ID in request body"
        )

    # Check if there's already an entry for this student, course, and week
    existing_entry = db.query(StudentJourney).filter(
        StudentJourney.student_id == student_id,
        StudentJourney.course_id == journey_data.course_id,
        StudentJourney.week_number == journey_data.week_number
    ).first()

    if existing_entry:
        # Update existing entry
        for key, value in journey_data.model_dump(exclude_unset=True).items():
            if hasattr(existing_entry, key):
                setattr(existing_entry, key, value)

        # If comments are provided, analyze emotions
        if journey_data.comments:
            emotion_profile = emotion_analyzer.analyze_text(journey_data.comments)

            # Update emotion fields
            existing_entry.frustration_level = emotion_profile.frustration_level
            existing_entry.engagement_level = emotion_profile.engagement_level
            existing_entry.confidence_level = emotion_profile.confidence_level
            existing_entry.satisfaction_level = emotion_profile.satisfaction_level
            existing_entry.frustration_type = emotion_profile.frustration_type
            existing_entry.frustration_intensity = emotion_profile.frustration_intensity
            existing_entry.frustration_trend = emotion_profile.frustration_trend
            existing_entry.urgency_level = emotion_profile.urgency_level
            existing_entry.urgency_signals = emotion_profile.urgency_signals
            existing_entry.response_urgency = emotion_profile.response_urgency
            existing_entry.emotional_temperature = emotion_profile.emotional_temperature
            existing_entry.emotional_volatility = emotion_profile.emotional_volatility
            existing_entry.emotional_trajectory = emotion_profile.emotional_trajectory
            existing_entry.hidden_dissatisfaction_flag = emotion_profile.hidden_dissatisfaction_flag
            existing_entry.hidden_dissatisfaction_confidence = emotion_profile.hidden_dissatisfaction_confidence
            existing_entry.hidden_signals = emotion_profile.hidden_signals
            existing_entry.politeness_mask_level = emotion_profile.politeness_mask_level
            existing_entry.dropout_risk_emotions = emotion_profile.dropout_risk_emotions
            existing_entry.positive_recovery_indicators = emotion_profile.positive_recovery_indicators
            existing_entry.emotional_triggers = emotion_profile.emotional_triggers
            existing_entry.emotion_coherence = emotion_profile.emotion_coherence
            existing_entry.sentiment_authenticity = emotion_profile.sentiment_authenticity
            existing_entry.emotional_complexity = emotion_profile.emotional_complexity

        db.commit()
        db.refresh(existing_entry)
        return StudentJourneyInDB.model_validate(existing_entry)
    else:
        # Create new entry
        new_journey = StudentJourney(
            id=uuid.uuid4(),
            student_id=student_id,
            course_id=journey_data.course_id,
            week_number=journey_data.week_number,
            nps_score=journey_data.nps_score,
            lms_usability_score=journey_data.lms_usability_score,
            instructor_quality_score=journey_data.instructor_quality_score,
            content_difficulty_score=journey_data.content_difficulty_score,
            support_quality_score=journey_data.support_quality_score,
            course_pace_score=journey_data.course_pace_score,
            comments=journey_data.comments,
            timestamp=datetime.now()
        )

        # If comments are provided, analyze emotions
        if journey_data.comments:
            emotion_profile = emotion_analyzer.analyze_text(journey_data.comments)

            # Set emotion fields
            new_journey.frustration_level = emotion_profile.frustration_level
            new_journey.engagement_level = emotion_profile.engagement_level
            new_journey.confidence_level = emotion_profile.confidence_level
            new_journey.satisfaction_level = emotion_profile.satisfaction_level
            new_journey.frustration_type = emotion_profile.frustration_type
            new_journey.frustration_intensity = emotion_profile.frustration_intensity
            new_journey.frustration_trend = emotion_profile.frustration_trend
            new_journey.urgency_level = emotion_profile.urgency_level
            new_journey.urgency_signals = emotion_profile.urgency_signals
            new_journey.response_urgency = emotion_profile.response_urgency
            new_journey.emotional_temperature = emotion_profile.emotional_temperature
            new_journey.emotional_volatility = emotion_profile.emotional_volatility
            new_journey.emotional_trajectory = emotion_profile.emotional_trajectory
            new_journey.hidden_dissatisfaction_flag = emotion_profile.hidden_dissatisfaction_flag
            new_journey.hidden_dissatisfaction_confidence = emotion_profile.hidden_dissatisfaction_confidence
            new_journey.hidden_signals = emotion_profile.hidden_signals
            new_journey.politeness_mask_level = emotion_profile.politeness_mask_level
            new_journey.dropout_risk_emotions = emotion_profile.dropout_risk_emotions
            new_journey.positive_recovery_indicators = emotion_profile.positive_recovery_indicators
            new_journey.emotional_triggers = emotion_profile.emotional_triggers
            new_journey.emotion_coherence = emotion_profile.emotion_coherence
            new_journey.sentiment_authenticity = emotion_profile.sentiment_authenticity
            new_journey.emotional_complexity = emotion_profile.emotional_complexity

        db.add(new_journey)
        db.commit()
        db.refresh(new_journey)
        return StudentJourneyInDB.model_validate(new_journey)

@router.post("/batch-journey")
async def create_batch_student_journey_entries(
    journey_data_list: List[StudentJourneyCreate] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Create or update multiple student journey entries with emotional analysis in batch
    """
    results = []

    for journey_data in journey_data_list:
        try:
            # Check if there's already an entry for this student, course, and week
            existing_entry = db.query(StudentJourney).filter(
                StudentJourney.student_id == journey_data.student_id,
                StudentJourney.course_id == journey_data.course_id,
                StudentJourney.week_number == journey_data.week_number
            ).first()

            if existing_entry:
                # Update existing entry
                for key, value in journey_data.model_dump(exclude_unset=True).items():
                    if hasattr(existing_entry, key):
                        setattr(existing_entry, key, value)

                # If comments are provided, analyze emotions
                if journey_data.comments:
                    emotion_profile = emotion_analyzer.analyze_text(journey_data.comments)

                    # Update emotion fields
                    existing_entry.frustration_level = emotion_profile.frustration_level
                    existing_entry.engagement_level = emotion_profile.engagement_level
                    existing_entry.confidence_level = emotion_profile.confidence_level
                    existing_entry.satisfaction_level = emotion_profile.satisfaction_level
                    existing_entry.frustration_type = emotion_profile.frustration_type
                    existing_entry.frustration_intensity = emotion_profile.frustration_intensity
                    existing_entry.frustration_trend = emotion_profile.frustration_trend
                    existing_entry.urgency_level = emotion_profile.urgency_level
                    existing_entry.urgency_signals = emotion_profile.urgency_signals
                    existing_entry.response_urgency = emotion_profile.response_urgency
                    existing_entry.emotional_temperature = emotion_profile.emotional_temperature
                    existing_entry.emotional_volatility = emotion_profile.emotional_volatility
                    existing_entry.emotional_trajectory = emotion_profile.emotional_trajectory
                    existing_entry.hidden_dissatisfaction_flag = emotion_profile.hidden_dissatisfaction_flag
                    existing_entry.hidden_dissatisfaction_confidence = emotion_profile.hidden_dissatisfaction_confidence
                    existing_entry.hidden_signals = emotion_profile.hidden_signals
                    existing_entry.politeness_mask_level = emotion_profile.politeness_mask_level
                    existing_entry.dropout_risk_emotions = emotion_profile.dropout_risk_emotions
                    existing_entry.positive_recovery_indicators = emotion_profile.positive_recovery_indicators
                    existing_entry.emotional_triggers = emotion_profile.emotional_triggers
                    existing_entry.emotion_coherence = emotion_profile.emotion_coherence
                    existing_entry.sentiment_authenticity = emotion_profile.sentiment_authenticity
                    existing_entry.emotional_complexity = emotion_profile.emotional_complexity

                results.append({
                    "student_id": journey_data.student_id,
                    "course_id": journey_data.course_id,
                    "week_number": journey_data.week_number,
                    "status": "updated"
                })
            else:
                # Create new entry
                new_journey = StudentJourney(
                    id=uuid.uuid4(),
                    student_id=journey_data.student_id,
                    course_id=journey_data.course_id,
                    week_number=journey_data.week_number,
                    nps_score=journey_data.nps_score,
                    lms_usability_score=journey_data.lms_usability_score,
                    instructor_quality_score=journey_data.instructor_quality_score,
                    content_difficulty_score=journey_data.content_difficulty_score,
                    support_quality_score=journey_data.support_quality_score,
                    course_pace_score=journey_data.course_pace_score,
                    comments=journey_data.comments,
                    timestamp=datetime.now()
                )

                # If comments are provided, analyze emotions
                if journey_data.comments:
                    emotion_profile = emotion_analyzer.analyze_text(journey_data.comments)

                    # Set emotion fields
                    new_journey.frustration_level = emotion_profile.frustration_level
                    new_journey.engagement_level = emotion_profile.engagement_level
                    new_journey.confidence_level = emotion_profile.confidence_level
                    new_journey.satisfaction_level = emotion_profile.satisfaction_level
                    new_journey.frustration_type = emotion_profile.frustration_type
                    new_journey.frustration_intensity = emotion_profile.frustration_intensity
                    new_journey.frustration_trend = emotion_profile.frustration_trend
                    new_journey.urgency_level = emotion_profile.urgency_level
                    new_journey.urgency_signals = emotion_profile.urgency_signals
                    new_journey.response_urgency = emotion_profile.response_urgency
                    new_journey.emotional_temperature = emotion_profile.emotional_temperature
                    new_journey.emotional_volatility = emotion_profile.emotional_volatility
                    new_journey.emotional_trajectory = emotion_profile.emotional_trajectory
                    new_journey.hidden_dissatisfaction_flag = emotion_profile.hidden_dissatisfaction_flag
                    new_journey.hidden_dissatisfaction_confidence = emotion_profile.hidden_dissatisfaction_confidence
                    new_journey.hidden_signals = emotion_profile.hidden_signals
                    new_journey.politeness_mask_level = emotion_profile.politeness_mask_level
                    new_journey.dropout_risk_emotions = emotion_profile.dropout_risk_emotions
                    new_journey.positive_recovery_indicators = emotion_profile.positive_recovery_indicators
                    new_journey.emotional_triggers = emotion_profile.emotional_triggers
                    new_journey.emotion_coherence = emotion_profile.emotion_coherence
                    new_journey.sentiment_authenticity = emotion_profile.sentiment_authenticity
                    new_journey.emotional_complexity = emotion_profile.emotional_complexity

                db.add(new_journey)
                results.append({
                    "student_id": journey_data.student_id,
                    "course_id": journey_data.course_id,
                    "week_number": journey_data.week_number,
                    "status": "created"
                })
        except Exception as e:
            results.append({
                "student_id": journey_data.student_id if hasattr(
                    journey_data, "student_id") else "unknown",
                "course_id": journey_data.course_id if hasattr(
                    journey_data, "course_id") else "unknown",
                "week_number": journey_data.week_number if hasattr(
                    journey_data, "week_number") else "unknown",
                "status": "error",
                "error": str(e)
            })

    db.commit()
    return {"results": results}

@router.post("/upload-csv")
async def upload_csv_data(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process a CSV file containing student journey data
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )

    # Create a temporary file to store the uploaded content
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
    temp_file_path = temp_file.name

    try:
        # Write the uploaded file content to the temporary file
        content = await file.read()
        with open(temp_file_path, 'wb') as f:
            f.write(content)

        # Process the CSV file
        student_journeys, quality_metrics = csv_data_importer.import_csv(temp_file_path)

        # Save the processed data to the database
        results = []
        for journey in student_journeys:
            try:
                # Check if there's already an entry for this student, course, and week
                existing_entry = db.query(StudentJourney).filter(
                    StudentJourney.student_id == journey.student_id,
                    StudentJourney.course_id == journey.course_id,
                    StudentJourney.week_number == journey.week_number
                ).first()

                if existing_entry:
                    # Update existing entry
                    for key, value in journey.model_dump(exclude_unset=True).items():
                        if hasattr(existing_entry, key):
                            setattr(existing_entry, key, value)

                    results.append({
                        "student_id": journey.student_id,
                        "course_id": journey.course_id,
                        "week_number": journey.week_number,
                        "status": "updated"
                    })
                else:
                    # Create new entry
                    new_journey = StudentJourney(
                        id=uuid.uuid4(),
                        **journey.model_dump()
                    )

                    db.add(new_journey)
                    results.append({
                        "student_id": journey.student_id,
                        "course_id": journey.course_id,
                        "week_number": journey.week_number,
                        "status": "created"
                    })
            except Exception as e:
                results.append({
                    "student_id": journey.student_id if hasattr(
                        journey, "student_id") else "unknown",
                    "course_id": journey.course_id if hasattr(journey, "course_id") else "unknown",
                    "week_number": journey.week_number if hasattr(
                        journey, "week_number") else "unknown",
                    "status": "error",
                    "error": str(e)
                })

        db.commit()

        # Clean up the temporary file in the background
        background_tasks.add_task(os.unlink, temp_file_path)

        return {
            "filename": file.filename,
            "rows_processed": quality_metrics.total_rows,
            "valid_rows": quality_metrics.valid_rows,
            "invalid_rows": quality_metrics.invalid_rows,
            "results": results,
            "quality_metrics": quality_metrics.dict()
        }

    except Exception as e:
        # Clean up the temporary file
        background_tasks.add_task(os.unlink, temp_file_path)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing CSV file: {str(e)}"
        )

@router.post("/upload-batch")
async def upload_batch_directory(
    directory_path: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
    Process all CSV files in a specified directory
    """
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Directory not found: {directory_path}"
        )

    try:
        # Initialize batch processor
        batch_processor = BatchProcessor(importer=csv_data_importer, db=db)

        # Process the directory
        results = await batch_processor.process_directory(directory_path)

        return {
            "directory": directory_path,
            "files_processed": results["files_processed"],
            "total_rows": results["total_rows"],
            "valid_rows": results["valid_rows"],
            "invalid_rows": results["invalid_rows"],
            "quality_metrics": results["quality_metrics"],
            "errors": results["errors"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing directory: {str(e)}"
        )
