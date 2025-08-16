
"""Async Service module for the application.

This module provides functionality related to async service.
"""
from typing import List, Dict, Any, Optional, Callable, TypeVar, Generic, Union, Coroutine
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
from functools import partial, wraps

T = TypeVar('T')
R = TypeVar('R')

class AsyncService:
    """Service for handling asynchronous operations"""

    def __init__(self, max_workers: int = 4):
        """Initialize the async service

        Args:
            max_workers: Maximum number of worker threads
        """
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._tasks = set()

    async def run_in_thread(self, func, *args, **kwargs):
        """Run a function in a separate thread

        Args:
            func: Function to run
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            Result of the function
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            partial(func, *args, **kwargs)
        )

    def create_task(self, coro):
        """Create a task and add it to the set of tasks

        Args:
            coro: Coroutine to run

        Returns:
            Task object
        """
        task = asyncio.create_task(coro)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task

    async def gather_with_concurrency(self, n, *coros):
        """Run coroutines with a limit on concurrency

        Args:
            n: Maximum number of coroutines to run concurrently
            *coros: Coroutines to run

        Returns:
            List of results
        """
        semaphore = asyncio.Semaphore(n)

        async def sem_coro(coro):
            async with semaphore:
                return await coro

        return await asyncio.gather(*(sem_coro(c) for c in coros))

    def __del__(self):
        """Clean up resources"""
        self.executor.shutdown(wait=False)


def async_to_sync(func):
    """Decorator to convert an async function to a sync function"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper


def sync_to_async(func):
    """Decorator to convert a sync function to an async function"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, partial(func, *args, **kwargs))
    return wrapper


class AsyncEmotionAnalyzer:
    """Asynchronous wrapper for emotion analyzer"""

    def __init__(self, emotion_analyzer, max_workers: int = 4):
        """Initialize the async emotion analyzer

        Args:
            emotion_analyzer: Emotion analyzer instance
            max_workers: Maximum number of worker threads
        """
        self.emotion_analyzer = emotion_analyzer
        self.async_service = AsyncService(max_workers=max_workers)

    async def analyze_emotions(self, text: str) -> Dict[str, Any]:
        """Analyze emotions in text asynchronously

        Args:
            text: Text to analyze

        Returns:
            Emotion profile
        """
        return await self.async_service.run_in_thread(
            self.emotion_analyzer.analyze_emotions,
            text
        )

    async def analyze_emotions_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze emotions in multiple texts asynchronously

        Args:
            texts: List of texts to analyze

        Returns:
            List of emotion profiles
        """
        tasks = [self.analyze_emotions(text) for text in texts]
        return await self.async_service.gather_with_concurrency(
            self.async_service.max_workers, *tasks)


class AsyncVectorDBService:
    """Asynchronous wrapper for vector database service"""

    def __init__(self, vector_db_service, max_workers: int = 4):
        """Initialize the async vector DB service

        Args:
            vector_db_service: Vector database service instance
            max_workers: Maximum number of worker threads
        """
        self.vector_db_service = vector_db_service
        self.async_service = AsyncService(max_workers=max_workers)

    async def find_similar_emotion_patterns(self, student_id: str, course_id: str,
                                          week_number: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar emotion patterns asynchronously

        Args:
            student_id: Student ID
            course_id: Course ID
            week_number: Week number
            limit: Maximum number of results

        Returns:
            List of similar emotion patterns
        """
        return await self.async_service.run_in_thread(
            self.vector_db_service.find_similar_emotion_patterns,
            student_id=student_id,
            course_id=course_id,
            week_number=week_number,
            limit=limit
        )

    async def find_emotion_similar_students(self, student_id: str, course_id: str,
                                          week_number: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Find students with similar emotions asynchronously

        Args:
            student_id: Student ID
            course_id: Course ID
            week_number: Week number
            limit: Maximum number of results

        Returns:
            List of similar students
        """
        return await self.async_service.run_in_thread(
            self.vector_db_service.find_emotion_similar_students,
            student_id=student_id,
            course_id=course_id,
            week_number=week_number,
            limit=limit
        )

    async def add_emotion_profile(self, student_id: str, course_id: str,
                                week_number: int, emotion_profile: Dict[str, Any],
                                additional_metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add emotion profile to vector database asynchronously

        Args:
            student_id: Student ID
            course_id: Course ID
            week_number: Week number
            emotion_profile: Emotion profile
            additional_metadata: Additional metadata

        Returns:
            Document ID
        """
        return await self.async_service.run_in_thread(
            self.vector_db_service.add_emotion_profile,
            student_id=student_id,
            course_id=course_id,
            week_number=week_number,
            emotion_profile=emotion_profile,
            additional_metadata=additional_metadata
        )
