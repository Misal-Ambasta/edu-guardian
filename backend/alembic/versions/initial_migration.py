"""Initial database migration

Revision ID: 001
Revises: 
Create Date: 2023-04-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create Users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_superuser', sa.Boolean(), default=False),
        sa.Column('full_name', sa.String()),
        sa.Column('role', sa.String()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Create StudentJourneys table
    op.create_table(
        'student_journeys',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('student_id', sa.String(), nullable=False, index=True),
        sa.Column('course_id', sa.String(), nullable=False, index=True),
        sa.Column('feedback_week', sa.Integer(), nullable=False),
        sa.Column('nps_score', sa.Integer()),
        sa.Column('satisfaction_score', sa.Integer()),
        sa.Column('primary_emotion', sa.String()),
        sa.Column('secondary_emotion', sa.String()),
        
        # NPS & Traditional metrics
        sa.Column('would_recommend', sa.Boolean()),
        sa.Column('ease_of_use_score', sa.Integer()),
        sa.Column('instructor_rating', sa.Integer()),
        sa.Column('content_quality_rating', sa.Integer()),
        
        # Emotional intelligence metrics
        sa.Column('frustration_level', sa.Integer()),
        sa.Column('frustration_type', sa.String()),
        sa.Column('frustration_source', sa.String()),
        sa.Column('frustration_urgency', sa.String()),
        sa.Column('hidden_dissatisfaction_flag', sa.Boolean()),
        sa.Column('hidden_dissatisfaction_confidence', sa.Float()),
        sa.Column('sentiment_score', sa.Float()),
        sa.Column('emotional_intensity', sa.Integer()),
        sa.Column('emotional_volatility', sa.Float()),
        sa.Column('emotional_temperature', sa.Integer()),
        sa.Column('risk_score', sa.Float()),
        sa.Column('expected_action_required', sa.Boolean()),
        sa.Column('expected_action_timeframe', sa.String()),
        
        # Semantic & content analysis
        sa.Column('keywords', ARRAY(sa.String())),
        sa.Column('feedback_topics', JSONB),
        sa.Column('raw_feedback_text', sa.Text()),
        sa.Column('processed_feedback_vector', JSONB),
        sa.Column('emotional_phrases', JSONB),
        
        # Student journey context
        sa.Column('progress_percentage', sa.Float()),
        sa.Column('completion_risk', sa.String()),
        sa.Column('previous_week_change', sa.Float()),
        sa.Column('emotional_trend', sa.String()),
        sa.Column('intervention_recommended', sa.Boolean()),
        sa.Column('intervention_type', sa.String()),
        sa.Column('support_priority', sa.Integer()),
        
        # Metadata
        sa.Column('feedback_timestamp', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now())
    )
    
    # Create WeeklyNPSReports table
    op.create_table(
        'weekly_nps_reports',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('course_id', sa.String(), nullable=False, index=True),
        sa.Column('week_number', sa.Integer(), nullable=False),
        sa.Column('report_date', sa.Date(), nullable=False),
        sa.Column('total_students', sa.Integer()),
        sa.Column('responding_students', sa.Integer()),
        
        # Aggregated NPS & Traditional metrics
        sa.Column('avg_nps_score', sa.Float()),
        sa.Column('promoters_count', sa.Integer()),
        sa.Column('passives_count', sa.Integer()),
        sa.Column('detractors_count', sa.Integer()),
        sa.Column('avg_satisfaction', sa.Float()),
        sa.Column('avg_ease_of_use', sa.Float()),
        sa.Column('avg_instructor_rating', sa.Float()),
        sa.Column('avg_content_quality', sa.Float()),
        
        # Aggregated Emotional intelligence metrics
        sa.Column('emotion_distribution', JSONB),
        sa.Column('avg_frustration_level', sa.Float()),
        sa.Column('frustration_type_distribution', JSONB),
        sa.Column('high_frustration_count', sa.Integer()),
        sa.Column('hidden_dissatisfaction_count', sa.Integer()),
        sa.Column('avg_emotional_temperature', sa.Float()),
        sa.Column('high_risk_students_count', sa.Integer()),
        sa.Column('avg_risk_score', sa.Float()),
        sa.Column('intervention_recommended_count', sa.Integer()),
        
        # Semantic analysis aggregates
        sa.Column('top_keywords', JSONB),
        sa.Column('top_feedback_topics', JSONB),
        sa.Column('emotional_phrase_clusters', JSONB),
        
        # Trend assessment
        sa.Column('predicted_dropout_count', sa.Integer()),
        sa.Column('satisfaction_trend', sa.String()),
        sa.Column('emotional_health_trend', sa.String()),
        sa.Column('emotional_health_score', sa.Float()),
        
        # Metadata
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now())
    )
    
    # Create StudentOutcomes table
    op.create_table(
        'student_outcomes',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('student_id', sa.String(), nullable=False, index=True),
        sa.Column('course_id', sa.String(), nullable=False, index=True),
        
        # Outcome metrics
        sa.Column('completed_course', sa.Boolean()),
        sa.Column('completion_week', sa.Integer()),
        sa.Column('final_grade', sa.String()),
        sa.Column('performance_category', sa.String()),  # 'excellent', 'good', 'average', 'poor'
        sa.Column('time_to_completion_weeks', sa.Integer()),
        
        # Emotional journey summary
        sa.Column('emotion_journey_summary', JSONB),
        sa.Column('avg_emotional_temperature', sa.Float()),
        sa.Column('max_frustration_level', sa.Integer()),
        sa.Column('weeks_with_high_frustration', sa.Integer()),
        sa.Column('weeks_with_hidden_dissatisfaction', sa.Integer()),
        sa.Column('emotional_recovery_pattern', sa.String()),  # 'quick', 'gradual', 'none'
        sa.Column('emotional_volatility_avg', sa.Float()),
        
        # Interventions & impact
        sa.Column('total_interventions', sa.Integer()),
        sa.Column('successful_interventions', sa.Integer()),
        sa.Column('intervention_effectiveness', sa.Float()),
        sa.Column('key_turning_point_week', sa.Integer()),
        
        # Retention metrics
        sa.Column('would_have_dropped_prediction', sa.Boolean()),
        sa.Column('retention_value', sa.Float()),
        
        # Metadata
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now())
    )
    
    # Create Interventions table
    op.create_table(
        'interventions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('student_id', sa.String(), nullable=False, index=True),
        sa.Column('intervention_type', sa.String(), nullable=False),
        sa.Column('target_aspect', sa.String()),
        
        # Emotion-based targeting
        sa.Column('target_emotion', sa.String()),
        sa.Column('emotional_urgency_level', sa.String()),
        sa.Column('intervention_urgency', sa.String()),
        
        sa.Column('recommended_week', sa.Integer()),
        sa.Column('applied_week', sa.Integer()),
        sa.Column('intervention_details', JSONB),
        
        # Enhanced outcome tracking
        sa.Column('success_metrics', JSONB),
        sa.Column('emotion_improvement', JSONB),
        sa.Column('outcome_status', sa.String()),
        
        # Timing analysis
        sa.Column('response_time_hours', sa.Float()),
        sa.Column('intervention_to_improvement_days', sa.Integer()),
        
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Create HistoricalPatterns table
    op.create_table(
        'historical_patterns',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('pattern_name', sa.String(), nullable=False),
        sa.Column('pattern_type', sa.String(), nullable=False),
        
        # Pattern definition
        sa.Column('detection_rules', JSONB, nullable=False),
        sa.Column('confidence_threshold', sa.Float()),
        
        # Emotion intelligence metrics
        sa.Column('emotion_signatures', JSONB),
        sa.Column('early_warning_indicators', ARRAY(sa.String())),
        
        # Efficacy tracking
        sa.Column('success_rate', sa.Float()),
        sa.Column('false_positive_rate', sa.Float()),
        sa.Column('avg_detection_week', sa.Float()),
        
        # Risk assessment
        sa.Column('business_impact', sa.String()),
        sa.Column('student_impact', sa.String()),
        sa.Column('typical_outcome', sa.String()),
        
        # Intervention efficacy
        sa.Column('recommended_interventions', JSONB),
        sa.Column('avg_intervention_efficacy', sa.Float()),
        
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now())
    )


def downgrade() -> None:
    op.drop_table('historical_patterns')
    op.drop_table('interventions')
    op.drop_table('student_outcomes')
    op.drop_table('weekly_nps_reports')
    op.drop_table('student_journeys')
    op.drop_table('users')
