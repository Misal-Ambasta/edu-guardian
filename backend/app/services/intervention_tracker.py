
"""Intervention Tracker module for the application.

This module provides functionality related to intervention tracker.
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from ..models.intervention import Intervention
from ..models.student_journey import StudentJourney
from ..emotion_analysis.analyzer import EmotionProfile
import uuid

class EmotionBasedInterventionTracker:
    """
    Tracks and analyzes the emotional outcomes of interventions
    """

    def __init__(self, db: Session):
        self.db = db

    async def track_emotion_intervention_outcome(
        self, intervention_id: str, student_id: str) -> Dict[str, float]:
        """
        Track the emotional outcome of an intervention by comparing before and after emotional states

        Args:
            intervention_id: The ID of the intervention to track
            student_id: The ID of the student who received the intervention

        Returns:
            Dict containing emotional improvement metrics
        """
        # Get before/after emotional states
        before_emotions = await self.get_pre_intervention_emotions(student_id, intervention_id)
        after_emotions = await self.get_post_intervention_emotions(student_id, intervention_id)

        if not before_emotions or not after_emotions:
            return {"error": "Could not find before and after emotional states"}

        # Calculate emotional improvement metrics
        emotion_improvements = {
            'frustration_reduction': before_emotions.frustration_level - after_emotions.frustration_level,
            'confidence_increase': after_emotions.confidence_level - before_emotions.confidence_level,
            'urgency_de_escalation': self.calculate_urgency_reduction(
                before_emotions, after_emotions),
            'hidden_dissatisfaction_resolved': self.check_hidden_dissatisfaction_resolution(
                before_emotions, after_emotions),
            'emotional_stability_improvement': self.calculate_stability_improvement(
                before_emotions, after_emotions),
            'engagement_improvement': after_emotions.engagement_level - before_emotions.engagement_level,
            'satisfaction_improvement': after_emotions.satisfaction_level - before_emotions.satisfaction_level,
            'overall_emotional_improvement': self.calculate_overall_improvement(
                before_emotions, after_emotions)
        }

        # Update intervention effectiveness database
        await self.update_intervention_effectiveness(intervention_id, emotion_improvements)

        return emotion_improvements

    async def get_pre_intervention_emotions(
        self, student_id: str, intervention_id: str) -> Optional[EmotionProfile]:
        """
        Get the emotional state of a student before an intervention
        """
        # Get the intervention to find when it was applied
        intervention = self.db.query(
            Intervention).filter(Intervention.id == uuid.UUID(intervention_id)).first()

        if not intervention:
            return None

        # Get the student journey entry before the intervention
        student_journey = self.db.query(StudentJourney).filter(
            StudentJourney.student_id == student_id,
            StudentJourney.week_number == intervention.recommended_week
        ).order_by(StudentJourney.timestamp.desc()).first()

        if not student_journey:
            return None

        # Convert to EmotionProfile
        return EmotionProfile(
            frustration_level=student_journey.frustration_level,
            engagement_level=student_journey.engagement_level,
            confidence_level=student_journey.confidence_level,
            satisfaction_level=student_journey.satisfaction_level,
            frustration_type=student_journey.frustration_type,
            frustration_intensity=student_journey.frustration_intensity,
            frustration_trend=student_journey.frustration_trend,
            urgency_level=student_journey.urgency_level,
            urgency_signals=student_journey.urgency_signals or [],
            response_urgency=student_journey.response_urgency,
            emotional_temperature=student_journey.emotional_temperature,
            emotional_volatility=student_journey.emotional_volatility,
            emotional_trajectory=student_journey.emotional_trajectory,
            hidden_dissatisfaction_flag=student_journey.hidden_dissatisfaction_flag,
            hidden_dissatisfaction_confidence=student_journey.hidden_dissatisfaction_confidence,
            hidden_signals=student_journey.hidden_signals or [],
            politeness_mask_level=student_journey.politeness_mask_level,
            dropout_risk_emotions=student_journey.dropout_risk_emotions or [],
            positive_recovery_indicators=student_journey.positive_recovery_indicators or [],
            emotional_triggers=student_journey.emotional_triggers or [],
            emotion_coherence=student_journey.emotion_coherence,
            sentiment_authenticity=student_journey.sentiment_authenticity,
            emotional_complexity=student_journey.emotional_complexity
        )

    async def get_post_intervention_emotions(
        self, student_id: str, intervention_id: str) -> Optional[EmotionProfile]:
        """
        Get the emotional state of a student after an intervention
        """
        # Get the intervention to find when it was applied
        intervention = self.db.query(
            Intervention).filter(Intervention.id == uuid.UUID(intervention_id)).first()

        if not intervention:
            return None

        # Get the student journey entry after the intervention
        student_journey = self.db.query(StudentJourney).filter(
            StudentJourney.student_id == student_id,
            StudentJourney.week_number == intervention.applied_week + 1  # Check the week after intervention
        ).order_by(StudentJourney.timestamp.asc()).first()

        if not student_journey:
            return None

        # Convert to EmotionProfile
        return EmotionProfile(
            frustration_level=student_journey.frustration_level,
            engagement_level=student_journey.engagement_level,
            confidence_level=student_journey.confidence_level,
            satisfaction_level=student_journey.satisfaction_level,
            frustration_type=student_journey.frustration_type,
            frustration_intensity=student_journey.frustration_intensity,
            frustration_trend=student_journey.frustration_trend,
            urgency_level=student_journey.urgency_level,
            urgency_signals=student_journey.urgency_signals or [],
            response_urgency=student_journey.response_urgency,
            emotional_temperature=student_journey.emotional_temperature,
            emotional_volatility=student_journey.emotional_volatility,
            emotional_trajectory=student_journey.emotional_trajectory,
            hidden_dissatisfaction_flag=student_journey.hidden_dissatisfaction_flag,
            hidden_dissatisfaction_confidence=student_journey.hidden_dissatisfaction_confidence,
            hidden_signals=student_journey.hidden_signals or [],
            politeness_mask_level=student_journey.politeness_mask_level,
            dropout_risk_emotions=student_journey.dropout_risk_emotions or [],
            positive_recovery_indicators=student_journey.positive_recovery_indicators or [],
            emotional_triggers=student_journey.emotional_triggers or [],
            emotion_coherence=student_journey.emotion_coherence,
            sentiment_authenticity=student_journey.sentiment_authenticity,
            emotional_complexity=student_journey.emotional_complexity
        )

    def calculate_urgency_reduction(self, before: EmotionProfile, after: EmotionProfile) -> float:
        """
        Calculate the reduction in urgency level
        """
        urgency_levels = {
            'low': 0.2,
            'medium': 0.4,
            'high': 0.6,
            'critical': 0.8,
            'immediate': 1.0
        }

        before_urgency = urgency_levels.get(before.urgency_level.lower(), 0.0)
        after_urgency = urgency_levels.get(after.urgency_level.lower(), 0.0)

        return max(0.0, before_urgency - after_urgency)

    def check_hidden_dissatisfaction_resolution(
        self, before: EmotionProfile, after: EmotionProfile) -> float:
        """
        Check if hidden dissatisfaction was resolved
        """
        if before.hidden_dissatisfaction_flag and not after.hidden_dissatisfaction_flag:
            return 1.0  # Fully resolved
        elif before.hidden_dissatisfaction_flag and after.hidden_dissatisfaction_flag:
            # Calculate improvement based on confidence reduction
            return max(
                0.0, before.hidden_dissatisfaction_confidence - after.hidden_dissatisfaction_confidence)
        return 0.0  # No hidden dissatisfaction to resolve

    def calculate_stability_improvement(
        self, before: EmotionProfile, after: EmotionProfile) -> float:
        """
        Calculate improvement in emotional stability
        """
        # Lower volatility means more stability
        return max(0.0, before.emotional_volatility - after.emotional_volatility)

    def calculate_overall_improvement(self, before: EmotionProfile, after: EmotionProfile) -> float:
        """
        Calculate overall emotional improvement
        """
        # Weighted average of key emotional dimensions
        weights = {
            'frustration': 0.3,
            'confidence': 0.2,
            'engagement': 0.2,
            'satisfaction': 0.3
        }

        frustration_improvement = max(0.0, before.frustration_level - after.frustration_level)
        confidence_improvement = max(0.0, after.confidence_level - before.confidence_level)
        engagement_improvement = max(0.0, after.engagement_level - before.engagement_level)
        satisfaction_improvement = max(0.0, after.satisfaction_level - before.satisfaction_level)

        weighted_sum = (
            weights['frustration'] * frustration_improvement +
            weights['confidence'] * confidence_improvement +
            weights['engagement'] * engagement_improvement +
            weights['satisfaction'] * satisfaction_improvement
        )

        return weighted_sum

    async def update_intervention_effectiveness(
        self, intervention_id: str, emotion_improvements: Dict[str, float]) -> None:
        """
        Update the intervention record with effectiveness metrics
        """
        intervention = self.db.query(
            Intervention).filter(Intervention.id == uuid.UUID(intervention_id)).first()

        if not intervention:
            return

        # Update the emotion improvement field
        intervention.emotion_improvement = emotion_improvements

        # Determine outcome status based on overall improvement
        overall_improvement = emotion_improvements.get('overall_emotional_improvement', 0.0)
        if overall_improvement >= 0.5:
            intervention.outcome_status = 'successful'
        elif overall_improvement >= 0.2:
            intervention.outcome_status = 'partial'
        else:
            intervention.outcome_status = 'failed'

        self.db.commit()

    async def get_template_performance(
        self, template_name: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get performance metrics for intervention templates
        """
        query = self.db.query(Intervention)

        if template_name:
            # Filter by template name if provided
            query = query.filter(
                Intervention.intervention_details['template_name'].astext == template_name)

        # Get interventions with outcome status
        interventions = query.filter(Intervention.outcome_status.isnot(None)).all()

        # Group by template
        template_stats = {}
        for intervention in interventions:
            template_name = intervention.intervention_details.get('template_name', 'unknown')

            if template_name not in template_stats:
                template_stats[template_name] = {
                    'template_name': template_name,
                    'usage_count': 0,
                    'success_count': 0,
                    'partial_count': 0,
                    'failure_count': 0,
                    'total_emotion_improvement': 0.0,
                    'average_response_time': 0.0,
                    'total_response_time': 0.0
                }

            stats = template_stats[template_name]
            stats['usage_count'] += 1

            if intervention.outcome_status == 'successful':
                stats['success_count'] += 1
            elif intervention.outcome_status == 'partial':
                stats['partial_count'] += 1
            else:
                stats['failure_count'] += 1

            # Add emotion improvement if available
            if intervention.emotion_improvement and 'overall_emotional_improvement' in intervention.emotion_improvement:
                stats['total_emotion_improvement'] += intervention.emotion_improvement['overall_emotional_improvement']

            # Add response time if available
            if intervention.response_time_hours is not None:
                stats['total_response_time'] += intervention.response_time_hours

        # Calculate averages and success rates
        results = []
        for template_name, stats in template_stats.items():
            if stats['usage_count'] > 0:
                stats['success_rate'] = stats['success_count'] / stats['usage_count']
                stats['average_emotion_improvement'] = stats['total_emotion_improvement'] / stats['usage_count']
                stats['average_response_time'] = stats['total_response_time'] / stats['usage_count']
            else:
                stats['success_rate'] = 0.0
                stats['average_emotion_improvement'] = 0.0
                stats['average_response_time'] = 0.0

            results.append(stats)

        # Sort by success rate (highest first)
        results.sort(key=lambda x: x['success_rate'], reverse=True)

        return results[:limit]

    async def get_intervention_timing_analysis(self) -> Dict[str, Any]:
        """
        Analyze intervention timing and its impact on success
        """
        interventions = self.db.query(
            Intervention).filter(Intervention.outcome_status.isnot(None)).all()

        # Group by urgency level
        urgency_timing = {}
        for intervention in interventions:
            urgency = intervention.emotional_urgency_level or 'unknown'

            if urgency not in urgency_timing:
                urgency_timing[urgency] = {
                    'urgency_level': urgency,
                    'total_count': 0,
                    'success_count': 0,
                    'total_response_time': 0.0,
                    'average_response_time': 0.0,
                    'success_rate': 0.0
                }

            stats = urgency_timing[urgency]
            stats['total_count'] += 1

            if intervention.outcome_status == 'successful':
                stats['success_count'] += 1

            if intervention.response_time_hours is not None:
                stats['total_response_time'] += intervention.response_time_hours

        # Calculate averages and success rates
        for urgency, stats in urgency_timing.items():
            if stats['total_count'] > 0:
                stats['success_rate'] = stats['success_count'] / stats['total_count']
                stats['average_response_time'] = stats['total_response_time'] / stats['total_count']

        # Analyze correlation between response time and success
        fast_interventions = [i for i in interventions if i.response_time_hours is not None and i.response_time_hours < 24]
        slow_interventions = [i for i in interventions if i.response_time_hours is not None and i.response_time_hours >= 24]

        fast_success_rate = 0.0
        if fast_interventions:
            fast_success_rate = len(
                [i for i in fast_interventions if i.outcome_status == 'successful']) / len(
                    fast_interventions)

        slow_success_rate = 0.0
        if slow_interventions:
            slow_success_rate = len(
                [i for i in slow_interventions if i.outcome_status == 'successful']) / len(
                    slow_interventions)

        return {
            'urgency_timing': list(urgency_timing.values()),
            'fast_response_success_rate': fast_success_rate,
            'slow_response_success_rate': slow_success_rate,
            'response_time_impact': fast_success_rate - slow_success_rate
        }
