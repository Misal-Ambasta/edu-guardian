from app.services.trajectory_predictor import EmotionTrajectoryPredictor
from sqlalchemy.orm import Session
"""
Utility functions for common operations.
"""


async def get_emotion_trajectory_prediction(student_id, course_id, db):
    """get_emotion_trajectory_prediction extracts common functionality."""

    # Initialize the trajectory predictor with the database session
    trajectory_predictor = EmotionTrajectoryPredictor(db)

    # Get the student's emotion history
    emotion_history = await trajectory_predictor.get_student_emotion_history(
        student_id, course_id)

    # Predict emotion evolution
    prediction = await trajectory_predictor.predict_emotion_evolution(emotion_history)
    
    return prediction
