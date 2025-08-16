import unittest
import os
import json
from unittest.mock import patch, MagicMock

from app.services.vector_db_factory import VectorDBFactory
from app.services.gemini_vector_db import GeminiVectorDBService, GeminiEmotionEmbeddings
from app.emotion_analysis.analyzer import EmotionProfile

class TestGeminiVectorDB(unittest.TestCase):
    
    def setUp(self):
        # Create a mock environment with API key
        self.env_patcher = patch.dict('os.environ', {'GOOGLE_API_KEY': 'fake-api-key'})
        self.env_patcher.start()
        
        # Mock the Google Generative AI client
        self.genai_patcher = patch('google.generativeai.GenerativeModel')
        self.mock_genai = self.genai_patcher.start()
        
        # Mock the embedding function
        self.embedding_patcher = patch('langchain_google_genai.GoogleGenerativeAIEmbeddings')
        self.mock_embedding = self.embedding_patcher.start()
        
        # Setup mock embedding function
        self.mock_embedding_instance = MagicMock()
        self.mock_embedding.return_value = self.mock_embedding_instance
        self.mock_embedding_instance.embed_documents.return_value = [[0.1, 0.2, 0.3]]
        self.mock_embedding_instance.embed_query.return_value = [0.1, 0.2, 0.3]
        
        # Mock Chroma client
        self.chroma_patcher = patch('chromadb.PersistentClient')
        self.mock_chroma = self.chroma_patcher.start()
        
        # Setup mock collection
        self.mock_collection = MagicMock()
        self.mock_chroma.return_value.get_or_create_collection.return_value = self.mock_collection
        
    def tearDown(self):
        self.env_patcher.stop()
        self.genai_patcher.stop()
        self.embedding_patcher.stop()
        self.chroma_patcher.stop()
    
    def test_factory_creates_gemini_service(self):
        # Test that the factory creates a GeminiVectorDBService
        service = VectorDBFactory.create_vector_db_service()
        self.assertIsInstance(service, GeminiVectorDBService)
    
    def test_factory_raises_error_when_api_key_not_set(self):
        # Test that the factory raises an error when GOOGLE_API_KEY is not set
        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(ValueError) as context:
                VectorDBFactory.create_vector_db_service()
            self.assertTrue('GOOGLE_API_KEY environment variable not set' in str(context.exception))
    
    def test_gemini_embeddings(self):
        # Test that GeminiEmotionEmbeddings correctly processes emotion profiles
        embeddings = GeminiEmotionEmbeddings()
        
        # Create a test emotion profile
        emotion_profile = EmotionProfile(
            frustration_level=0.7,
            engagement_level=0.8,
            confidence_level=0.6,
            satisfaction_level=0.5,
            emotional_temperature=0.65,
            emotional_volatility=0.3,
            hidden_dissatisfaction_flag=True,
            urgency_level="high",
            frustration_type="conceptual",
            emotional_trajectory="declining"
        )
        
        # Test embedding generation
        embedding = embeddings.embed_emotion_profile(emotion_profile)
        
        # Verify the mock was called with the correct data
        self.mock_embedding_instance.embed_query.assert_called_once()
        call_args = self.mock_embedding_instance.embed_query.call_args[0][0]
        
        # Verify the embedding contains all the emotion profile data
        self.assertIn("frustration_level: 0.7", call_args)
        self.assertIn("engagement_level: 0.8", call_args)
        self.assertIn("hidden_dissatisfaction_flag: True", call_args)
        self.assertIn("urgency_level: high", call_args)
    
    def test_store_emotion_pattern(self):
        # Test storing an emotion pattern
        service = GeminiVectorDBService()
        
        # Create a test emotion profile
        emotion_profile = EmotionProfile(
            frustration_level=0.7,
            engagement_level=0.8,
            confidence_level=0.6,
            satisfaction_level=0.5,
            emotional_temperature=0.65,
            emotional_volatility=0.3,
            hidden_dissatisfaction_flag=True,
            urgency_level="high",
            frustration_type="conceptual",
            emotional_trajectory="declining"
        )
        
        # Store the emotion pattern
        document_id = service.store_emotion_pattern(
            student_id="test_student",
            course_id="test_course",
            week_number=1,
            emotion_profile=emotion_profile
        )
        
        # Verify the document was added to the collection
        self.mock_collection.add.assert_called_once()
        
        # Check that the document ID was returned
        self.assertEqual(document_id, "test_student_test_course_1")
    
    def test_find_similar_students(self):
        # Test finding similar students
        service = GeminiVectorDBService()
        
        # Mock the query response
        self.mock_collection.query.return_value = {
            'ids': [['doc1', 'doc2']],
            'distances': [[0.1, 0.2]],
            'metadatas': [[{
                'student_id': 'student1',
                'course_id': 'course1',
                'week_number': '1'
            }, {
                'student_id': 'student2',
                'course_id': 'course1',
                'week_number': '1'
            }]],
            'documents': [[json.dumps({
                'frustration_level': 0.7,
                'engagement_level': 0.8
            }), json.dumps({
                'frustration_level': 0.6,
                'engagement_level': 0.7
            })]]
        }
        
        # Create a test emotion profile
        emotion_profile = EmotionProfile(
            frustration_level=0.7,
            engagement_level=0.8,
            confidence_level=0.6,
            satisfaction_level=0.5,
            emotional_temperature=0.65,
            emotional_volatility=0.3,
            hidden_dissatisfaction_flag=True,
            urgency_level="high",
            frustration_type="conceptual",
            emotional_trajectory="declining"
        )
        
        # Find similar students
        result = service.find_emotion_similar_students(
            student_id="test_student",
            course_id="test_course",
            week_number=1,
            limit=2
        )
        
        # Verify the query was called
        self.mock_collection.query.assert_called_once()
        
        # Check the result format
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['metadata']['student_id'], 'student1')
        self.assertEqual(result[1]['metadata']['student_id'], 'student2')

if __name__ == '__main__':
    unittest.main()