
"""Vector Db Factory module for the application.

This module provides functionality related to vector db factory.
"""
# from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv
from .gemini_vector_db import GeminiVectorDBService

load_dotenv()

class VectorDBFactory:
    """Factory class for creating vector database services"""

    @staticmethod
    def create_vector_db_service() -> GeminiVectorDBService:
        """Create a vector database service

        Returns:
            A GeminiVectorDBService instance

        Raises:
            ValueError: If GOOGLE_API_KEY is not set
            Exception: If there's an error initializing GeminiVectorDBService
        """
        # Check if GOOGLE_API_KEY is set
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY environment variable not set")

        # Initialize GeminiVectorDBService
        return GeminiVectorDBService()
