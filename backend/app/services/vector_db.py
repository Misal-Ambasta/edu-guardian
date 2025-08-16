
"""Vector Db module for the application.

This module provides functionality related to vector db.
"""
from typing import List, Dict, Any, Optional, Tuple
import os
import json
from pydantic import BaseModel
from dotenv import load_dotenv

import numpy as np
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings

from ..emotion_analysis.analyzer import EmotionProfile
load_dotenv()

class EmotionVector(BaseModel):
    """Model for emotion vector embeddings"""
    student_id: str
    course_id: str
    week_number: int
    emotion_vector: List[float]
    emotion_profile: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

class EmotionEmbeddings(Embeddings):
    """Custom embeddings class for emotion profiles that implements LangChain's Embeddings interface"""

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed documents using emotion profile data"""
        # This method would normally convert texts to embeddings
        # In our case, we'll parse the JSON strings back to emotion profiles and generate embeddings
        embeddings = []
        for text in texts:
            try:
                emotion_profile = EmotionProfile.parse_raw(text)
                vector = self._generate_emotion_embedding(emotion_profile)
                embeddings.append(vector)
            except Exception as e:
                # Fallback to a zero vector if parsing fails
                print(f"Error embedding document: {e}")
                embeddings.append([0.0] * 18)  # Same dimension as our emotion vectors
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Embed query text"""
        # For queries, we'll try to parse as emotion profile or use a simpler approach
        try:
            emotion_profile = EmotionProfile.parse_raw(text)
            return self._generate_emotion_embedding(emotion_profile)
        except Exception:
            # If the query isn't a valid emotion profile JSON, create a simple embedding
            # This is a simplified approach - in production you might want more sophisticated parsing
            return [0.5] * 18  # Default vector

    def _generate_emotion_embedding(self, emotion_profile: EmotionProfile) -> List[float]:
        """Generate a vector embedding from an emotion profile"""
        # Extract numerical values from emotion profile
        vector_components = [
            # Primary emotions (0-1 scale)
            emotion_profile.frustration_level,
            emotion_profile.engagement_level,
            emotion_profile.confidence_level,
            emotion_profile.satisfaction_level,

            # Emotional temperature and volatility
            emotion_profile.emotional_temperature,
            emotion_profile.emotional_volatility,

            # Hidden dissatisfaction
            float(emotion_profile.hidden_dissatisfaction_flag),
            emotion_profile.hidden_dissatisfaction_confidence or 0.0,
            emotion_profile.politeness_mask_level or 0.0,

            # Convert categorical values to numerical
            self._encode_frustration_type(emotion_profile.frustration_type),
            self._encode_frustration_intensity(emotion_profile.frustration_intensity),
            self._encode_frustration_trend(emotion_profile.frustration_trend),
            self._encode_urgency_level(emotion_profile.urgency_level),
            self._encode_response_urgency(emotion_profile.response_urgency),
            self._encode_emotional_trajectory(emotion_profile.emotional_trajectory),

            # Meta-emotional analysis
            emotion_profile.emotion_coherence or 0.5,
            emotion_profile.sentiment_authenticity or 0.5,
            self._encode_emotional_complexity(emotion_profile.emotional_complexity)
        ]

        # Normalize vector to unit length
        vector = np.array(vector_components, dtype=np.float32)
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector.tolist()

    # These encoding methods are now in the EmotionEmbeddings class

