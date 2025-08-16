
"""Batch Processor module for the application.

This module provides functionality related to batch processor.
"""
from typing import List, Dict, Any, Optional, Callable, TypeVar, Generic, Union
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
from functools import partial

T = TypeVar('T')
R = TypeVar('R')

class BatchProcessor(Generic[T, R]):
    """Service for batch processing heavy computations"""

    def __init__(self,
                 process_func: Callable[[T], R],
                 batch_size: int = 10,
                 max_workers: int = 4,
                 timeout: float = 30.0):
        """Initialize the batch processor

        Args:
            process_func: Function to process each item
            batch_size: Maximum number of items to process in a batch
            max_workers: Maximum number of worker threads
            timeout: Maximum time to wait for batch processing in seconds
        """
        self.process_func = process_func
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.timeout = timeout
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    async def process_batch(self, items: List[T]) -> List[R]:
        """Process a batch of items asynchronously

        Args:
            items: List of items to process

        Returns:
            List of processed results
        """
        if not items:
            return []

        # Split into batches if needed
        if len(items) > self.batch_size:
            results = []
            for i in range(0, len(items), self.batch_size):
                batch = items[i:i + self.batch_size]
                batch_results = await self.process_batch(batch)
                results.extend(batch_results)
            return results

        # Process the batch using thread pool
        loop = asyncio.get_event_loop()
        tasks = []
        for item in items:
            task = loop.run_in_executor(
                self.executor,
                self.process_func,
                item
            )
            tasks.append(task)

        # Wait for all tasks to complete with timeout
        try:
            results = await asyncio.gather(*tasks)
            return results
        except asyncio.TimeoutError:
            print(f"Batch processing timed out after {self.timeout} seconds")
            return [None] * len(items)

    def __del__(self):
        """Clean up resources"""
        self.executor.shutdown(wait=False)


class EmotionBatchProcessor:
    """Batch processor for emotion analysis"""

    def __init__(self, emotion_analyzer, batch_size: int = 10, max_workers: int = 4):
        """Initialize the emotion batch processor

        Args:
            emotion_analyzer: Emotion analyzer instance
            batch_size: Maximum number of items to process in a batch
            max_workers: Maximum number of worker threads
        """
        self.emotion_analyzer = emotion_analyzer
        self.batch_processor = BatchProcessor(
            process_func=self._process_feedback,
            batch_size=batch_size,
            max_workers=max_workers
        )

    def _process_feedback(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single feedback item

        Args:
            feedback: Feedback data

        Returns:
            Processed feedback with emotion analysis
        """
        try:
            # Extract text from feedback
            text = feedback.get("feedback_text", "")

            # Analyze emotions
            emotion_profile = self.emotion_analyzer.analyze_emotions(text)

            # Add emotion profile to feedback
            feedback["emotion_profile"] = emotion_profile.dict()

            return feedback
        except Exception as e:
            print(f"Error processing feedback: {e}")
            return feedback

    async def process_feedbacks(self, feedbacks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a batch of feedbacks

        Args:
            feedbacks: List of feedback data

        Returns:
            List of processed feedbacks with emotion analysis
        """
        return await self.batch_processor.process_batch(feedbacks)


class VectorBatchProcessor:
    """Batch processor for vector embeddings"""

    def __init__(self, vector_db_service, batch_size: int = 10, max_workers: int = 4):
        """Initialize the vector batch processor

        Args:
            vector_db_service: Vector database service instance
            batch_size: Maximum number of items to process in a batch
            max_workers: Maximum number of worker threads
        """
        self.vector_db_service = vector_db_service
        self.batch_processor = BatchProcessor(
            process_func=self._process_emotion_profile,
            batch_size=batch_size,
            max_workers=max_workers
        )

    def _process_emotion_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single emotion profile for vector embedding

        Args:
            data: Emotion profile data with metadata

        Returns:
            Data with document ID
        """
        try:
            # Extract data
            student_id = data.get("student_id")
            course_id = data.get("course_id")
            week_number = data.get("week_number")
            emotion_profile = data.get("emotion_profile")
            metadata = data.get("metadata", {})

            # Add to vector database
            document_id = self.vector_db_service.add_emotion_profile(
                student_id=student_id,
                course_id=course_id,
                week_number=week_number,
                emotion_profile=emotion_profile,
                additional_metadata=metadata
            )

            # Add document ID to data
            data["document_id"] = document_id

            return data
        except Exception as e:
            print(f"Error processing emotion profile: {e}")
            data["error"] = str(e)
            return data

    async def process_emotion_profiles(
        self, profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a batch of emotion profiles

        Args:
            profiles: List of emotion profile data with metadata

        Returns:
            List of processed data with document IDs
        """
        return await self.batch_processor.process_batch(profiles)
