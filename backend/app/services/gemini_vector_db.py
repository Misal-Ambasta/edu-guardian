from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import os
import json
from pydantic import BaseModel
from dotenv import load_dotenv
from ..emotion_analysis.analyzer import EmotionProfile
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from .vector_cache import VectorCache

load_dotenv()

class EmotionVector(BaseModel):
    """Model for emotion vector embeddings"""
    student_id: str
    course_id: str
    week_number: int
    emotion_vector: List[float]
    emotion_profile: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

class GeminiEmotionEmbeddings(Embeddings):
    """Gemini embeddings class for emotion profiles that implements LangChain's Embeddings interface"""

    def __init__(self):
        """Initialize the Gemini embeddings model"""
        # Get API key from environment variable
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")

        # Configure the Gemini API
        genai.configure(api_key=api_key)

        # Initialize the Gemini embeddings model
        self.embeddings_model = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            task_type="RETRIEVAL_DOCUMENT"
        )

        # Initialize the Gemini query embeddings model
        self.query_embeddings_model = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            task_type="RETRIEVAL_QUERY"
        )

        # Initialize vector cache
        self.vector_cache = VectorCache()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed documents using Gemini embedding model with caching"""
        results = []
        texts_to_embed = []
        indices = []

        # Check cache first
        for i, text in enumerate(texts):
            doc_id = str(hash(text))
            cached_embedding = self.vector_cache.get_document_embedding(doc_id)

            if cached_embedding is not None:
                # Convert numpy array to list for consistency
                results.append(cached_embedding.tolist())
            else:
                texts_to_embed.append(text)
                indices.append(i)

        # If there are texts not in cache, embed them
        if texts_to_embed:
            new_embeddings = self.embeddings_model.embed_documents(texts_to_embed)

            # Store in cache and add to results
            for i, embedding in zip(indices, new_embeddings):
                doc_id = str(hash(texts[i]))
                self.vector_cache.store_document_embedding(doc_id, np.array(embedding))
                results.append(embedding)

        return results

    def embed_query(self, text: str) -> List[float]:
        """Embed query text using Gemini embedding model with caching"""
        # Check cache first
        cached_embedding = self.vector_cache.get_query_embedding(text)

        if cached_embedding is not None:
            # Convert numpy array to list for consistency
            return cached_embedding.tolist()

        # If not in cache, embed and store
        embedding = self.query_embeddings_model.embed_query(text)
        self.vector_cache.store_query_embedding(text, np.array(embedding))

        return embedding

    def _emotion_profile_to_text(self, emotion_profile: EmotionProfile) -> str:
        """Convert emotion profile to text format for embedding"""
        # Create a detailed text representation of the emotion profile
        # This helps the embedding model understand the semantic meaning
        text = f"""Student emotion profile with:
        - Frustration level: {emotion_profile.frustration_level}
        - Engagement level: {emotion_profile.engagement_level}
        - Confidence level: {emotion_profile.confidence_level}
        - Satisfaction level: {emotion_profile.satisfaction_level}
        - Emotional temperature: {emotion_profile.emotional_temperature}
        - Emotional volatility: {emotion_profile.emotional_volatility}
        - Hidden dissatisfaction: {emotion_profile.hidden_dissatisfaction_flag}
        - Hidden dissatisfaction confidence: {emotion_profile.hidden_dissatisfaction_confidence}
        - Politeness mask level: {emotion_profile.politeness_mask_level}
        - Frustration type: {emotion_profile.frustration_type}
        - Frustration intensity: {emotion_profile.frustration_intensity}
        - Frustration trend: {emotion_profile.frustration_trend}
        - Urgency level: {emotion_profile.urgency_level}
        - Response urgency: {emotion_profile.response_urgency}
        - Emotional trajectory: {emotion_profile.emotional_trajectory}
        - Emotion coherence: {emotion_profile.emotion_coherence}
        - Sentiment authenticity: {emotion_profile.sentiment_authenticity}
        - Emotional complexity: {emotion_profile.emotional_complexity}
        """
        return text

class GeminiVectorDBService:
    """Service for handling emotion vector embeddings and pattern matching using Gemini and LangChain"""

    def __init__(self):
        # Initialize the Gemini embeddings model
        self.embedding_function = GeminiEmotionEmbeddings()

        # Set up ChromaDB collections using LangChain's Chroma integration
        self.emotion_patterns = Chroma(
            collection_name="emotion_patterns_gemini",
            embedding_function=self.embedding_function,
            persist_directory=os.getenv("CHROMA_DB_PATH", "./chromadb")
        )

        self.interventions = Chroma(
            collection_name="historical_interventions_gemini",
            embedding_function=self.embedding_function,
            persist_directory=os.getenv("CHROMA_DB_PATH", "./chromadb")
        )

        # Initialize the Gemini model for retrieval
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")

        genai.configure(api_key=api_key)
        self.retrieval_model = "gemini-2.5-flash"

    def embed_emotion_profile(self, emotion_profile: EmotionProfile) -> List[float]:
        """Generate a vector embedding from an emotion profile using Gemini"""
        # Convert emotion profile to text format
        text = self.embedding_function._emotion_profile_to_text(emotion_profile)

        # Generate embedding using Gemini
        return self.embedding_function.embed_query(text)

    def add_emotion_profile(self, student_id: str, course_id: str, week_number: int,
                           emotion_profile: EmotionProfile, additional_metadata: Dict[str, Any] = None) -> str:
        """Store an emotion pattern in the vector database using Gemini embeddings"""
        # Prepare metadata
        metadata = {
            "student_id": student_id,
            "course_id": course_id,
            "week_number": week_number,
            **(additional_metadata or {})
        }

        # Create a unique ID
        document_id = f"{student_id}_{course_id}_{week_number}"

        # Convert emotion profile to text format for storage
        emotion_text = self.embedding_function._emotion_profile_to_text(emotion_profile)

        # Also store the JSON representation in metadata for reconstruction
        metadata["emotion_profile_json"] = json.dumps(emotion_profile.dict())

        # Store using LangChain's Chroma integration
        from langchain_core.documents import Document

        document = Document(
            page_content=emotion_text,
            metadata=metadata,
            id=document_id
        )

        self.emotion_patterns.add_documents([document], ids=[document_id])

        return document_id

    def find_similar_emotion_patterns(self, emotion_profile: EmotionProfile,
                                     limit: int = 10, metadata_filter: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Find similar emotion patterns in the database using Gemini embeddings with optimized vector search"""
        # Convert emotion profile to text for query
        query_text = self.embedding_function._emotion_profile_to_text(emotion_profile)

        # Generate a cache key for this query
        cache_key = f"similar_patterns:{hash(query_text)}:{limit}:{hash(str(metadata_filter))}"

        # Check if we have cached results
        cached_results = self.embedding_function.vector_cache.get_document_metadata(cache_key)
        if cached_results:
            return cached_results

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
                # Extract the emotion profile JSON from metadata
                emotion_data = json.loads(doc.metadata.get("emotion_profile_json", "{}"))
                similar_patterns.append({
                    "id": doc.metadata.get("id") or doc.id,
                    "emotion_profile": emotion_data,
                    "metadata": doc.metadata,
                    "distance": score
                })
            except Exception as e:
                print(f"Error processing document: {e}")

        # Cache the results for future queries
        self.embedding_function.vector_cache.store_document_metadata(cache_key, similar_patterns)

        return similar_patterns

    def find_emotion_similar_students(self, student_id: str, course_id: str, week_number: int,
                                    limit: int = 10) -> Dict[str, Any]:
        """Find students with similar emotion patterns using Gemini embeddings"""
        # Get the student's emotion profile
        document_id = f"{student_id}_{course_id}_{week_number}"

        # Try to retrieve by ID first
        try:
            results = self.emotion_patterns.get(ids=[document_id])
            if not results['documents']:
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
                if not results:
                    return {"error": "Student emotion profile not found"}
                student_doc = results[0]
            else:
                student_doc = Document(
                    page_content=results['documents'][0],
                    metadata=results['metadatas'][0],
                    id=results['ids'][0]
                )

            # Get the emotion profile from the document
            emotion_profile_json = student_doc.metadata.get("emotion_profile_json")
            if not emotion_profile_json:
                return {"error": "Emotion profile data not found"}

            emotion_profile = EmotionProfile.parse_raw(emotion_profile_json)

            # Find similar students excluding the query student
            filter_dict = {}
            if student_id:
                filter_dict["student_id"] = {"$ne": student_id}

            # Find similar emotion patterns
            similar_patterns = self.find_similar_emotion_patterns(
                emotion_profile=emotion_profile,
                limit=limit,
                metadata_filter=filter_dict
            )

            return {
                "student_profile": emotion_profile.dict(),
                "similar_students": similar_patterns
            }

        except Exception as e:
            return {"error": f"Error finding similar students: {str(e)}"}

    def generate_insights_from_patterns(self, emotion_patterns: List[Dict[str, Any]],
                                      query: str) -> str:
        """Generate insights from emotion patterns using Gemini 2.5 Flash"""
        # Format the emotion patterns as text
        patterns_text = ""
        for i, pattern in enumerate(
            emotion_patterns[:5]):  # Limit to 5 patterns to avoid token limits
            profile = pattern.get("emotion_profile", {})
            patterns_text += f"Pattern {i+1}:\n"
            for key, value in profile.items():
                patterns_text += f"- {key}: {value}\n"
            patterns_text += "\n"

        # Create a prompt for Gemini
        prompt = f"""Based on the following emotion patterns from students, {query}

        Emotion Patterns:
        {patterns_text}

        Provide a concise analysis focusing specifically on the query.
        """

        # Generate insights using Gemini 2.5 Flash
        try:
            response = genai.models.generate_content(
                model=self.retrieval_model,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Error generating insights: {str(e)}"