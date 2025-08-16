from typing import List, Dict, Any, Optional
import asyncio
import os
from dotenv import load_dotenv

from ..models.emotion import EmotionProfile
from .enhanced_rag import EnhancedRAGService
from .chunking_strategies import ChunkingStrategies
from .retrieval_strategies import EmotionPatternRetriever, RetrievalStrategies

# Load environment variables
load_dotenv()

async def example_basic_rag_usage():
    """
    Example of basic RAG usage with the enhanced RAG service.
    """
    # Get API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        return
    
    # Initialize RAG service
    rag_service = EnhancedRAGService(api_key=api_key)
    await rag_service.initialize_vector_stores()
    
    # Create a sample emotion profile
    emotion_profile = EmotionProfile(
        frustration_level=0.7,
        engagement_level=0.4,
        confidence_level=0.3,
        satisfaction_level=0.2,
        emotional_temperature=0.8,
        emotional_volatility=0.6,
        hidden_dissatisfaction_flag=True,
        urgency_level="high",
        frustration_type="technical",
        emotional_trajectory="declining",
        dominant_emotions=["frustration", "anxiety"],
        sentiment_score=-0.6
    )
    
    # Add the emotion profile to the vector store
    metadata = {
        "student_id": "student123",
        "course_id": "course456",
        "week_number": 3,
        "document_id": "doc789"
    }
    
    document_id = await rag_service.add_emotion_profile(emotion_profile, metadata)
    print(f"Added emotion profile with document ID: {document_id}")
    
    # Find similar emotion patterns
    similar_patterns = await rag_service.find_similar_emotion_patterns(
        emotion_profile=emotion_profile,
        exclude_student_id="student123"
    )
    
    print(f"Found {len(similar_patterns)} similar patterns:")
    for i, pattern in enumerate(similar_patterns):
        print(f"Pattern {i+1}: Similarity score {pattern['similarity_score']:.2f}")
        print(f"  Student ID: {pattern['student_id']}")
        print(f"  Course ID: {pattern['course_id']}")
        print(f"  Week: {pattern['week_number']}")
        print()
    
    # Get recommended interventions
    recommendations = await rag_service.get_recommended_interventions(
        student_id="student123",
        course_id="course456",
        week_number=3,
        similar_patterns=similar_patterns
    )
    
    print(f"Found {len(recommendations)} recommended interventions:")
    for i, rec in enumerate(recommendations):
        print(f"Recommendation {i+1}: {rec.get('intervention_type')}")
        print(f"  Success rate: {rec.get('success_rate', 0):.2f}")
        print(f"  Description: {rec.get('description', '')}")
        print()
    
    # Generate insights from patterns
    query = "What are the main emotional challenges faced by this student and what interventions might help?"    
    insights = await rag_service.generate_insights_from_patterns(query, similar_patterns)
    
    print("Generated insights:")
    print(insights)

async def example_advanced_chunking():
    """
    Example of advanced chunking strategies.
    """
    # Create a sample emotion profile
    emotion_profile = EmotionProfile(
        frustration_level=0.7,
        engagement_level=0.4,
        confidence_level=0.3,
        satisfaction_level=0.2,
        emotional_temperature=0.8,
        emotional_volatility=0.6,
        hidden_dissatisfaction_flag=True,
        urgency_level="high",
        frustration_type="technical",
        emotional_trajectory="declining",
        dominant_emotions=["frustration", "anxiety"],
        sentiment_score=-0.6
    )
    
    # Convert to dictionary
    emotion_dict = emotion_profile.dict()
    
    # Metadata
    metadata = {
        "student_id": "student123",
        "course_id": "course456",
        "week_number": 3,
        "document_id": "doc789"
    }
    
    # Create chunks using different strategies
    print("Creating chunks using different strategies:")
    
    # 1. Emotion profile to chunks
    emotion_chunks = ChunkingStrategies.emotion_profile_to_chunks(emotion_dict, metadata)
    print(f"Emotion profile chunks: {len(emotion_chunks)}")
    for i, chunk in enumerate(emotion_chunks):
        print(f"Chunk {i+1} - Aspect: {chunk.metadata.get('aspect')}")
        print(f"Content: {chunk.page_content[:50]}...")
        print()
    
    # 2. JSON chunking
    json_chunks = ChunkingStrategies.chunk_json_data(emotion_dict, metadata)
    print(f"JSON chunks: {len(json_chunks)}")
    for i, chunk in enumerate(json_chunks):
        print(f"Chunk {i+1}:")
        print(f"Content: {chunk.page_content[:50]}...")
        print()
    
    # 3. Semantic chunking
    text = """Student is showing signs of frustration with the course material. 
    Their engagement has been declining over the past three weeks. 
    They have expressed concerns about the pace of the course and difficulty understanding key concepts. 
    Their confidence is low, and they are at risk of falling behind. 
    Recent comments indicate technical issues with the learning platform are adding to their frustration.
    """
    
    semantic_chunks = ChunkingStrategies.create_semantic_chunks(text, metadata)
    print(f"Semantic chunks: {len(semantic_chunks)}")
    for i, chunk in enumerate(semantic_chunks):
        print(f"Chunk {i+1}:")
        print(f"Content: {chunk.page_content}")
        print()

