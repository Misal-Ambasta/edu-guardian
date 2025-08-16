
"""Interventions module for the application.

This module provides functionality related to interventions.
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from ..database.db import get_db
from typing import List, Optional, Dict, Any
from ..models.intervention import Intervention, InterventionCreate, InterventionUpdate, InterventionInDB
from ..services.intervention_tracker import EmotionBasedInterventionTracker
from ..services.async_service import AsyncService, async_to_sync, sync_to_async
from ..services.historical_pattern import HistoricalPatternService
import uuid
import asyncio

router = APIRouter()

@router.get("/", response_model=List[InterventionInDB])
async def get_interventions(
    student_id: Optional[str] = None,
    course_id: Optional[str] = None,
    limit: int = 10,
    with_recommendations: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get interventions with optional filtering and recommendations
    """
    # Create async service
    async_service = AsyncService()

    # Define database query function
    @sync_to_async
    def get_interventions_from_db():
        query = db.query(Intervention)

        if student_id:
            query = query.filter(Intervention.student_id == student_id)

        if course_id:
            query = query.filter(Intervention.course_id == course_id)

        # Apply limit
        query = query.limit(limit)

        return query.all()

    # Get interventions asynchronously
    interventions = await get_interventions_from_db()

    # If recommendations are requested, get them asynchronously
    if with_recommendations and student_id and course_id:
        # Create historical pattern service
        pattern_service = HistoricalPatternService()

        # Get recommendations asynchronously
        recommendations_task = async_service.create_task(
            pattern_service.get_recommended_interventions(
                student_id=student_id,
                course_id=course_id,
                week_number=0  # Default to current week
            )
        )

        # Wait for recommendations
        recommendations = await recommendations_task

        # Add recommendations to response
        for intervention in interventions:
            intervention.recommendations = recommendations

    return interventions

@router.post("/", response_model=InterventionInDB)
async def create_intervention(
    intervention: InterventionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a new intervention record with asynchronous processing
    """
    # Create intervention in database
    db_intervention = Intervention(
        **intervention.dict()
    )

    db.add(db_intervention)
    db.commit()
    db.refresh(db_intervention)

    # Process intervention in background
    background_tasks.add_task(
        process_intervention_async,
        intervention_id=db_intervention.id,
        student_id=db_intervention.student_id,
        course_id=db_intervention.course_id
    )

    return db_intervention


async def process_intervention_async(intervention_id: str, student_id: str, course_id: str):
    """
    Process intervention asynchronously in background
    """
    try:
        # Create services
        pattern_service = HistoricalPatternService()

        # Update historical patterns
        await pattern_service.store_intervention_result(
            Intervention(id=intervention_id, student_id=student_id, course_id=course_id)
        )

        # Log success
        print(f"Successfully processed intervention {intervention_id} in background")
    except Exception as e:
        # Log error
        print(f"Error processing intervention {intervention_id} in background: {e}")


@router.get("/{intervention_id}", response_model=InterventionInDB)
async def get_intervention(
    intervention_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific intervention by ID
    """
    try:
        intervention = db.query(
            Intervention).filter(Intervention.id == uuid.UUID(intervention_id)).first()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid intervention ID format")

    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")

    return intervention

@router.put("/{intervention_id}", response_model=InterventionInDB)
async def update_intervention(
    intervention_id: str,
    intervention_update: InterventionUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an intervention record
    """
    try:
        db_intervention = db.query(
            Intervention).filter(Intervention.id == uuid.UUID(intervention_id)).first()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid intervention ID format")

    if not db_intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")

    # Update fields
    update_data = intervention_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_intervention, key, value)

    db.commit()
    db.refresh(db_intervention)

    return db_intervention

@router.delete("/{intervention_id}")
async def delete_intervention(
    intervention_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete an intervention record
    """
    try:
        db_intervention = db.query(
            Intervention).filter(Intervention.id == uuid.UUID(intervention_id)).first()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid intervention ID format")

    if not db_intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")

    db.delete(db_intervention)
    db.commit()

    return {"status": "success", "message": "Intervention deleted"}

@router.get("/track/{intervention_id}")
async def track_intervention_outcome(
    intervention_id: str,
    student_id: str,
    db: Session = Depends(get_db)
):
    """
    Track the emotional outcome of an intervention
    """
    tracker = EmotionBasedInterventionTracker(db)

    try:
        result = await tracker.track_emotion_intervention_outcome(intervention_id, student_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error tracking intervention outcome: {str(e)}")

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result

@router.get("/templates/performance")
async def get_template_performance(
    template_name: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get performance metrics for intervention templates
    """
    tracker = EmotionBasedInterventionTracker(db)

    try:
        result = await tracker.get_template_performance(template_name, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting template performance: {str(e)}")

    return {"template_performance": result}

@router.get("/timing/analysis")
async def get_intervention_timing_analysis(
    db: Session = Depends(get_db)
):
    """
    Analyze intervention timing and its impact on success
    """
    tracker = EmotionBasedInterventionTracker(db)

    try:
        result = await tracker.get_intervention_timing_analysis()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error analyzing intervention timing: {str(e)}")

    return result
