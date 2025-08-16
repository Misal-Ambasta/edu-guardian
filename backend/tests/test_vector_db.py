import pytest
from app.services.vector_db import EmotionVectorDatabase
from app.models.student_journey import EmotionProfile

class TestEmotionVectorDatabase:
    
    def setup_method(self):
        # Initialize with test collection name
        self.vector_db = EmotionVectorDatabase(collection_name="test_emotion_vectors")
    
    def test_embed_emotion_profile(self):
        # Create test emotion profile
        profile = EmotionProfile(
            frustration_level=0.7,
            engagement_level=0.6,
            confidence_level=0.5,
            satisfaction_level=0.4,
            frustration_type="technical",
            frustration_intensity="moderate",
            frustration_trend="increasing",
            urgency_level="medium",
            urgency_signals=["missed_deadlines", "help_requests"],
            response_urgency="same_day",
            emotional_temperature=0.6,
            emotional_volatility=0.5,
            emotional_trajectory="declining",
            hidden_dissatisfaction_flag=True,
            hidden_dissatisfaction_confidence=0.8,
            hidden_signals=["faint_praise", "diplomatic_language"],
            politeness_mask_level=0.7,
            dropout_risk_emotions=["helplessness", "overwhelm"],
            positive_recovery_indicators=[],
            emotional_triggers=["technical_issues"],
            emotion_coherence=0.6,
            sentiment_authenticity=0.7,
            emotional_complexity="mixed"
        )
        
        # Test embedding generation
        embedding = self.vector_db.embed_emotion_profile(profile)
        
        # Verify result
        assert isinstance(embedding, list)
        assert len(embedding) > 0
    
    def test_add_emotion_profile(self, mocker):
        # Mock the ChromaDB client
        mock_collection = mocker.MagicMock()
        mocker.patch.object(self.vector_db, 'collection', mock_collection)
        
        # Create test emotion profile
        profile = EmotionProfile(
            frustration_level=0.7,
            engagement_level=0.6,
            confidence_level=0.5,
            satisfaction_level=0.4,
            frustration_type="technical",
            frustration_intensity="moderate",
            frustration_trend="increasing",
            urgency_level="medium",
            urgency_signals=["missed_deadlines", "help_requests"],
            response_urgency="same_day",
            emotional_temperature=0.6,
            emotional_volatility=0.5,
            emotional_trajectory="declining",
            hidden_dissatisfaction_flag=True,
            hidden_dissatisfaction_confidence=0.8,
            hidden_signals=["faint_praise", "diplomatic_language"],
            politeness_mask_level=0.7,
            dropout_risk_emotions=["helplessness", "overwhelm"],
            positive_recovery_indicators=[],
            emotional_triggers=["technical_issues"],
            emotion_coherence=0.6,
            sentiment_authenticity=0.7,
            emotional_complexity="mixed"
        )
        
        # Test adding profile
        self.vector_db.add_emotion_profile("test_student_1", profile, "test_course", 3)
        
        # Verify collection.add was called
        mock_collection.add.assert_called_once()
    
    def test_find_similar_emotion_patterns(self, mocker):
        # Mock the ChromaDB client
        mock_collection = mocker.MagicMock()
        mock_collection.query.return_value = {
            'ids': ['test_student_2', 'test_student_3'],
            'distances': [0.1, 0.2],
            'metadatas': [
                {'student_id': 'test_student_2', 'course_id': 'test_course', 'week_number': 2},
                {'student_id': 'test_student_3', 'course_id': 'test_course', 'week_number': 4}
            ]
        }
        mocker.patch.object(self.vector_db, 'collection', mock_collection)
        
        # Create test emotion profile
        profile = EmotionProfile(
            frustration_level=0.7,
            engagement_level=0.6,
            confidence_level=0.5,
            satisfaction_level=0.4,
            frustration_type="technical",
            frustration_intensity="moderate",
            frustration_trend="increasing",
            urgency_level="medium",
            urgency_signals=["missed_deadlines", "help_requests"],
            response_urgency="same_day",
            emotional_temperature=0.6,
            emotional_volatility=0.5,
            emotional_trajectory="declining",
            hidden_dissatisfaction_flag=True,
            hidden_dissatisfaction_confidence=0.8,
            hidden_signals=["faint_praise", "diplomatic_language"],
            politeness_mask_level=0.7,
            dropout_risk_emotions=["helplessness", "overwhelm"],
            positive_recovery_indicators=[],
            emotional_triggers=["technical_issues"],
            emotion_coherence=0.6,
            sentiment_authenticity=0.7,
            emotional_complexity="mixed"
        )
        
        # Test finding similar patterns
        results = self.vector_db.find_similar_emotion_patterns(profile, limit=2)
        
        # Verify result
        assert isinstance(results, list)
        assert len(results) == 2
        assert results[0]['student_id'] == 'test_student_2'
        assert results[1]['student_id'] == 'test_student_3'