async def example_advanced_retrieval():
    """
    Example of advanced retrieval strategies.
    """
    # Get API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        return
    
    # Initialize RAG service
    rag_service = EnhancedRAGService(api_key=api_key)
    await rag_service.initialize_vector_stores()
    
    # Create a retriever
    retriever = EmotionPatternRetriever(rag_service.emotion_patterns_store)
    
    # Create a sample emotion profile
    emotion_profile = EmotionProfile(
        frustration_level=0.7,
        engagement_level=0.4,
        confidence_level=0.3,
        satisfaction_level=0.2,
        emotional_temperature=0.8,
        emotional_volatility=0.6,
        hidden_dissatisfaction_flag=True,
        urgency_level="high",
        frustration_type="technical",
        emotional_trajectory="declining",
        dominant_emotions=["frustration", "anxiety"],
        sentiment_score=-0.6
    )
    
    # Convert to dictionary
    emotion_dict = emotion_profile.dict()
    
    # 1. Retrieve by emotion profile
    print("Retrieving by emotion profile:")
    similar_patterns = await RetrievalStrategies.retrieve_similar_emotion_patterns(
        retriever=retriever,
        emotion_profile=emotion_dict
    )
    
    print(f"Found {len(similar_patterns)} similar patterns")
    
    # 2. Retrieve intervention recommendations
    print("\nRetrieving intervention recommendations:")
    recommendations = await RetrievalStrategies.retrieve_intervention_recommendations(
        retriever=retriever,
        emotion_profile=emotion_dict
    )
    
    print(f"Found {len(recommendations)} recommendations")
    
    # 3. Retrieve by emotional trajectory
    print("\nRetrieving by emotional trajectory:")
    trajectory_patterns = await RetrievalStrategies.retrieve_by_emotional_trajectory(
        retriever=retriever,
        trajectory="declining"
    )
    
    print(f"Found {len(trajectory_patterns)} patterns with declining trajectory")
    
    # 4. Retrieve by urgency
    print("\nRetrieving by urgency:")
    urgent_patterns = await RetrievalStrategies.retrieve_by_urgency(
        retriever=retriever,
        urgency_level="high"
    )
    
    print(f"Found {len(urgent_patterns)} patterns with high urgency")

async def example_rag_chain():
    """
    Example of using a RAG chain for question answering.
    """
    # Get API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        return
    
    # Initialize RAG service
    rag_service = EnhancedRAGService(api_key=api_key)
    await rag_service.initialize_vector_stores()
    
    # Create a sample query
    query = "What interventions are most effective for students with high frustration and declining engagement?"
    
    # Query with RAG
    response = await rag_service.query_with_rag(
        query=query,
        student_id="student123",
        course_id="course456",
        week_number=3
    )
    
    print("Query:")
    print(query)
    print("\nResponse:")
    print(response)

async def main():
    """
    Run all examples.
    """
    print("=== Basic RAG Usage Example ===")
    await example_basic_rag_usage()
    
    print("\n=== Advanced Chunking Example ===")
    await example_advanced_chunking()
    
    print("\n=== Advanced Retrieval Example ===")
    await example_advanced_retrieval()
    
    print("\n=== RAG Chain Example ===")
    await example_rag_chain()

if __name__ == "__main__":
    asyncio.run(main())