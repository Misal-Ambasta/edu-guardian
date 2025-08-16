"""Add indexes for performance optimization

Revision ID: 002
Revises: 001
Create Date: 2023-04-15

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Helper function to safely create an index
    def safe_create_index(index_name, table_name, columns, unique=False):
        from sqlalchemy import inspect
        from sqlalchemy.engine.reflection import Inspector
        from sqlalchemy import text
        
        # Get database connection
        conn = op.get_bind()
        
        # Check if index exists
        inspector = inspect(conn)
        existing_indexes = inspector.get_indexes(table_name)
        index_exists = any(idx['name'] == index_name for idx in existing_indexes)
        
        if not index_exists:
            try:
                if unique:
                    op.create_index(index_name, table_name, columns, unique=True)
                else:
                    op.create_index(index_name, table_name, columns)
                print(f"Created index {index_name} on {table_name}")
            except Exception as e:
                print(f"Error creating index {index_name}: {e}")
        else:
            print(f"Index {index_name} already exists on {table_name}")
    
    # Add indexes to StudentJourneys table
    safe_create_index('ix_student_journeys_primary_emotion', 'student_journeys', ['primary_emotion'])
    safe_create_index('ix_student_journeys_secondary_emotion', 'student_journeys', ['secondary_emotion'])
    safe_create_index('ix_student_journeys_feedback_week', 'student_journeys', ['feedback_week'])
    safe_create_index('ix_student_journeys_student_course_week', 'student_journeys', ['student_id', 'course_id', 'feedback_week'], unique=True)
    
    # Add indexes to Interventions table
    safe_create_index('ix_interventions_student_id', 'interventions', ['student_id'])
    safe_create_index('ix_interventions_course_id', 'interventions', ['course_id'])
    safe_create_index('ix_interventions_intervention_type', 'interventions', ['intervention_type'])
    safe_create_index('ix_interventions_status', 'interventions', ['status'])
    safe_create_index('ix_interventions_created_at', 'interventions', ['created_at'])
    
    # Add indexes to WeeklyReports table
    safe_create_index('ix_weekly_reports_course_id', 'weekly_reports', ['course_id'])
    safe_create_index('ix_weekly_reports_week_number', 'weekly_reports', ['week_number'])
    safe_create_index('ix_weekly_reports_course_week', 'weekly_reports', ['course_id', 'week_number'], unique=True)
    
    # Add indexes to HistoricalPatterns table
    safe_create_index('ix_historical_patterns_pattern_type', 'historical_patterns', ['pattern_type'])
    safe_create_index('ix_historical_patterns_student_id', 'historical_patterns', ['student_id'])
    safe_create_index('ix_historical_patterns_course_id', 'historical_patterns', ['course_id'])


def downgrade() -> None:
    # Remove indexes from StudentJourneys table
    op.drop_index('ix_student_journeys_primary_emotion', table_name='student_journeys')
    op.drop_index('ix_student_journeys_secondary_emotion', table_name='student_journeys')
    op.drop_index('ix_student_journeys_feedback_week', table_name='student_journeys')
    op.drop_index('ix_student_journeys_student_course_week', table_name='student_journeys')
    
    # Remove indexes from Interventions table
    op.drop_index('ix_interventions_student_id', table_name='interventions')
    op.drop_index('ix_interventions_course_id', table_name='interventions')
    op.drop_index('ix_interventions_intervention_type', table_name='interventions')
    op.drop_index('ix_interventions_status', table_name='interventions')
    op.drop_index('ix_interventions_created_at', table_name='interventions')
    
    # Remove indexes from WeeklyReports table
    op.drop_index('ix_weekly_reports_course_id', table_name='weekly_reports')
    op.drop_index('ix_weekly_reports_week_number', table_name='weekly_reports')
    op.drop_index('ix_weekly_reports_course_week', table_name='weekly_reports')
    
    # Remove indexes from HistoricalPatterns table
    op.drop_index('ix_historical_patterns_pattern_type', table_name='historical_patterns')
    op.drop_index('ix_historical_patterns_student_id', table_name='historical_patterns')
    op.drop_index('ix_historical_patterns_course_id', table_name='historical_patterns')