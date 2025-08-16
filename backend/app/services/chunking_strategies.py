from typing import List, Dict, Any, Optional, Union, Callable
import json
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter, TokenTextSplitter
from langchain_core.documents import Document

class ChunkingStrategies:
    """
    A utility class that provides various chunking strategies for different types of data
    to optimize RAG performance.
    """
    
    @staticmethod
    def create_emotion_profile_chunks(text: str, metadata: Dict[str, Any], 
                                     chunk_size: int = 1000, 
                                     chunk_overlap: int = 200) -> List[Document]:
        """
        Create chunks from emotion profile text using recursive character splitting.
        This is useful for long emotion profile descriptions or when including comments.
        
        Args:
            text: The text to chunk
            metadata: Metadata to include with each chunk
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of Document objects
        """
        # Create text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        
        # Split text into chunks
        texts = text_splitter.split_text(text)
        
        # Create documents
        documents = []
        for i, chunk_text in enumerate(texts):
            # Create a copy of metadata for each chunk
            chunk_metadata = metadata.copy()
            
            # Add chunk information to metadata
            chunk_metadata["chunk"] = i
            chunk_metadata["chunk_count"] = len(texts)
            
            # Create document
            doc = Document(page_content=chunk_text, metadata=chunk_metadata)
            documents.append(doc)
        
        return documents
    
    @staticmethod
    def create_semantic_chunks(text: str, metadata: Dict[str, Any]) -> List[Document]:
        """
        Create semantically meaningful chunks based on content structure.
        This uses a recursive splitter with carefully chosen separators to respect semantic boundaries.
        
        Args:
            text: The text to chunk
            metadata: Metadata to include with each chunk
            
        Returns:
            List of Document objects
        """
        # Create text splitter optimized for semantic boundaries
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        
        # Split text into chunks
        texts = text_splitter.split_text(text)
        
        # Create documents
        documents = []
        for i, chunk_text in enumerate(texts):
            # Create a copy of metadata for each chunk
            chunk_metadata = metadata.copy()
            
            # Add chunk information to metadata
            chunk_metadata["chunk"] = i
            chunk_metadata["chunk_count"] = len(texts)
            
            # Create document
            doc = Document(page_content=chunk_text, metadata=chunk_metadata)
            documents.append(doc)
        
        return documents
    
    @staticmethod
    def create_token_based_chunks(text: str, metadata: Dict[str, Any], 
                                 chunk_size: int = 256, 
                                 chunk_overlap: int = 20) -> List[Document]:
        """
        Create chunks based on token count rather than character count.
        This is useful when working with token-sensitive models like Gemini.
        
        Args:
            text: The text to chunk
            metadata: Metadata to include with each chunk
            chunk_size: Maximum number of tokens per chunk
            chunk_overlap: Number of overlapping tokens between chunks
            
        Returns:
            List of Document objects
        """
        # Create token-based text splitter
        text_splitter = TokenTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        # Split text into chunks
        texts = text_splitter.split_text(text)
        
        # Create documents
        documents = []
        for i, chunk_text in enumerate(texts):
            # Create a copy of metadata for each chunk
            chunk_metadata = metadata.copy()
            
            # Add chunk information to metadata
            chunk_metadata["chunk"] = i
            chunk_metadata["chunk_count"] = len(texts)
            
            # Create document
            doc = Document(page_content=chunk_text, metadata=chunk_metadata)
            documents.append(doc)
        
        return documents
    
    @staticmethod
    def chunk_json_data(json_data: Dict[str, Any], metadata: Dict[str, Any], 
                       flatten: bool = True) -> List[Document]:
        """
        Create chunks from JSON data, either by flattening or by maintaining structure.
        
        Args:
            json_data: The JSON data to chunk
            metadata: Metadata to include with each chunk
            flatten: Whether to flatten the JSON structure
            
        Returns:
            List of Document objects
        """
        documents = []
        
        if flatten:
            # Flatten JSON structure into a single string
            flattened_text = ""
            for key, value in json_data.items():
                if isinstance(value, (dict, list)):
                    flattened_text += f"{key}: {json.dumps(value)}\n"
                else:
                    flattened_text += f"{key}: {value}\n"
            
            # Create a single document
            doc = Document(page_content=flattened_text, metadata=metadata)
            documents.append(doc)
        else:
            # Create separate documents for each top-level key
            for key, value in json_data.items():
                # Create a copy of metadata for each chunk
                chunk_metadata = metadata.copy()
                chunk_metadata["key"] = key
                
                # Convert value to string
                if isinstance(value, (dict, list)):
                    content = json.dumps(value)
                else:
                    content = str(value)
                
                # Create document
                doc = Document(page_content=f"{key}: {content}", metadata=chunk_metadata)
                documents.append(doc)
        
        return documents
    
    @staticmethod
    def create_custom_chunks(text: str, metadata: Dict[str, Any], 
                           chunk_func: Callable[[str], List[str]]) -> List[Document]:
        """
        Create chunks using a custom chunking function.
        
        Args:
            text: The text to chunk
            metadata: Metadata to include with each chunk
            chunk_func: Custom function that takes text and returns a list of chunks
            
        Returns:
            List of Document objects
        """
        # Apply custom chunking function
        texts = chunk_func(text)
        
        # Create documents
        documents = []
        for i, chunk_text in enumerate(texts):
            # Create a copy of metadata for each chunk
            chunk_metadata = metadata.copy()
            
            # Add chunk information to metadata
            chunk_metadata["chunk"] = i
            chunk_metadata["chunk_count"] = len(texts)
            
            # Create document
            doc = Document(page_content=chunk_text, metadata=chunk_metadata)
            documents.append(doc)
        
        return documents
    
    @staticmethod
    def emotion_profile_to_chunks(emotion_profile: Dict[str, Any], metadata: Dict[str, Any]) -> List[Document]:
        """
        Convert an emotion profile to multiple chunks based on different aspects of the profile.
        This creates more granular chunks for better retrieval.
        
        Args:
            emotion_profile: The emotion profile to chunk
            metadata: Metadata to include with each chunk
            
        Returns:
            List of Document objects
        """
        documents = []
        
        # Create chunks for different aspects of the emotion profile
        
        # Core emotions chunk
        core_emotions_text = f"""Core Emotions:
        Frustration Level: {emotion_profile.get('frustration_level', 0)}
        Engagement Level: {emotion_profile.get('engagement_level', 0)}
        Confidence Level: {emotion_profile.get('confidence_level', 0)}
        Satisfaction Level: {emotion_profile.get('satisfaction_level', 0)}
        """
        
        core_metadata = metadata.copy()
        core_metadata["aspect"] = "core_emotions"
        documents.append(Document(page_content=core_emotions_text, metadata=core_metadata))
        
        # Emotional dynamics chunk
        dynamics_text = f"""Emotional Dynamics:
        Emotional Temperature: {emotion_profile.get('emotional_temperature', 0)}
        Emotional Volatility: {emotion_profile.get('emotional_volatility', 0)}
        Hidden Dissatisfaction: {emotion_profile.get('hidden_dissatisfaction_flag', False)}
        Urgency Level: {emotion_profile.get('urgency_level', 'low')}
        """
        
        dynamics_metadata = metadata.copy()
        dynamics_metadata["aspect"] = "emotional_dynamics"
        documents.append(Document(page_content=dynamics_text, metadata=dynamics_metadata))
        
        # Trajectory and context chunk
        trajectory_text = f"""Trajectory and Context:
        Frustration Type: {emotion_profile.get('frustration_type', 'unknown')}
        Emotional Trajectory: {emotion_profile.get('emotional_trajectory', 'stable')}
        Dominant Emotions: {', '.join(emotion_profile.get('dominant_emotions', []))}
        Sentiment Score: {emotion_profile.get('sentiment_score', 0)}
        """
        
        trajectory_metadata = metadata.copy()
        trajectory_metadata["aspect"] = "trajectory_context"
        documents.append(Document(page_content=trajectory_text, metadata=trajectory_metadata))
        
        # Full profile as a single chunk
        full_text = f"""Complete Emotion Profile:
        {json.dumps(emotion_profile, indent=2)}
        """
        
        full_metadata = metadata.copy()
        full_metadata["aspect"] = "full_profile"
        documents.append(Document(page_content=full_text, metadata=full_metadata))
        
        return documents