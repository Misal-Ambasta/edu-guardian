from typing import List, Dict, Any, Optional, Union, Tuple
import json
import asyncio
from langchain.schema import Document
from langchain.embeddings import CacheBackedEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

from ..models.emotion import EmotionProfile
from ..models.historical_pattern import HistoricalPattern
from .vector_cache import VectorCache

class EnhancedRAGService:
    """
    Enhanced RAG (Retrieval Augmented Generation) service that leverages advanced LangChain features
    for improved retrieval, context handling, and generation capabilities.
    """
    
    def __init__(self, api_key: str, cache_dir: str = "./cache"):
        """
        Initialize the Enhanced RAG service.
        
        Args:
            api_key: Google Generative AI API key
            cache_dir: Directory to store vector cache
        """
        self.api_key = api_key
        self.cache_dir = cache_dir
        
        # Initialize embeddings with caching
        self.base_embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=api_key,
            task_type="retrieval_query"
        )
        
        # Set up cache for embeddings
        self.vector_cache = VectorCache(cache_dir=cache_dir)
        self.cached_embeddings = CacheBackedEmbeddings.from_bytes_store(
            self.base_embeddings,
            self.vector_cache,
            namespace="emotion_embeddings"
        )
        
        # Initialize vector stores
        self.emotion_patterns_store = None
        self.historical_interventions_store = None
        
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.2,
            convert_system_message_to_human=True
        )
    
    async def initialize_vector_stores(self):
        """
        Initialize or load the vector stores for emotion patterns and historical interventions.
        """
        # Initialize emotion patterns store
        self.emotion_patterns_store = Chroma(
            collection_name="emotion_patterns_enhanced",
            embedding_function=self.cached_embeddings,
            persist_directory=f"{self.cache_dir}/emotion_patterns"
        )
        
        # Initialize historical interventions store
        self.historical_interventions_store = Chroma(
            collection_name="historical_interventions_enhanced",
            embedding_function=self.cached_embeddings,
            persist_directory=f"{self.cache_dir}/historical_interventions"
        )
    
    def _emotion_profile_to_text(self, emotion_profile: EmotionProfile) -> str:
        """
        Convert an emotion profile to a detailed text representation for embedding.
        
        Args:
            emotion_profile: The emotion profile to convert
            
        Returns:
            Text representation of the emotion profile
        """
        text_parts = [
            f"Student emotion profile with frustration level {emotion_profile.frustration_level:.2f} out of 1.0.",
            f"Engagement level is {emotion_profile.engagement_level:.2f} out of 1.0.",
            f"Confidence level is {emotion_profile.confidence_level:.2f} out of 1.0.",
            f"Satisfaction level is {emotion_profile.satisfaction_level:.2f} out of 1.0.",
            f"Emotional temperature is {emotion_profile.emotional_temperature:.2f} out of 1.0.",
            f"Emotional volatility is {emotion_profile.emotional_volatility:.2f} out of 1.0.",
        ]
        
        if emotion_profile.hidden_dissatisfaction_flag:
            text_parts.append("There are signs of hidden dissatisfaction.")
        
        if emotion_profile.urgency_level:
            text_parts.append(f"The urgency level is {emotion_profile.urgency_level}.")
        
        if emotion_profile.frustration_type:
            text_parts.append(f"The frustration type is {emotion_profile.frustration_type}.")
        
        if emotion_profile.emotional_trajectory:
            text_parts.append(f"The emotional trajectory is {emotion_profile.emotional_trajectory}.")
        
        if emotion_profile.dominant_emotions:
            emotions_str = ", ".join(emotion_profile.dominant_emotions)
            text_parts.append(f"Dominant emotions: {emotions_str}.")
        
        if emotion_profile.sentiment_score is not None:
            text_parts.append(f"Sentiment score is {emotion_profile.sentiment_score:.2f}.")
        
        return " ".join(text_parts)
    
    async def add_emotion_profile(self, emotion_profile: EmotionProfile, 
                                metadata: Dict[str, Any]) -> str:
        """
        Add an emotion profile to the vector database.
        
        Args:
            emotion_profile: The emotion profile to add
            metadata: Additional metadata to store with the profile
            
        Returns:
            Document ID of the added profile
        """
        if self.emotion_patterns_store is None:
            await self.initialize_vector_stores()
        
        # Convert emotion profile to text
        text_representation = self._emotion_profile_to_text(emotion_profile)
        
        # Add emotion profile JSON to metadata
        metadata["emotion_profile"] = json.dumps(emotion_profile.dict())
        
        # Create document
        document = Document(page_content=text_representation, metadata=metadata)
        
        # Add to vector store
        ids = self.emotion_patterns_store.add_documents([document])
        
        # Persist changes
        self.emotion_patterns_store.persist()
        
        return ids[0]
    
    async def find_similar_emotion_patterns(self, emotion_profile: EmotionProfile, 
                                          k: int = 5, exclude_student_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find similar emotion patterns to the given profile.
        
        Args:
            emotion_profile: The emotion profile to find similar patterns for
            k: Number of similar patterns to retrieve
            exclude_student_id: Optional student ID to exclude from results
            
        Returns:
            List of similar emotion patterns with similarity scores
        """
        if self.emotion_patterns_store is None:
            await self.initialize_vector_stores()
        
        # Convert emotion profile to text
        query_text = self._emotion_profile_to_text(emotion_profile)
        
        # Create filter to exclude the specified student if needed
        filter_dict = None
        if exclude_student_id:
            filter_dict = {"student_id": {"$ne": exclude_student_id}}
        
        # Perform similarity search
        results = self.emotion_patterns_store.similarity_search_with_score(
            query=query_text,
            k=k,
            filter=filter_dict
        )
        
        # Process results
        similar_patterns = []
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
            
            similar_patterns.append(pattern)
        
        return similar_patterns
    
    async def get_recommended_interventions(self, student_id: str, course_id: str, 
                                          week_number: int, similar_patterns: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Get recommended interventions based on historical patterns using the enhanced RAG pipeline.
        
        Args:
            student_id: Student ID
            course_id: Course ID
            week_number: Week number
            similar_patterns: Optional pre-retrieved similar patterns
            
        Returns:
            List of recommended interventions
        """
        # Find similar patterns if not provided
        if not similar_patterns:
            # Get the student's emotion profile
            # This would typically come from a database query
            # For now, we'll use a placeholder
            emotion_profile = EmotionProfile()
            
            # Find similar patterns
            similar_patterns = await self.find_similar_emotion_patterns(
                emotion_profile=emotion_profile,
                exclude_student_id=student_id
            )
        
        # Extract successful interventions from similar patterns
        recommended_interventions = []
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
                    # Add similarity score to intervention
                    intervention["similarity_score"] = pattern.get("similarity_score", 0.0)
                    recommended_interventions.append(intervention)
        
        # Remove duplicates and sort by success rate
        unique_interventions = {}
        for intervention in recommended_interventions:
            intervention_type = intervention.get("intervention_type", "")
            if intervention_type not in unique_interventions or \
               intervention.get("success_rate", 0) > unique_interventions[intervention_type].get("success_rate", 0):
                unique_interventions[intervention_type] = intervention
        
        # Convert to list and sort by success rate
        result = list(unique_interventions.values())
        result.sort(key=lambda x: x.get("success_rate", 0), reverse=True)
        
        return result
    
    async def generate_insights_from_patterns(self, query: str, patterns: List[Dict[str, Any]]) -> str:
        """
        Generate insights from emotion patterns using the LangChain RAG pipeline.
        
        Args:
            query: The query or question to answer
            patterns: List of emotion patterns to analyze
            
        Returns:
            Generated insights text
        """
        # Format patterns into a text representation
        patterns_text = self._format_patterns_for_context(patterns)
        
        # Create a RAG prompt template
        template = """
        You are an educational analytics expert analyzing student emotion patterns.
        
        Use the following emotion pattern data to answer the question or generate insights.
        
        EMOTION PATTERNS:
        {context}
        
        QUESTION: {question}
        
        Provide a concise, data-driven analysis based on the emotion patterns. Focus on actionable insights.
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        
        # Create the RAG chain
        rag_chain = (
            {"context": RunnableLambda(lambda _: patterns_text), "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        # Run the chain
        response = await rag_chain.ainvoke(query)
        
        return response
    
    def _format_patterns_for_context(self, patterns: List[Dict[str, Any]], max_patterns: int = 5) -> str:
        """
        Format emotion patterns into a text representation for context.
        
        Args:
            patterns: List of emotion patterns
            max_patterns: Maximum number of patterns to include
            
        Returns:
            Formatted text representation
        """
        # Limit to top patterns by similarity score
        patterns = sorted(patterns, key=lambda x: x.get("similarity_score", 0), reverse=True)[:max_patterns]
        
        formatted_patterns = []
        for i, pattern in enumerate(patterns):
            emotion_profile = pattern.get("emotion_profile", {})
            
            pattern_text = f"Pattern {i+1} (Similarity: {pattern.get('similarity_score', 0):.2f}):\n"
            pattern_text += f"  Student ID: {pattern.get('student_id', 'Unknown')}\n"
            pattern_text += f"  Course ID: {pattern.get('course_id', 'Unknown')}\n"
            pattern_text += f"  Week: {pattern.get('week_number', 0)}\n"
            
            # Add emotion profile details
            pattern_text += "  Emotion Profile:\n"
            for key, value in emotion_profile.items():
                if isinstance(value, float):
                    pattern_text += f"    {key}: {value:.2f}\n"
                else:
                    pattern_text += f"    {key}: {value}\n"
            
            # Add successful interventions if available
            metadata = pattern.get("metadata", {})
            if "successful_interventions" in metadata:
                interventions = metadata["successful_interventions"]
                if isinstance(interventions, str):
                    try:
                        interventions = json.loads(interventions)
                    except json.JSONDecodeError:
                        interventions = []
                
                if interventions:
                    pattern_text += "  Successful Interventions:\n"
                    for intervention in interventions:
                        int_type = intervention.get("intervention_type", "Unknown")
                        success_rate = intervention.get("success_rate", 0)
                        pattern_text += f"    {int_type} (Success Rate: {success_rate:.2f})\n"
            
            formatted_patterns.append(pattern_text)
        
        return "\n\n".join(formatted_patterns)
    
    async def create_rag_chain(self, system_prompt: str):
        """
        Create a reusable RAG chain with the specified system prompt.
        
        Args:
            system_prompt: System prompt for the LLM
            
        Returns:
            RAG chain that can be invoked with a query and context
        """
        # Create a prompt template with system and user messages
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{context}\n\nQuestion: {question}")
        ])
        
        # Create the RAG chain
        rag_chain = (
            prompt
            | self.llm
            | StrOutputParser()
        )
        
        return rag_chain
    
    async def query_with_rag(self, query: str, student_id: str, course_id: str, week_number: int) -> str:
        """
        Query the RAG system with a specific question about a student.
        
        Args:
            query: The query or question to answer
            student_id: Student ID
            course_id: Course ID
            week_number: Week number
            
        Returns:
            Generated response
        """
        # Get the student's emotion profile from the database
        from sqlalchemy.orm import Session
        from ..database.db import get_db
        from ..models.student_journey import StudentJourney
        
        # Get database session
        db = next(get_db())
        
        try:
            # Query the database for the student's latest journey entry
            student_journey = db.query(StudentJourney).filter(
                StudentJourney.student_id == student_id,
                StudentJourney.course_id == course_id
            ).order_by(StudentJourney.week_number.desc()).first()
            
            if not student_journey:
                # If no journey found, return a default emotion profile
                emotion_profile = EmotionProfile(
                    frustration_level=0.5,
                    engagement_level=0.5,
                    confidence_level=0.5,
                    satisfaction_level=0.5,
                    frustration_type="mixed",
                    frustration_intensity="moderate",
                    frustration_trend="stable",
                    urgency_level="low",
                    urgency_signals=[],
                    response_urgency="routine",
                    emotional_temperature=0.5,
                    emotional_volatility=0.5,
                    emotional_trajectory="neutral",
                    hidden_dissatisfaction_flag=False,
                    hidden_dissatisfaction_confidence=0.1,
                    hidden_signals=[],
                    politeness_mask_level=0.3,
                    dropout_risk_emotions=[],
                    positive_recovery_indicators=[],
                    emotional_triggers=[],
                    emotion_coherence=0.5,
                    sentiment_authenticity=0.5,
                    emotional_complexity="simple"
                )
            else:
                # Create an EmotionProfile from the StudentJourney data
                emotion_profile = EmotionProfile(
                    frustration_level=student_journey.frustration_level or 0.5,
                    engagement_level=student_journey.engagement_level or 0.5,
                    confidence_level=student_journey.confidence_level or 0.5,
                    satisfaction_level=student_journey.satisfaction_level or 0.5,
                    frustration_type=student_journey.frustration_type or "mixed",
                    frustration_intensity=student_journey.frustration_intensity or "moderate",
                    frustration_trend=student_journey.frustration_trend or "stable",
                    urgency_level=student_journey.urgency_level or "low",
                    urgency_signals=student_journey.urgency_signals or [],
                    response_urgency=student_journey.response_urgency or "routine",
                    emotional_temperature=student_journey.emotional_temperature or 0.5,
                    emotional_volatility=student_journey.emotional_volatility or 0.5,
                    emotional_trajectory=student_journey.emotional_trajectory or "neutral",
                    hidden_dissatisfaction_flag=student_journey.hidden_dissatisfaction_flag or False,
                    hidden_dissatisfaction_confidence=student_journey.hidden_dissatisfaction_confidence or 0.1,
                    hidden_signals=student_journey.hidden_signals or [],
                    politeness_mask_level=student_journey.politeness_mask_level or 0.3,
                    dropout_risk_emotions=student_journey.dropout_risk_emotions or [],
                    positive_recovery_indicators=student_journey.positive_recovery_indicators or [],
                    emotional_triggers=student_journey.emotional_triggers or [],
                    emotion_coherence=student_journey.emotion_coherence or 0.5,
                    sentiment_authenticity=student_journey.sentiment_authenticity or 0.5,
                    emotional_complexity=student_journey.emotional_complexity or "simple"
                )
        finally:
            # Close the database session
            db.close()
        
        # Find similar patterns
        similar_patterns = await self.find_similar_emotion_patterns(
            emotion_profile=emotion_profile,
            exclude_student_id=student_id
        )
        
        # Format patterns into context
        context = self._format_patterns_for_context(similar_patterns)
        
        # Create a system prompt
        system_prompt = """
        You are an educational analytics assistant that helps educators understand student emotion patterns 
        and recommend appropriate interventions. Use the provided context about similar student patterns 
        to answer questions accurately and provide actionable insights.
        """
        
        # Create the RAG chain
        rag_chain = await self.create_rag_chain(system_prompt)
        
        # Run the chain
        response = await rag_chain.ainvoke({"context": context, "question": query})
        
        return response