class VectorDBService:
    """Service for handling emotion vector embeddings and pattern matching using LangChain"""

    def __init__(self):
        # Initialize the custom embeddings model
        self.embedding_function = EmotionEmbeddings()

        # Set up ChromaDB collections using LangChain's Chroma integration
        self.emotion_patterns = Chroma(
            collection_name="emotion_patterns",
            embedding_function=self.embedding_function,
            persist_directory=os.getenv("CHROMA_DB_PATH", "./chromadb")
        )

        self.interventions = Chroma(
            collection_name="historical_interventions",
            embedding_function=self.embedding_function,
            persist_directory=os.getenv("CHROMA_DB_PATH", "./chromadb")
        )

    def generate_emotion_embedding(self, emotion_profile: EmotionProfile) -> List[float]:
        """Generate a vector embedding from an emotion profile"""
        # Use the embedding function from our custom embeddings class
        return self.embedding_function._generate_emotion_embedding(emotion_profile)

    def store_emotion_pattern(self, student_id: str, course_id: str, week_number: int,
                             emotion_profile: EmotionProfile, additional_metadata: Dict[str, Any] = None) -> str:
        """Store an emotion pattern in the vector database"""
        # Prepare metadata
        metadata = {
            "student_id": student_id,
            "course_id": course_id,
            "week_number": week_number,
            **additional_metadata or {}
        }

        # Create a unique ID
        document_id = f"{student_id}_{course_id}_{week_number}"

        # Convert emotion profile to JSON string for storage
        emotion_json = json.dumps(emotion_profile.dict())

        # Store using LangChain's Chroma integration
        from langchain_core.documents import Document

        document = Document(
            page_content=emotion_json,
            metadata=metadata,
            id=document_id
        )

        self.emotion_patterns.add_documents([document], ids=[document_id])

        return document_id

    def find_similar_emotion_patterns(self, emotion_profile: EmotionProfile,
                                     limit: int = 10, metadata_filter: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Find similar emotion patterns in the database"""
        # Convert emotion profile to JSON for query
        query_text = json.dumps(emotion_profile.dict())

        # Prepare filter if metadata filter is provided
        filter_dict = metadata_filter or {}

        # Query the database using LangChain's similarity_search_with_score
        results = self.emotion_patterns.similarity_search_with_score(
            query=query_text,
            k=limit,
            filter=filter_dict if filter_dict else None
        )

        # Process and return results
        similar_patterns = []
        for doc, score in results:
            try:
                emotion_data = json.loads(doc.page_content)
                similar_patterns.append({
                    "id": doc.metadata.get("id") or doc.id,
                    "emotion_profile": emotion_data,
                    "metadata": doc.metadata,
                    "distance": score
                })
            except Exception as e:
                print(f"Error processing document: {e}")

        return similar_patterns

    def find_emotion_similar_students(self, student_id: str, course_id: str, week_number: int,
                                    limit: int = 10) -> Dict[str, Any]:
        """Find students with similar emotion patterns"""
        # Get the student's emotion profile using LangChain's filter capability
        document_id = f"{student_id}_{course_id}_{week_number}"

        # Try to retrieve by ID first
        try:
            results = self.emotion_patterns.get(ids=[document_id])
            if not results:
                # If not found by ID, try filtering
                filter_dict = {
                    "student_id": student_id,
                    "course_id": course_id,
                    "week_number": week_number
                }
                results = self.emotion_patterns.similarity_search(
                    query="",  # Empty query to get exact matches by filter
                    k=1,
                    filter=filter_dict
                )
        except Exception:
            # Fallback to similarity search with filter
            filter_dict = {
                "student_id": student_id,
                "course_id": course_id,
                "week_number": week_number
            }
            results = self.emotion_patterns.similarity_search(
                query="",  # Empty query to get exact matches by filter
                k=1,
                filter=filter_dict
            )

        if not results:
            return {"error": "Student emotion profile not found"}

        # Parse the emotion profile from the first result
        if hasattr(results[0], 'page_content'):
            # If results is a list of Documents
            emotion_profile = EmotionProfile.parse_raw(results[0].page_content)
        else:
            # If results is from get() method
            emotion_profile = EmotionProfile.parse_raw(results[0])

        # Find similar students, excluding the query student
        similar_students = self.find_similar_emotion_patterns(
            emotion_profile=emotion_profile,
            limit=limit+1,  # +1 to account for the query student
            metadata_filter={"course_id": course_id}
        )

        # Remove the query student from results if present
        similar_students = [s for s in similar_students if s["metadata"].get(
            "student_id") != student_id]

        # Limit to requested number
        similar_students = similar_students[:limit]

        # Get successful interventions for these similar students
        successful_interventions = self._get_successful_interventions_for_similar_students(
            [s["metadata"]["student_id"] for s in similar_students]
        )

        # Calculate emotion recovery probability
        emotion_recovery_probability = self._calculate_emotion_recovery_rate(similar_students)

        # Find optimal intervention windows
        optimal_intervention_windows = self._find_best_intervention_windows(similar_students)

        return {
            "emotion_matched_students": similar_students,
            "successful_emotion_interventions": successful_interventions,
            "emotion_recovery_probability": emotion_recovery_probability,
            "optimal_emotion_intervention_timing": optimal_intervention_windows
        }

    def _get_successful_interventions_for_similar_students(
        self, student_ids: List[str]) -> List[Dict[str, Any]]:
        """Get successful interventions for similar students"""
        # This would query the interventions collection or database
        # For now, return a placeholder
        return []

    def _calculate_emotion_recovery_rate(self, similar_students: List[Dict[str, Any]]) -> float:
        """Calculate the emotion recovery rate based on similar students"""
        # This would analyze the emotion trajectories of similar students
        # For now, return a placeholder
        return 0.75  # 75% recovery rate

    def _find_best_intervention_windows(
        self, similar_students: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find the best intervention windows based on similar students"""
        # This would analyze when interventions were most successful
        # For now, return a placeholder
        return {
            "optimal_day": "Tuesday",
            "optimal_week_point": "Early in week",
            "response_time_window": "24 hours"
        }

    # Helper methods for encoding categorical values
    def _encode_frustration_type(self, frustration_type: Optional[str]) -> float:
        mapping = {
            "technical": 0.2,
            "content": 0.4,
            "pace": 0.6,
            "support": 0.8,
            "mixed": 1.0,
            None: 0.0
        }
        return mapping.get(frustration_type, 0.0)

    def _encode_frustration_intensity(self, intensity: Optional[str]) -> float:
        mapping = {
            "mild": 0.25,
            "moderate": 0.5,
            "severe": 0.75,
            "critical": 1.0,
            None: 0.0
        }
        return mapping.get(intensity, 0.0)

    def _encode_frustration_trend(self, trend: Optional[str]) -> float:
        mapping = {
            "decreasing": 0.25,
            "stable": 0.5,
            "increasing": 0.75,
            "spiking": 1.0,
            None: 0.5  # Default to stable
        }
        return mapping.get(trend, 0.5)

    def _encode_urgency_level(self, urgency: Optional[str]) -> float:
        mapping = {
            "low": 0.2,
            "medium": 0.4,
            "high": 0.6,
            "critical": 0.8,
            "immediate": 1.0,
            None: 0.0
        }
        return mapping.get(urgency, 0.0)

    def _encode_response_urgency(self, response: Optional[str]) -> float:
        mapping = {
            "routine": 0.25,
            "within_week": 0.5,
            "same_day": 0.75,
            "within_hour": 1.0,
            None: 0.25  # Default to routine
        }
        return mapping.get(response, 0.25)

    def _encode_emotional_trajectory(self, trajectory: Optional[str]) -> float:
        mapping = {
            "declining": 0.25,
            "fluctuating": 0.5,
            "neutral": 0.6,
            "improving": 1.0,
            None: 0.6  # Default to neutral
        }
        return mapping.get(trajectory, 0.6)

    def _encode_emotional_complexity(self, complexity: Optional[str]) -> float:
        mapping = {
            "simple": 0.25,
            "mixed": 0.5,
            "complex": 0.75,
            "conflicted": 1.0,
            None: 0.5  # Default to mixed
        }
        return mapping.get(complexity, 0.5)

# Add alias for backward compatibility
EmotionVectorDatabase = VectorDBService
