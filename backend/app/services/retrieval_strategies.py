from typing import List, Dict, Any, Optional, Union, Callable
import json
from langchain.schema import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_community.vectorstores import Chroma

class HybridRetriever(BaseRetriever):
    """
    A hybrid retriever that combines vector search with metadata filtering
    for more accurate and relevant retrieval results.
    """
    
    def __init__(self, vector_store: Chroma, metadata_filters: Dict[str, Any] = None, k: int = 5):
        """
        Initialize the hybrid retriever.
        
        Args:
            vector_store: The vector store to search
            metadata_filters: Optional metadata filters to apply
            k: Number of documents to retrieve
        """
        super().__init__()
        self.vector_store = vector_store
        self.metadata_filters = metadata_filters or {}
        self.k = k
    
    def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun) -> List[Document]:
        """
        Get relevant documents using hybrid retrieval approach.
        
        Args:
            query: The query string
            run_manager: Callback manager
            
        Returns:
            List of relevant documents
        """
        # Perform vector search with metadata filtering
        docs = self.vector_store.similarity_search(
            query=query,
            k=self.k,
            filter=self.metadata_filters
        )
        
        return docs

class EmotionPatternRetriever:
    """
    Specialized retriever for emotion patterns that implements various
    retrieval strategies optimized for educational emotion data.
    """
    
    def __init__(self, vector_store: Chroma):
        """
        Initialize the emotion pattern retriever.
        
        Args:
            vector_store: The vector store containing emotion patterns
        """
        self.vector_store = vector_store
    
    async def retrieve_by_similarity(self, query_text: str, k: int = 5, 
                                   metadata_filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Retrieve emotion patterns by similarity to the query text.
        
        Args:
            query_text: The query text
            k: Number of patterns to retrieve
            metadata_filters: Optional metadata filters
            
        Returns:
            List of similar emotion patterns with similarity scores
        """
        # Perform similarity search
        results = self.vector_store.similarity_search_with_score(
            query=query_text,
            k=k,
            filter=metadata_filters
        )
        
        # Process results
        patterns = []
        for doc, score in results:
            # Convert similarity score (distance) to a 0-1 scale where 1 is most similar
            similarity = 1.0 - min(score, 1.0)
            
            # Extract emotion profile from metadata
            emotion_profile_json = doc.metadata.get("emotion_profile")
            emotion_profile_dict = json.loads(emotion_profile_json) if emotion_profile_json else {}
            
            # Create result entry
            pattern = {
                "document_id": doc.metadata.get("document_id", ""),
                "student_id": doc.metadata.get("student_id", ""),
                "course_id": doc.metadata.get("course_id", ""),
                "week_number": doc.metadata.get("week_number", 0),
                "emotion_profile": emotion_profile_dict,
                "similarity_score": similarity,
                "metadata": doc.metadata
            }
            
            patterns.append(pattern)
        
        return patterns
    
    async def retrieve_by_emotion_profile(self, emotion_profile: Dict[str, Any], k: int = 5, 
                                        exclude_student_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve emotion patterns similar to the given emotion profile.
        
        Args:
            emotion_profile: The emotion profile to find similar patterns for
            k: Number of patterns to retrieve
            exclude_student_id: Optional student ID to exclude
            
        Returns:
            List of similar emotion patterns with similarity scores
        """
        # Convert emotion profile to text representation
        query_text = self._emotion_profile_to_text(emotion_profile)
        
        # Create filter to exclude the specified student if needed
        filter_dict = None
        if exclude_student_id:
            filter_dict = {"student_id": {"$ne": exclude_student_id}}
        
        # Retrieve by similarity
        return await self.retrieve_by_similarity(query_text, k, filter_dict)
    
    async def retrieve_by_aspect(self, aspect: str, value: Any, k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve emotion patterns by a specific aspect and value.
        
        Args:
            aspect: The aspect to filter by (e.g., "frustration_level")
            value: The value to filter by
            k: Number of patterns to retrieve
            
        Returns:
            List of matching emotion patterns
        """
        # Create query text based on aspect and value
        query_text = f"{aspect} is {value}"
        
        # Create metadata filter
        filter_dict = None
        if aspect in ["student_id", "course_id", "week_number"]:
            filter_dict = {aspect: value}
        
        # Retrieve by similarity
        return await self.retrieve_by_similarity(query_text, k, filter_dict)
    
    async def retrieve_by_multiple_aspects(self, aspects: Dict[str, Any], k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve emotion patterns by multiple aspects and values.
        
        Args:
            aspects: Dictionary of aspects and values to filter by
            k: Number of patterns to retrieve
            
        Returns:
            List of matching emotion patterns
        """
        # Create query text based on aspects and values
        query_parts = []
        for aspect, value in aspects.items():
            query_parts.append(f"{aspect} is {value}")
        
        query_text = ". ".join(query_parts)
        
        # Create metadata filter
        filter_dict = {}
        for aspect, value in aspects.items():
            if aspect in ["student_id", "course_id", "week_number"]:
                filter_dict[aspect] = value
        
        # Use empty filter if no filterable aspects
        if not filter_dict:
            filter_dict = None
        
        # Retrieve by similarity
        return await self.retrieve_by_similarity(query_text, k, filter_dict)
    
    async def retrieve_by_emotional_state(self, emotional_state: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve emotion patterns by a described emotional state.
        
        Args:
            emotional_state: Description of the emotional state
            k: Number of patterns to retrieve
            
        Returns:
            List of matching emotion patterns
        """
        # Use the emotional state description as the query
        return await self.retrieve_by_similarity(emotional_state, k)
    
    async def retrieve_by_intervention_success(self, intervention_type: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve emotion patterns where a specific intervention type was successful.
        
        Args:
            intervention_type: The type of intervention
            k: Number of patterns to retrieve
            
        Returns:
            List of matching emotion patterns
        """
        # Create query text
        query_text = f"Successful intervention of type {intervention_type}"
        
        # Retrieve patterns
        patterns = await self.retrieve_by_similarity(query_text, k * 2)  # Retrieve more to filter
        
        # Filter patterns with successful interventions of the specified type
        filtered_patterns = []
        for pattern in patterns:
            metadata = pattern.get("metadata", {})
            if "successful_interventions" in metadata:
                interventions = metadata["successful_interventions"]
                if isinstance(interventions, str):
                    try:
                        interventions = json.loads(interventions)
                    except json.JSONDecodeError:
                        interventions = []
                
                # Check if any intervention matches the specified type
                for intervention in interventions:
                    if intervention.get("intervention_type") == intervention_type:
                        filtered_patterns.append(pattern)
                        break
        
        # Return top k filtered patterns
        return filtered_patterns[:k]
    
    def _emotion_profile_to_text(self, emotion_profile: Dict[str, Any]) -> str:
        """
        Convert an emotion profile to a detailed text representation for retrieval.
        
        Args:
            emotion_profile: The emotion profile to convert
            
        Returns:
            Text representation of the emotion profile
        """
        text_parts = []
        
        # Add core emotions
        if "frustration_level" in emotion_profile:
            text_parts.append(f"Frustration level {emotion_profile['frustration_level']:.2f} out of 1.0.")
        
        if "engagement_level" in emotion_profile:
            text_parts.append(f"Engagement level {emotion_profile['engagement_level']:.2f} out of 1.0.")
        
        if "confidence_level" in emotion_profile:
            text_parts.append(f"Confidence level {emotion_profile['confidence_level']:.2f} out of 1.0.")
        
        if "satisfaction_level" in emotion_profile:
            text_parts.append(f"Satisfaction level {emotion_profile['satisfaction_level']:.2f} out of 1.0.")
        
        # Add emotional dynamics
        if "emotional_temperature" in emotion_profile:
            text_parts.append(f"Emotional temperature {emotion_profile['emotional_temperature']:.2f} out of 1.0.")
        
        if "emotional_volatility" in emotion_profile:
            text_parts.append(f"Emotional volatility {emotion_profile['emotional_volatility']:.2f} out of 1.0.")
        
        if "hidden_dissatisfaction_flag" in emotion_profile and emotion_profile["hidden_dissatisfaction_flag"]:
            text_parts.append("There are signs of hidden dissatisfaction.")
        
        if "urgency_level" in emotion_profile:
            text_parts.append(f"The urgency level is {emotion_profile['urgency_level']}.")
        
        # Add trajectory and context
        if "frustration_type" in emotion_profile:
            text_parts.append(f"The frustration type is {emotion_profile['frustration_type']}.")
        
        if "emotional_trajectory" in emotion_profile:
            text_parts.append(f"The emotional trajectory is {emotion_profile['emotional_trajectory']}.")
        
        if "dominant_emotions" in emotion_profile and emotion_profile["dominant_emotions"]:
            emotions_str = ", ".join(emotion_profile["dominant_emotions"])
            text_parts.append(f"Dominant emotions: {emotions_str}.")
        
        if "sentiment_score" in emotion_profile:
            text_parts.append(f"Sentiment score is {emotion_profile['sentiment_score']:.2f}.")
        
        return " ".join(text_parts)

class RetrievalStrategies:
    """
    A collection of retrieval strategies for different use cases in the RAG pipeline.
    """
    
    @staticmethod
    async def retrieve_similar_emotion_patterns(retriever: EmotionPatternRetriever, 
                                              emotion_profile: Dict[str, Any], 
                                              k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve emotion patterns similar to the given profile.
        
        Args:
            retriever: The emotion pattern retriever
            emotion_profile: The emotion profile to find similar patterns for
            k: Number of patterns to retrieve
            
        Returns:
            List of similar emotion patterns
        """
        return await retriever.retrieve_by_emotion_profile(emotion_profile, k)
    
    @staticmethod
    async def retrieve_intervention_recommendations(retriever: EmotionPatternRetriever, 
                                                 emotion_profile: Dict[str, Any], 
                                                 k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve intervention recommendations based on the emotion profile.
        
        Args:
            retriever: The emotion pattern retriever
            emotion_profile: The emotion profile to find recommendations for
            k: Number of recommendations to retrieve
            
        Returns:
            List of intervention recommendations
        """
        # Retrieve similar patterns
        similar_patterns = await retriever.retrieve_by_emotion_profile(emotion_profile, k * 2)
        
        # Extract successful interventions
        recommendations = []
        for pattern in similar_patterns:
            metadata = pattern.get("metadata", {})
            if "successful_interventions" in metadata:
                interventions = metadata["successful_interventions"]
                if isinstance(interventions, str):
                    try:
                        interventions = json.loads(interventions)
                    except json.JSONDecodeError:
                        interventions = []
                
                for intervention in interventions:
                    # Add similarity score and pattern info to intervention
                    intervention["similarity_score"] = pattern.get("similarity_score", 0.0)
                    intervention["source_pattern"] = {
                        "student_id": pattern.get("student_id", ""),
                        "course_id": pattern.get("course_id", ""),
                        "week_number": pattern.get("week_number", 0)
                    }
                    recommendations.append(intervention)
        
        # Remove duplicates and sort by success rate
        unique_recommendations = {}
        for rec in recommendations:
            rec_type = rec.get("intervention_type", "")
            if rec_type not in unique_recommendations or \
               rec.get("success_rate", 0) > unique_recommendations[rec_type].get("success_rate", 0):
                unique_recommendations[rec_type] = rec
        
        # Convert to list and sort by success rate
        result = list(unique_recommendations.values())
        result.sort(key=lambda x: x.get("success_rate", 0), reverse=True)
        
        return result[:k]
    
    @staticmethod
    async def retrieve_by_emotional_trajectory(retriever: EmotionPatternRetriever, 
                                             trajectory: str, 
                                             k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve patterns by emotional trajectory.
        
        Args:
            retriever: The emotion pattern retriever
            trajectory: The emotional trajectory to search for
            k: Number of patterns to retrieve
            
        Returns:
            List of matching emotion patterns
        """
        return await retriever.retrieve_by_aspect("emotional_trajectory", trajectory, k)
    
    @staticmethod
    async def retrieve_by_urgency(retriever: EmotionPatternRetriever, 
                               urgency_level: str, 
                               k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve patterns by urgency level.
        
        Args:
            retriever: The emotion pattern retriever
            urgency_level: The urgency level to search for
            k: Number of patterns to retrieve
            
        Returns:
            List of matching emotion patterns
        """
        return await retriever.retrieve_by_aspect("urgency_level", urgency_level, k)
    
    @staticmethod
    async def retrieve_by_frustration_type(retriever: EmotionPatternRetriever, 
                                        frustration_type: str, 
                                        k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve patterns by frustration type.
        
        Args:
            retriever: The emotion pattern retriever
            frustration_type: The frustration type to search for
            k: Number of patterns to retrieve
            
        Returns:
            List of matching emotion patterns
        """
        return await retriever.retrieve_by_aspect("frustration_type", frustration_type, k)