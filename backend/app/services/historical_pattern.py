
"""Historical Pattern module for the application.

This module provides functionality related to historical pattern.
"""
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel
from datetime import datetime
import json
import asyncio

from langchain_core.documents import Document

from ..emotion_analysis.analyzer import EmotionProfile
from .vector_db_factory import VectorDBFactory
from .cache_service import cached, invalidate_cache
from ..models.historical_pattern import HistoricalPattern, EmotionPatternMatch
from ..models.student_journey import StudentJourney
from ..models.intervention import Intervention
class HistoricalPatternService:
    """Service for finding historical patterns in student emotion data"""

    def __init__(self):
        self.vector_db = VectorDBFactory.create_vector_db_service()

    @cached(ttl=3600, key_prefix="emotion_patterns")
    async def find_emotion_patterns(self, student_id: str, course_id: str,
                                  week_number: int, similar_patterns: Optional[List[Dict[str, Any]]] = None) -> HistoricalPattern:
        """Find historical emotion patterns for a student using LangChain with caching"""
        # Get similar students with matching emotion patterns if not provided
        if not similar_patterns:
            result = self.vector_db.find_emotion_similar_students(
                student_id=student_id,
                course_id=course_id,
                week_number=week_number,
                limit=5
            )

            if "error" in result:
                # Return empty pattern if student not found
                return HistoricalPattern(
                    student_id=student_id,
                    course_id=course_id,
                    week_number=week_number
                )

            similar_patterns = result

        # Convert the results to LangChain Documents and then to EmotionPatternMatch objects
        documents = []
        scores = []

        for pattern in similar_patterns:
            try:
                # Create a Document from the pattern
                if isinstance(pattern["emotion_profile"], str):
                    # If it's already a JSON string
                    content = pattern["emotion_profile"]
                else:
                    # If it's a dict, convert to JSON string
                    content = json.dumps(pattern["emotion_profile"])

                doc = Document(
                    page_content=content,
                    metadata=pattern["metadata"]
                )
                documents.append(doc)
                scores.append(pattern["distance"] if pattern.get("distance") is not None else 0.5)
            except Exception as e:
                print(f"Error creating document from pattern: {e}")

        # Create a HistoricalPattern from the documents
        historical_pattern = HistoricalPattern.from_langchain_documents(
            student_id=student_id,
            course_id=course_id,
            week_number=week_number,
            documents=documents,
            scores=scores
        )

        # Add additional information if available
        if isinstance(similar_patterns, dict):
            historical_pattern.successful_interventions = similar_patterns.get(
                "successful_emotion_interventions", [])
            historical_pattern.emotion_recovery_probability = similar_patterns.get(
                "emotion_recovery_probability", 0.0)
            historical_pattern.optimal_intervention_timing = similar_patterns.get(
                "optimal_emotion_intervention_timing", {})

        return historical_pattern

    @invalidate_cache(key_pattern="emotion_patterns:*")
    async def store_student_emotion_vector(self, student_journey: StudentJourney) -> str:
        """Store a student's emotion vector in the database using LangChain and invalidate cache"""
        # Extract the emotion profile from the student journey
        emotion_profile = student_journey.emotion_profile

        # Additional metadata to store
        additional_metadata = {
            "timestamp": student_journey.timestamp.isoformat(),
            "feedback_id": student_journey.feedback_id,
            "course_name": student_journey.course_name,
            "instructor": student_journey.instructor
        }

        # Create a LangChain Document
        document_id = f"{student_journey.student_id}_{student_journey.course_id}_{student_journey.week_number}"

        # Convert emotion profile to JSON string
        emotion_json = json.dumps(emotion_profile.dict())

        # Create the Document
        document = Document(
            page_content=emotion_json,
            metadata=additional_metadata,
            id=document_id
        )

        # Store the emotion pattern using the vector DB service
        document_id = self.vector_db.store_emotion_pattern(
            student_id=student_journey.student_id,
            course_id=student_journey.course_id,
            week_number=student_journey.week_number,
            emotion_profile=emotion_profile,
            additional_metadata=additional_metadata
        )

        return document_id

    @invalidate_cache(key_pattern="emotion_patterns:*")
    async def store_student_emotion_vectors_batch(
        self, student_journeys: List[StudentJourney]) -> List[str]:
        """Store multiple student emotion vectors in batch for improved performance"""
        from .batch_processor import VectorBatchProcessor

        # Create batch processor
        batch_processor = VectorBatchProcessor(
            vector_db_service=self.vector_db,
            batch_size=10,
            max_workers=4
        )

        # Prepare data for batch processing
        batch_data = []
        for journey in student_journeys:
            # Extract data from student journey
            batch_data.append({
                "student_id": journey.student_id,
                "course_id": journey.course_id,
                "week_number": journey.week_number,
                "emotion_profile": journey.emotion_profile,
                "metadata": {
                    "timestamp": journey.timestamp.isoformat(),
                    "feedback_id": journey.feedback_id,
                    "course_name": journey.course_name,
                    "instructor": journey.instructor
                }
            })

        # Process batch
        results = await batch_processor.process_emotion_profiles(batch_data)

        # Extract document IDs
        document_ids = [result.get("document_id") for result in results if "document_id" in result]

        return document_ids

    async def store_intervention_result(self, intervention: Intervention) -> None:
        """Store the result of an intervention in the database"""
        # This would store the intervention in the historical_interventions collection
        # Implementation would depend on the structure of the Intervention model
        # For now, this is a placeholder
        pass

    async def get_recommended_interventions(self, student_id: str, course_id: str,
                                          week_number: int, similar_patterns: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Get recommended interventions based on historical patterns using LangChain"""
        # Find historical patterns
        historical_pattern = await self.find_emotion_patterns(
            student_id=student_id,
            course_id=course_id,
            week_number=week_number,
            similar_patterns=similar_patterns
        )

        # Extract successful interventions from similar students
        recommended_interventions = historical_pattern.successful_interventions

        # Sort by success rate
        recommended_interventions.sort(key=lambda x: x.get("success_rate", 0), reverse=True)

        return recommended_interventions

    async def get_recommended_interventions_batch(
        self, student_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Get recommended interventions for multiple students in batch

        Args:
            student_data: List of dictionaries with student_id, course_id, and week_number

        Returns:
            Dictionary mapping student IDs to their recommended interventions
        """
        from .batch_processor import BatchProcessor

        # Create a processor function
        async def process_student(data):
            student_id = data["student_id"]
            course_id = data["course_id"]
            week_number = data["week_number"]

            interventions = await self.get_recommended_interventions(
                student_id=student_id,
                course_id=course_id,
                week_number=week_number
            )

            return {
                "student_id": student_id,
                "interventions": interventions
            }

        # Create batch processor
        batch_processor = BatchProcessor(
            process_func=lambda data: asyncio.run(process_student(data)),
            batch_size=10,
            max_workers=4
        )

        # Process batch
        results = await batch_processor.process_batch(student_data)

        # Convert to dictionary mapping student IDs to interventions
        interventions_by_student = {}
        for result in results:
            if result and "student_id" in result:
                interventions_by_student[result["student_id"]] = result.get("interventions", [])

        return interventions_by_student

    async def analyze_emotion_trajectory(self, student_id: str, course_id: str,
                                       start_week: int, end_week: int) -> Dict[str, Any]:
        """Analyze the emotion trajectory of a student over time"""
        # This would analyze the emotion vectors for a student over multiple weeks
        # For now, return a placeholder
        return {
            "trajectory_analysis": "placeholder"
        }

    async def generate_pattern_signature(self, emotion_profile: EmotionProfile) -> str:
        """Generate a unique signature for an emotion pattern

        This creates a standardized representation of an emotion profile that can be used
        for pattern matching and similarity comparison.
        """
        # Extract key emotional dimensions and normalize them
        signature_components = [
            f"f{emotion_profile.frustration_level:.2f}",
            f"e{emotion_profile.engagement_level:.2f}",
            f"c{emotion_profile.confidence_level:.2f}",
            f"s{emotion_profile.satisfaction_level:.2f}",
            f"t{emotion_profile.emotional_temperature:.2f}",
            f"v{emotion_profile.emotional_volatility:.2f}",
            f"h{1 if emotion_profile.hidden_dissatisfaction_flag else 0}",
            f"u{self._urgency_to_numeric(emotion_profile.urgency_level)}",
            f"ft{emotion_profile.frustration_type[:3]}",  # First 3 chars of frustration type
            f"tr{self._trajectory_to_numeric(emotion_profile.emotional_trajectory)}"
        ]

        # Join components to create signature
        return "_".join(signature_components)

    def _urgency_to_numeric(self, urgency_level: str) -> float:
        """Convert urgency level string to numeric value for signature"""
        urgency_map = {
            "low": 0.2,
            "medium": 0.4,
            "high": 0.6,
            "critical": 0.8,
            "immediate": 1.0
        }
        return urgency_map.get(urgency_level.lower(), 0.0)

    def _trajectory_to_numeric(self, trajectory: str) -> float:
        """Convert emotional trajectory string to numeric value for signature"""
        trajectory_map = {
            "improving": 0.8,
            "neutral": 0.5,
            "declining": 0.2,
            "fluctuating": 0.4
        }
        return trajectory_map.get(trajectory.lower(), 0.5)

    async def calculate_pattern_similarity(
        self, pattern1: EmotionProfile, pattern2: EmotionProfile) -> float:
        """Calculate similarity score between two emotion patterns

        Returns a float between 0.0 (completely different) and 1.0 (identical)
        """
        # Define weights for different components
        weights = {
            "primary_emotions": 0.4,  # Frustration, engagement, confidence, satisfaction
            "temperature_volatility": 0.2,  # Emotional temperature and volatility
            "hidden_dissatisfaction": 0.15,  # Hidden dissatisfaction detection
            "urgency": 0.15,  # Urgency indicators
            "trajectory": 0.1   # Emotional trajectory
        }

        # Calculate primary emotions similarity (weighted average of differences)
        primary_diff = (
            abs(pattern1.frustration_level - pattern2.frustration_level) +
            abs(pattern1.engagement_level - pattern2.engagement_level) +
            abs(pattern1.confidence_level - pattern2.confidence_level) +
            abs(pattern1.satisfaction_level - pattern2.satisfaction_level)
        ) / 4.0
        primary_sim = 1.0 - primary_diff

        # Calculate temperature/volatility similarity
        temp_vol_diff = (
            abs(pattern1.emotional_temperature - pattern2.emotional_temperature) +
            abs(pattern1.emotional_volatility - pattern2.emotional_volatility)
        ) / 2.0
        temp_vol_sim = 1.0 - temp_vol_diff

        # Calculate hidden dissatisfaction similarity
        hidden_sim = 1.0 if pattern1.hidden_dissatisfaction_flag == pattern2.hidden_dissatisfaction_flag else 0.0

        # Calculate urgency similarity
        urgency_sim = 1.0 - abs(self._urgency_to_numeric(pattern1.urgency_level) -
                               self._urgency_to_numeric(pattern2.urgency_level))

        # Calculate trajectory similarity
        trajectory_sim = 1.0 if pattern1.emotional_trajectory == pattern2.emotional_trajectory else 0.0

        # Calculate weighted similarity score
        similarity = (
            weights["primary_emotions"] * primary_sim +
            weights["temperature_volatility"] * temp_vol_sim +
            weights["hidden_dissatisfaction"] * hidden_sim +
            weights["urgency"] * urgency_sim +
            weights["trajectory"] * trajectory_sim
        )

        return similarity

    async def recognize_historical_patterns(
        self, student_id: str, course_id: str, week_number: int) -> Dict[str, Any]:
        """Recognize historical patterns in a student's emotion data

        This method analyzes the student's current emotion profile and compares it with
        historical patterns to identify matches and predict outcomes.
        """
        # Get the student's current emotion profile
        historical_pattern = await self.find_emotion_patterns(
            student_id=student_id,
            course_id=course_id,
            week_number=week_number
        )

        if not historical_pattern.emotion_pattern_matches:
            return {
                "pattern_recognition": "No historical patterns found",
                "pattern_matches": [],
                "predicted_outcomes": {}
            }

        # Analyze the patterns
        pattern_signatures = []
        for match in historical_pattern.emotion_pattern_matches:
            # Generate signature for each pattern
            signature = await self.generate_pattern_signature(match.emotion_profile)
            pattern_signatures.append({
                "student_id": match.matched_student_id,
                "signature": signature,
                "similarity_score": match.similarity_score,
                "emotion_profile": match.emotion_profile.dict(),
                "metadata": match.match_metadata
            })

        # Group patterns by similarity
        pattern_clusters = self._cluster_patterns(pattern_signatures)

        # Predict outcomes based on historical patterns
        predicted_outcomes = self._predict_outcomes_from_patterns(pattern_clusters)

        return {
            "pattern_recognition": "Completed",
            "pattern_matches": pattern_signatures,
            "pattern_clusters": pattern_clusters,
            "predicted_outcomes": predicted_outcomes
        }

    def _cluster_patterns(self, pattern_signatures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Group similar patterns into clusters"""
        # Simple clustering based on signature similarity
        clusters = []
        processed = set()

        for i, pattern in enumerate(pattern_signatures):
            if i in processed:
                continue

            # Start a new cluster
            cluster = {
                "cluster_id": len(clusters) + 1,
                "patterns": [pattern],
                "avg_similarity": pattern["similarity_score"],
                "signature_prototype": pattern["signature"]
            }
            processed.add(i)

            # Find similar patterns for this cluster
            for j, other in enumerate(pattern_signatures):
                if j in processed or i == j:
                    continue

                # Simple signature comparison (in a real implementation, this would be more sophisticated)
                if self._are_signatures_similar(pattern["signature"], other["signature"]):
                    cluster["patterns"].append(other)
                    cluster["avg_similarity"] = sum(
                        p["similarity_score"] for p in cluster["patterns"]) / len(
                            cluster["patterns"])
                    processed.add(j)

            clusters.append(cluster)

        return clusters

    def _are_signatures_similar(self, sig1: str, sig2: str) -> bool:
        """Determine if two pattern signatures are similar"""
        # Simple implementation - count matching components
        components1 = sig1.split("_")
        components2 = sig2.split("_")

        if len(components1) != len(components2):
            return False

        # Count matching components
        matches = 0
        for c1, c2 in zip(components1, components2):
            # Extract the type and value
            type1, val1 = c1[0], c1[1:]
            type2, val2 = c2[0], c2[1:]

            if type1 != type2:
                continue

            # For numeric values, check if they're close
            if type1 in "fecstvuh":
                try:
                    v1 = float(val1)
                    v2 = float(val2)
                    if abs(v1 - v2) <= 0.2:  # Threshold for similarity
                        matches += 1
                except ValueError:
                    pass
            # For string values, check exact match
            else:
                if val1 == val2:
                    matches += 1

        # Consider similar if at least 70% of components match
        return matches / len(components1) >= 0.7

    def _predict_outcomes_from_patterns(
        self, pattern_clusters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict outcomes based on historical pattern clusters"""
        if not pattern_clusters:
            return {}

        # Analyze each cluster to predict outcomes
        dropout_risk = 0.0
        intervention_success_probability = 0.0
        recommended_interventions = []

        # Weight clusters by size and similarity
        total_weight = 0.0

        for cluster in pattern_clusters:
            # Calculate cluster weight based on size and average similarity
            weight = len(cluster["patterns"]) * cluster["avg_similarity"]
            total_weight += weight

            # Analyze patterns in this cluster
            cluster_dropout_risk = 0.0
            cluster_interventions = []

            for pattern in cluster["patterns"]:
                metadata = pattern.get("metadata", {})

                # Extract outcome information if available
                if "completion_status" in metadata:
                    if metadata["completion_status"].startswith("dropped"):
                        cluster_dropout_risk += 1.0

                # Extract intervention information if available
                if "successful_interventions" in metadata:
                    cluster_interventions.extend(metadata["successful_interventions"])

            # Calculate cluster-level metrics
            if len(cluster["patterns"]) > 0:
                cluster_dropout_risk /= len(cluster["patterns"])

                # Weight the dropout risk by this cluster's weight
                dropout_risk += cluster_dropout_risk * weight

                # Add unique interventions from this cluster
                for intervention in cluster_interventions:
                    if intervention not in recommended_interventions:
                        recommended_interventions.append(intervention)

        # Normalize by total weight
        if total_weight > 0:
            dropout_risk /= total_weight

        # Calculate intervention success probability based on historical data
        # (simplified implementation)
        intervention_success_probability = 1.0 - dropout_risk

        return {
            "dropout_risk": dropout_risk,
            "intervention_success_probability": intervention_success_probability,
            "recommended_interventions": recommended_interventions
        }

    async def identify_successful_interventions(
        self, pattern_matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify successful interventions from historical pattern matches"""
        # Group interventions by type
        intervention_stats = {}

        for match in pattern_matches:
            metadata = match.get("metadata", {})
            student_id = match.get("student_id", "unknown")

            # Skip if no intervention data
            if "interventions" not in metadata:
                continue

            for intervention in metadata["interventions"]:
                intervention_type = intervention.get("type", "unknown")
                success = intervention.get("success", False)

                # Initialize stats for this intervention type if needed
                if intervention_type not in intervention_stats:
                    intervention_stats[intervention_type] = {
                        "type": intervention_type,
                        "total_count": 0,
                        "success_count": 0,
                        "success_rate": 0.0,
                        "examples": []
                    }

                # Update stats
                intervention_stats[intervention_type]["total_count"] += 1
                if success:
                    intervention_stats[intervention_type]["success_count"] += 1

                # Add example if successful
                if success and len(intervention_stats[intervention_type]["examples"]) < 3:
                    intervention_stats[intervention_type]["examples"].append({
                        "student_id": student_id,
                        "details": intervention
                    })

        # Calculate success rates and sort by success rate
        interventions = []
        for stats in intervention_stats.values():
            if stats["total_count"] > 0:
                stats["success_rate"] = stats["success_count"] / stats["total_count"]
            interventions.append(stats)

        # Sort by success rate (highest first)
        interventions.sort(key=lambda x: x["success_rate"], reverse=True)

        return interventions
