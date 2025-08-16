from app.models.historical_pattern import HistoricalPattern
"""
Utility functions for common operations.
"""


async def create_historical_pattern(student_id, course_id, week_number, documents, scores):
    """create_historical_pattern extracts common functionality."""

    historical_pattern = HistoricalPattern.from_langchain_documents(
        student_id=student_id,
        course_id=course_id,
        week_number=week_number,
        documents=documents,
        scores=scores
    )
    
    return historical_pattern
