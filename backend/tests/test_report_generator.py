import pytest
from datetime import datetime
from app.services.report_generator import WeeklyNPSReportGenerator
from app.models.weekly_report import WeeklyNPSReport

class TestWeeklyNPSReportGenerator:
    
    def setup_method(self, db_session):
        self.report_generator = WeeklyNPSReportGenerator(db_session)
    
    def test_generate_weekly_report(self, mocker):
        # Mock the necessary methods
        mocker.patch.object(
            self.report_generator, 'collect_week_data', 
            return_value={
                'course_id': 'test_course',
                'week_number': 3,
                'responses': [{'nps_score': 8}, {'nps_score': 7}, {'nps_score': 9}],
                'aspect_scores': {
                    'lms_usability': 3.5,
                    'instructor_quality': 4.2,
                    'content_difficulty': 3.8,
                    'support_quality': 3.9,
                    'course_pace': 3.7
                }
            }
        )
        
        # Test report generation
        report = self.report_generator.generate_weekly_report('test_course', 3)
        
        # Verify result
        assert isinstance(report, WeeklyNPSReport)
        assert report.course_id == 'test_course'
        assert report.week_number == 3
        assert report.overall_nps > 0
        assert report.report_confidence > 0
    
    def test_create_executive_summary(self, mocker):
        # Mock data
        raw_data = {
            'course_id': 'test_course',
            'week_number': 3,
            'responses': [{'nps_score': 8}, {'nps_score': 7}, {'nps_score': 9}],
            'aspect_scores': {
                'lms_usability': 3.5,
                'instructor_quality': 4.2,
                'content_difficulty': 3.8,
                'support_quality': 3.9,
                'course_pace': 3.7
            }
        }
        
        ai_insights = [
            {'insight_text': 'Test insight 1', 'confidence_level': 0.9},
            {'insight_text': 'Test insight 2', 'confidence_level': 0.8}
        ]
        
        # Test executive summary creation
        summary = self.report_generator.create_executive_summary(raw_data, ai_insights)
        
        # Verify result
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert 'WEEKLY NPS INTELLIGENCE REPORT' in summary
    
    def test_analyze_emotions(self, mocker):
        # Mock data
        raw_data = {
            'responses': [
                {
                    'frustration_level': 0.7,
                    'engagement_level': 0.6,
                    'confidence_level': 0.5,
                    'satisfaction_level': 0.4,
                    'urgency_level': 'medium',
                    'hidden_dissatisfaction_flag': True
                },
                {
                    'frustration_level': 0.3,
                    'engagement_level': 0.8,
                    'confidence_level': 0.7,
                    'satisfaction_level': 0.9,
                    'urgency_level': 'low',
                    'hidden_dissatisfaction_flag': False
                }
            ]
        }
        
        # Test emotion analysis
        emotion_analysis = self.report_generator.analyze_emotions(raw_data)
        
        # Verify result
        assert isinstance(emotion_analysis, dict)
        assert 'average_frustration_level' in emotion_analysis
        assert 'hidden_dissatisfaction_count' in emotion_analysis
        assert 'urgency_breakdown' in emotion_analysis