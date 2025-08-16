import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the parent directory to sys.path to allow importing from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.models.emotion import EmotionProfile
from app.services.enhanced_rag import EnhancedRAGService
from app.services.chunking_strategies import ChunkingStrategies

# Load environment variables
load_dotenv()

async def test_enhanced_rag():
    """
    Simple test to verify the enhanced RAG implementation works correctly.
    """
    # Get API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        return False
    
    try:
        # Initialize RAG service
        print("Initializing RAG service...")
        rag_service = EnhancedRAGService(api_key=api_key)
        await rag_service.initialize_vector_stores()
        print("RAG service initialized successfully.")
        
        # Create a sample emotion profile
        print("Creating sample emotion profile...")
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
        
        # Test chunking strategies
        print("Testing chunking strategies...")
        metadata = {
            "student_id": "test_student",
            "course_id": "test_course",
            "week_number": 1,
            "document_id": "test_doc"
        }
        
        chunks = ChunkingStrategies.emotion_profile_to_chunks(emotion_profile.dict(), metadata)
        print(f"Created {len(chunks)} chunks from emotion profile.")
        
        # Test adding emotion profile to vector store
        print("Testing adding emotion profile to vector store...")
        document_id = await rag_service.add_emotion_profile(emotion_profile, metadata)
        print(f"Added emotion profile with document ID: {document_id}")
        
        # Test generating insights
        print("Testing generating insights...")
        query = "What are the main emotional challenges faced by this student?"
        similar_patterns = [{
            "emotion_profile": emotion_profile.dict(),
            "student_id": "test_student",
            "course_id": "test_course",
            "week_number": 1,
            "similarity_score": 1.0
        }]
        
        insights = await rag_service.generate_insights_from_patterns(query, similar_patterns)
        print("Generated insights:")
        print(insights)
        
        # Test RAG chain
        print("\nTesting RAG chain...")
        response = await rag_service.query_with_rag(
            query="What interventions might help this student?",
            student_id="test_student",
            course_id="test_course",
            week_number=1
        )
        
        print("RAG chain response:")
        print(response)
        
        print("\nAll tests completed successfully!")
        return True
    
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_enhanced_rag())
    if success:
        print("\n✅ Enhanced RAG implementation is working correctly!")
    else:
        print("\n❌ Enhanced RAG implementation test failed!")
        sys.exit(1)