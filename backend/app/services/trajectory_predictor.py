
"""Trajectory Predictor module for the application.

This module provides functionality related to trajectory predictor.
"""
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

import numpy as np

from ..models.emotion_trajectory import EmotionTrajectoryPrediction, StudentEmotionHistory
from ..models.student_journey import StudentJourney
from ..emotion_analysis.analyzer import EmotionProfile
class EmotionTrajectoryPredictor:
    """
    Predicts the evolution of student emotions over time based on historical data
    """

    def __init__(self, db: Session):
        self.db = db

    async def predict_emotion_evolution(
        self, student_emotion_history: StudentEmotionHistory) -> EmotionTrajectoryPrediction:
        """
        Analyze emotional patterns over time and predict future emotional states

        Args:
            student_emotion_history: Historical emotion data for a student

        Returns:
            EmotionTrajectoryPrediction with multi-week predictions, risk escalations, and intervention windows
        """
        # Analyze emotional patterns over time
        frustration_trajectory = self.model_frustration_curve(student_emotion_history)
        engagement_decay = self.predict_engagement_decline(student_emotion_history)
        hidden_dissatisfaction_emergence = self.predict_hidden_dissatisfaction(
            student_emotion_history)

        # Multi-week emotion predictions
        emotion_predictions = {
            'next_week': self.predict_next_week_emotions(student_emotion_history),
            'two_week': self.predict_two_week_emotions(student_emotion_history),
            'course_completion': self.predict_end_course_emotions(student_emotion_history)
        }

        # Risk escalation predictions
        risk_escalations = {
            'frustration_boiling_point': self.predict_frustration_threshold(frustration_trajectory),
            'engagement_dropout_risk': self.predict_engagement_dropout(engagement_decay),
            'hidden_to_open_dissatisfaction': self.predict_dissatisfaction_explosion(
                hidden_dissatisfaction_emergence)
        }

        # Find optimal intervention windows
        optimal_intervention_windows = self.find_intervention_windows(
            emotion_predictions,
            risk_escalations
        )

        # Calculate prediction confidence scores
        confidence_scores = self.calculate_prediction_confidence(student_emotion_history)

        return EmotionTrajectoryPrediction(
            emotion_predictions=emotion_predictions,
            risk_escalations=risk_escalations,
            optimal_intervention_windows=optimal_intervention_windows,
            confidence_scores=confidence_scores
        )

    def model_frustration_curve(self, history: StudentEmotionHistory) -> Dict[str, Any]:
        """
        Model the frustration curve over time and predict future trajectory

        Args:
            history: Historical emotion data for a student

        Returns:
            Dictionary with frustration trajectory analysis
        """
        # Extract frustration levels and weeks
        weeks = np.array(history.weeks)
        frustration_levels = np.array(history.frustration_levels)

        # Need at least 3 data points for meaningful prediction
        if len(weeks) < 3:
            return {
                'trend': 'insufficient_data',
                'prediction': None,
                'confidence': 0.0,
                'days_to_threshold': None
            }

        # Fit a polynomial regression model (degree 2 for curve)
        coeffs = np.polyfit(weeks, frustration_levels, 2)
        poly = np.poly1d(coeffs)

        # Predict next 3 weeks
        next_weeks = np.array([max(weeks) + i for i in range(1, 4)])
        predicted_frustration = poly(next_weeks)

        # Clip predictions to valid range [0, 1]
        predicted_frustration = np.clip(predicted_frustration, 0, 1)

        # Determine trend direction
        if coeffs[0] > 0.01:  # Positive quadratic term (accelerating up)
            trend = 'accelerating_increase'
        elif coeffs[0] < -0.01:  # Negative quadratic term (decelerating)
            trend = 'decelerating'
        elif coeffs[1] > 0.01:  # Positive linear term (steady increase)
            trend = 'steady_increase'
        elif coeffs[1] < -0.01:  # Negative linear term (steady decrease)
            trend = 'steady_decrease'
        else:  # Relatively flat
            trend = 'stable'

        # Calculate days to critical threshold (0.8)
        days_to_threshold = None
        threshold = 0.8

        if max(predicted_frustration) >= threshold:
            # Find where the curve crosses the threshold
            # Solve: ax^2 + bx + c = threshold
            a, b, c = coeffs
            c = c - threshold

            # Quadratic formula
            discriminant = b**2 - 4*a*c
            if discriminant >= 0:
                x1 = (-b + np.sqrt(discriminant)) / (2*a)
                x2 = (-b - np.sqrt(discriminant)) / (2*a)

                # Find the relevant root (future time point)
                current_week = max(weeks)
                future_roots = [x for x in [x1, x2] if x > current_week]

                if future_roots:
                    # Convert to days (assuming weeks are numbered consecutively)
                    weeks_to_threshold = min(future_roots) - current_week
                    days_to_threshold = int(weeks_to_threshold * 7)

        # Calculate confidence based on data quality and model fit
        r_squared = self._calculate_r_squared(weeks, frustration_levels, poly)
        data_points_factor = min(1.0, len(weeks) / 10)  # More data points = higher confidence
        confidence = r_squared * 0.7 + data_points_factor * 0.3

        return {
            'trend': trend,
            'prediction': {week: float(
                pred) for week, pred in zip(next_weeks, predicted_frustration)},
            'confidence': float(confidence),
            'days_to_threshold': days_to_threshold
        }

    def predict_engagement_decline(self, history: StudentEmotionHistory) -> Dict[str, Any]:
        """
        Predict engagement decline patterns and dropout risk

        Args:
            history: Historical emotion data for a student

        Returns:
            Dictionary with engagement decline analysis
        """
        # Extract engagement levels and weeks
        weeks = np.array(history.weeks)
        engagement_levels = np.array(history.engagement_levels)

        # Need at least 3 data points for meaningful prediction
        if len(weeks) < 3:
            return {
                'trend': 'insufficient_data',
                'prediction': None,
                'dropout_risk': 'unknown',
                'confidence': 0.0,
                'weeks_to_disengagement': None
            }

        # Fit a polynomial regression model (degree 2 for curve)
        coeffs = np.polyfit(weeks, engagement_levels, 2)
        poly = np.poly1d(coeffs)

        # Predict next 3 weeks
        next_weeks = np.array([max(weeks) + i for i in range(1, 4)])
        predicted_engagement = poly(next_weeks)

        # Clip predictions to valid range [0, 1]
        predicted_engagement = np.clip(predicted_engagement, 0, 1)

        # Determine trend and dropout risk
        if min(predicted_engagement) < 0.3:
            dropout_risk = 'high'
        elif min(predicted_engagement) < 0.5:
            dropout_risk = 'medium'
        else:
            dropout_risk = 'low'

        # Calculate weeks to critical disengagement (0.3)
        weeks_to_disengagement = None
        threshold = 0.3

        if min(predicted_engagement) <= threshold:
            # Find where the curve crosses the threshold
            a, b, c = coeffs
            c = c - threshold

            # Quadratic formula
            discriminant = b**2 - 4*a*c
            if discriminant >= 0:
                x1 = (-b + np.sqrt(discriminant)) / (2*a)
                x2 = (-b - np.sqrt(discriminant)) / (2*a)

                # Find the relevant root (future time point)
                current_week = max(weeks)
                future_roots = [x for x in [x1, x2] if x > current_week]

                if future_roots:
                    weeks_to_disengagement = min(future_roots) - current_week

        # Calculate confidence based on data quality and model fit
        r_squared = self._calculate_r_squared(weeks, engagement_levels, poly)
        data_points_factor = min(1.0, len(weeks) / 10)  # More data points = higher confidence
        confidence = r_squared * 0.7 + data_points_factor * 0.3

        return {
            'trend': 'declining' if coeffs[1] < 0 else 'improving',
            'prediction': {week: float(
                pred) for week, pred in zip(next_weeks, predicted_engagement)},
            'dropout_risk': dropout_risk,
            'confidence': float(confidence),
            'weeks_to_disengagement': float(
                weeks_to_disengagement) if weeks_to_disengagement else None
        }

    def predict_hidden_dissatisfaction(self, history: StudentEmotionHistory) -> Dict[str, Any]:
        """
        Predict the emergence of hidden dissatisfaction and its potential to become open dissatisfaction

        Args:
            history: Historical emotion data for a student

        Returns:
            Dictionary with hidden dissatisfaction analysis
        """
        # Extract hidden dissatisfaction flags and weeks
        weeks = history.weeks
        hidden_flags = history.hidden_dissatisfaction_flags
        satisfaction_levels = history.satisfaction_levels
        frustration_levels = history.frustration_levels

        # Need at least 3 data points for meaningful prediction
        if len(weeks) < 3:
            return {
                'risk': 'insufficient_data',
                'explosion_probability': 0.0,
                'days_to_explosion': None,
                'confidence': 0.0
            }

        # Count consecutive weeks with hidden dissatisfaction
        consecutive_hidden_weeks = 0
        for i in range(len(hidden_flags) - 1, -1, -1):
            if hidden_flags[i]:
                consecutive_hidden_weeks += 1
            else:
                break

        # Check for increasing frustration with stable/high satisfaction (classic hidden pattern)
        frustration_increasing = False
        satisfaction_stable = False

        if len(frustration_levels) >= 3:
            recent_frustration = frustration_levels[-3:]
            if recent_frustration[2] > recent_frustration[0]:
                frustration_increasing = True

        if len(satisfaction_levels) >= 3:
            recent_satisfaction = satisfaction_levels[-3:]
            if max(
                recent_satisfaction) - min(
                    recent_satisfaction) < 0.2 and min(recent_satisfaction) > 0.5:
                satisfaction_stable = True

        # Determine explosion risk
        if consecutive_hidden_weeks >= 3 and frustration_increasing and satisfaction_stable:
            risk = 'high'
            explosion_probability = min(0.9, 0.5 + consecutive_hidden_weeks * 0.1)
            days_to_explosion = max(1, 14 - consecutive_hidden_weeks * 2)  # Rough estimate
        elif consecutive_hidden_weeks >= 2 and frustration_increasing:
            risk = 'medium'
            explosion_probability = min(0.7, 0.3 + consecutive_hidden_weeks * 0.1)
            days_to_explosion = max(3, 21 - consecutive_hidden_weeks * 2)  # Rough estimate
        elif consecutive_hidden_weeks >= 1:
            risk = 'low'
            explosion_probability = min(0.4, 0.1 + consecutive_hidden_weeks * 0.1)
            days_to_explosion = max(7, 28 - consecutive_hidden_weeks * 2)  # Rough estimate
        else:
            risk = 'minimal'
            explosion_probability = 0.1
            days_to_explosion = None

        # Calculate confidence based on data quality
        data_points_factor = min(1.0, len(weeks) / 10)  # More data points = higher confidence
        pattern_strength = 0.5 + (
            0.1 * consecutive_hidden_weeks) if consecutive_hidden_weeks > 0 else 0.5
        confidence = data_points_factor * 0.5 + pattern_strength * 0.5

        return {
            'risk': risk,
            'explosion_probability': float(explosion_probability),
            'days_to_explosion': days_to_explosion,
            'confidence': float(confidence)
        }

    def predict_next_week_emotions(self, history: StudentEmotionHistory) -> Dict[str, float]:
        """
        Predict emotions for the next week

        Args:
            history: Historical emotion data for a student

        Returns:
            Dictionary with predicted emotion values
        """
        # Need at least 2 data points for meaningful prediction
        if len(history.weeks) < 2:
            return self._default_emotion_prediction()

        # Use linear regression for short-term prediction
        frustration_pred = self._predict_next_value(history.weeks, history.frustration_levels)
        engagement_pred = self._predict_next_value(history.weeks, history.engagement_levels)
        confidence_pred = self._predict_next_value(history.weeks, history.confidence_levels)
        satisfaction_pred = self._predict_next_value(history.weeks, history.satisfaction_levels)

        # Predict emotional temperature based on frustration and engagement
        temperature_pred = (frustration_pred * 0.7 + (1 - engagement_pred) * 0.3)

        return {
            'frustration_level': float(frustration_pred),
            'engagement_level': float(engagement_pred),
            'confidence_level': float(confidence_pred),
            'satisfaction_level': float(satisfaction_pred),
            'emotional_temperature': float(temperature_pred)
        }

    def predict_two_week_emotions(self, history: StudentEmotionHistory) -> Dict[str, float]:
        """
        Predict emotions for two weeks ahead

        Args:
            history: Historical emotion data for a student

        Returns:
            Dictionary with predicted emotion values
        """
        # Need at least 3 data points for meaningful prediction
        if len(history.weeks) < 3:
            return self._default_emotion_prediction()

        # Use polynomial regression for medium-term prediction
        weeks = np.array(history.weeks)
        next_week = max(weeks) + 2  # Two weeks ahead

        frustration_pred = self._predict_polynomial(
            weeks, np.array(history.frustration_levels), next_week)
        engagement_pred = self._predict_polynomial(
            weeks, np.array(history.engagement_levels), next_week)
        confidence_pred = self._predict_polynomial(
            weeks, np.array(history.confidence_levels), next_week)
        satisfaction_pred = self._predict_polynomial(
            weeks, np.array(history.satisfaction_levels), next_week)

        # Predict emotional temperature based on frustration and engagement
        temperature_pred = (frustration_pred * 0.7 + (1 - engagement_pred) * 0.3)

        return {
            'frustration_level': float(frustration_pred),
            'engagement_level': float(engagement_pred),
            'confidence_level': float(confidence_pred),
            'satisfaction_level': float(satisfaction_pred),
            'emotional_temperature': float(temperature_pred)
        }

    def predict_end_course_emotions(self, history: StudentEmotionHistory) -> Dict[str, float]:
        """
        Predict emotions at the end of the course

        Args:
            history: Historical emotion data for a student

        Returns:
            Dictionary with predicted emotion values
        """
        # Need at least 3 data points for meaningful prediction
        if len(history.weeks) < 3:
            return self._default_emotion_prediction()

        # Assume course is 12 weeks long
        weeks = np.array(history.weeks)
        end_week = 12

        # If we're already past week 10, predictions are less reliable
        if max(weeks) >= 10:
            # Use last 3 weeks to predict final state
            recent_weeks = weeks[-3:]
            recent_frustration = np.array(history.frustration_levels[-3:])
            recent_engagement = np.array(history.engagement_levels[-3:])
            recent_confidence = np.array(history.confidence_levels[-3:])
            recent_satisfaction = np.array(history.satisfaction_levels[-3:])

            frustration_pred = self._predict_polynomial(recent_weeks, recent_frustration, end_week)
            engagement_pred = self._predict_polynomial(recent_weeks, recent_engagement, end_week)
            confidence_pred = self._predict_polynomial(recent_weeks, recent_confidence, end_week)
            satisfaction_pred = self._predict_polynomial(
                recent_weeks, recent_satisfaction, end_week)
        else:
            # Use all available data for long-term prediction
            frustration_pred = self._predict_polynomial(
                weeks, np.array(history.frustration_levels), end_week)
            engagement_pred = self._predict_polynomial(
                weeks, np.array(history.engagement_levels), end_week)
            confidence_pred = self._predict_polynomial(
                weeks, np.array(history.confidence_levels), end_week)
            satisfaction_pred = self._predict_polynomial(
                weeks, np.array(history.satisfaction_levels), end_week)

        # Predict emotional temperature based on frustration and engagement
        temperature_pred = (frustration_pred * 0.7 + (1 - engagement_pred) * 0.3)

        return {
            'frustration_level': float(frustration_pred),
            'engagement_level': float(engagement_pred),
            'confidence_level': float(confidence_pred),
            'satisfaction_level': float(satisfaction_pred),
            'emotional_temperature': float(temperature_pred)
        }

    def predict_frustration_threshold(
        self, frustration_trajectory: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict when frustration will reach a critical threshold

        Args:
            frustration_trajectory: Frustration trajectory analysis

        Returns:
            Dictionary with frustration threshold analysis
        """
        # Extract relevant data from frustration trajectory
        trend = frustration_trajectory.get('trend', 'unknown')
        days_to_threshold = frustration_trajectory.get('days_to_threshold')
        confidence = frustration_trajectory.get('confidence', 0.0)

        # Determine risk level
        if trend == 'insufficient_data':
            risk_level = 'unknown'
        elif days_to_threshold is not None and days_to_threshold <= 3:
            risk_level = 'critical'
        elif days_to_threshold is not None and days_to_threshold <= 7:
            risk_level = 'high'
        elif days_to_threshold is not None and days_to_threshold <= 14:
            risk_level = 'medium'
        elif trend in ['accelerating_increase', 'steady_increase']:
            risk_level = 'low'
        else:
            risk_level = 'minimal'

        # Determine intervention urgency
        if risk_level == 'critical':
            intervention_urgency = 'immediate'
        elif risk_level == 'high':
            intervention_urgency = 'within_24_hours'
        elif risk_level == 'medium':
            intervention_urgency = 'within_week'
        else:
            intervention_urgency = 'routine'

        return {
            'risk_level': risk_level,
            'days_to_threshold': days_to_threshold,
            'intervention_urgency': intervention_urgency,
            'confidence': confidence
        }

    def predict_engagement_dropout(self, engagement_decay: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict dropout risk based on engagement decay

        Args:
            engagement_decay: Engagement decay analysis

        Returns:
            Dictionary with dropout risk analysis
        """
        # Extract relevant data from engagement decay
        dropout_risk = engagement_decay.get('dropout_risk', 'unknown')
        weeks_to_disengagement = engagement_decay.get('weeks_to_disengagement')
        confidence = engagement_decay.get('confidence', 0.0)

        # Determine intervention type
        if dropout_risk == 'high':
            intervention_type = 'intensive_support'
        elif dropout_risk == 'medium':
            intervention_type = 'targeted_engagement'
        elif dropout_risk == 'low':
            intervention_type = 'preventive_check_in'
        else:
            intervention_type = 'routine_monitoring'

        # Calculate days to intervention
        days_to_intervention = None
        if weeks_to_disengagement is not None:
            # Intervene before critical disengagement
            days_to_intervention = max(1, int(weeks_to_disengagement * 7 - 7))

        return {
            'dropout_risk': dropout_risk,
            'weeks_to_disengagement': weeks_to_disengagement,
            'intervention_type': intervention_type,
            'days_to_intervention': days_to_intervention,
            'confidence': confidence
        }

    def predict_dissatisfaction_explosion(
        self, hidden_dissatisfaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict when hidden dissatisfaction might explode into open dissatisfaction

        Args:
            hidden_dissatisfaction: Hidden dissatisfaction analysis

        Returns:
            Dictionary with dissatisfaction explosion analysis
        """
        # Extract relevant data from hidden dissatisfaction
        risk = hidden_dissatisfaction.get('risk', 'unknown')
        explosion_probability = hidden_dissatisfaction.get('explosion_probability', 0.0)
        days_to_explosion = hidden_dissatisfaction.get('days_to_explosion')
        confidence = hidden_dissatisfaction.get('confidence', 0.0)

        # Determine intervention approach
        if risk == 'high':
            intervention_approach = 'empathetic_outreach'
        elif risk == 'medium':
            intervention_approach = 'indirect_support'
        elif risk == 'low':
            intervention_approach = 'subtle_check_in'
        else:
            intervention_approach = 'routine_monitoring'

        # Determine intervention timing
        if days_to_explosion is not None and days_to_explosion <= 3:
            intervention_timing = 'immediate'
        elif days_to_explosion is not None and days_to_explosion <= 7:
            intervention_timing = 'this_week'
        elif days_to_explosion is not None:
            intervention_timing = 'next_week'
        else:
            intervention_timing = 'routine'

        return {
            'risk': risk,
            'explosion_probability': explosion_probability,
            'days_to_explosion': days_to_explosion,
            'intervention_approach': intervention_approach,
            'intervention_timing': intervention_timing,
            'confidence': confidence
        }

    def find_intervention_windows(self,
                                emotion_predictions: Dict[str, Dict[str, float]],
                                risk_escalations: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Identify optimal intervention windows based on predictions and risk escalations

        Args:
            emotion_predictions: Multi-week emotion predictions
            risk_escalations: Risk escalation predictions

        Returns:
            Dictionary with optimal intervention windows
        """
        # Extract relevant data from risk escalations
        frustration_threshold = risk_escalations.get('frustration_boiling_point', {})
        engagement_dropout = risk_escalations.get('engagement_dropout_risk', {})
        dissatisfaction_explosion = risk_escalations.get('hidden_to_open_dissatisfaction', {})

        # Determine most urgent intervention
        urgent_interventions = []

        # Check frustration threshold
        frustration_days = frustration_threshold.get('days_to_threshold')
        if frustration_days is not None and frustration_days <= 7:
            urgent_interventions.append({
                'type': 'frustration_intervention',
                'days': frustration_days,
                'urgency': frustration_threshold.get('intervention_urgency', 'routine'),
                'confidence': frustration_threshold.get('confidence', 0.0)
            })

        # Check engagement dropout
        engagement_days = engagement_dropout.get('days_to_intervention')
        if engagement_days is not None:
            urgent_interventions.append({
                'type': 'engagement_intervention',
                'days': engagement_days,
                'urgency': 'within_week' if engagement_days <= 7 else 'routine',
                'confidence': engagement_dropout.get('confidence', 0.0)
            })

        # Check dissatisfaction explosion
        dissatisfaction_days = dissatisfaction_explosion.get('days_to_explosion')
        if dissatisfaction_days is not None:
            urgent_interventions.append({
                'type': 'dissatisfaction_intervention',
                'days': dissatisfaction_days,
                'urgency': dissatisfaction_explosion.get('intervention_timing', 'routine'),
                'confidence': dissatisfaction_explosion.get('confidence', 0.0)
            })

        # Sort interventions by urgency and confidence
        urgent_interventions.sort(
            key=lambda x: (self._urgency_to_numeric(x['urgency']), -x['days'], -x['confidence']))

        # Create intervention windows
        intervention_windows = {}

        if urgent_interventions:
            most_urgent = urgent_interventions[0]
            intervention_windows['primary'] = {
                'type': most_urgent['type'],
                'timing': most_urgent['urgency'],
                'days_from_now': most_urgent['days'],
                'confidence': most_urgent['confidence']
            }

            # Add secondary interventions if available
            if len(urgent_interventions) > 1:
                secondary = urgent_interventions[1]
                intervention_windows['secondary'] = {
                    'type': secondary['type'],
                    'timing': secondary['urgency'],
                    'days_from_now': secondary['days'],
                    'confidence': secondary['confidence']
                }
        else:
            # Default to routine check-in if no urgent interventions
            intervention_windows['primary'] = {
                'type': 'routine_check_in',
                'timing': 'routine',
                'days_from_now': 14,  # Two weeks
                'confidence': 0.5
            }

        # Add specific dates
        now = datetime.now()
        for window_key, window in intervention_windows.items():
            days = window.get('days_from_now')
            if days is not None:
                intervention_date = now + timedelta(days=days)
                window['target_date'] = intervention_date.strftime('%Y-%m-%d')

        return intervention_windows

    def calculate_prediction_confidence(self, history: StudentEmotionHistory) -> Dict[str, float]:
        """
        Calculate confidence scores for various predictions

        Args:
            history: Historical emotion data for a student

        Returns:
            Dictionary with confidence scores
        """
        # Base confidence on data quality and quantity
        data_points = len(history.weeks)
        data_quality_factor = min(1.0, data_points / 10)  # More data points = higher confidence

        # Calculate consistency of data (lower variance = higher consistency)
        frustration_variance = np.var(history.frustration_levels) if data_points > 1 else 1.0
        engagement_variance = np.var(history.engagement_levels) if data_points > 1 else 1.0
        consistency_factor = 1.0 - min(1.0, (frustration_variance + engagement_variance) / 2)

        # Calculate recency factor (more recent data = higher confidence)
        recency_factor = 0.7  # Default
        if data_points >= 3:
            # Check if we have recent data (last 2 weeks)
            max_week = max(history.weeks)
            if max_week >= max(history.weeks) - 2:
                recency_factor = 0.9

        # Base confidence score
        base_confidence = data_quality_factor * 0.4 + consistency_factor * 0.3 + recency_factor * 0.3

        # Adjust confidence for different prediction types
        return {
            'next_week': min(0.95, base_confidence * 1.2),  # Short-term predictions more confident
            'two_week': min(0.9, base_confidence * 1.0),  # Medium-term predictions
            'course_completion': min(
                0.8, base_confidence * 0.8),  # Long-term predictions less confident
            'frustration_threshold': min(0.9, base_confidence * 1.1),
            'engagement_dropout': min(0.85, base_confidence * 1.0),
            'dissatisfaction_explosion': min(
                0.8, base_confidence * 0.9),  # Hidden states harder to predict
            'intervention_windows': min(0.85, base_confidence * 1.0),
            'overall': base_confidence
        }

    def _predict_next_value(self, weeks: List[int], values: List[float]) -> float:
        """
        Predict the next value using linear regression
        """
        if len(weeks) < 2:
            return values[-1] if values else 0.5  # Default to last value or 0.5

        x = np.array(weeks)
        y = np.array(values)

        # Fit linear regression
        coeffs = np.polyfit(x, y, 1)
        poly = np.poly1d(coeffs)

        # Predict next week
        next_week = max(weeks) + 1
        prediction = poly(next_week)

        # Clip to valid range [0, 1]
        return max(0.0, min(1.0, prediction))

    def _predict_polynomial(self, weeks: np.ndarray, values: np.ndarray, target_week: int) -> float:
        """
        Predict a value using polynomial regression
        """
        if len(weeks) < 3:
            # Fall back to linear for insufficient data
            coeffs = np.polyfit(weeks, values, 1)
        else:
            # Use quadratic for 3+ data points
            coeffs = np.polyfit(weeks, values, 2)

        poly = np.poly1d(coeffs)
        prediction = poly(target_week)

        # Clip to valid range [0, 1]
        return max(0.0, min(1.0, prediction))

    def _calculate_r_squared(self, x: np.ndarray, y: np.ndarray, poly: np.poly1d) -> float:
        """
        Calculate R-squared value for polynomial fit
        """
        y_pred = poly(x)
        ss_total = np.sum((y - np.mean(y))**2)
        ss_residual = np.sum((y - y_pred)**2)

        if ss_total == 0:  # Avoid division by zero
            return 0.0

        r_squared = 1 - (ss_residual / ss_total)
        return max(0.0, min(1.0, r_squared))  # Clip to [0, 1]

    def _default_emotion_prediction(self) -> Dict[str, float]:
        """
        Return default emotion prediction when insufficient data
        """
        return {
            'frustration_level': 0.5,
            'engagement_level': 0.5,
            'confidence_level': 0.5,
            'satisfaction_level': 0.5,
            'emotional_temperature': 0.5
        }

    def _urgency_to_numeric(self, urgency: str) -> int:
        """
        Convert urgency string to numeric value for sorting
        """
        urgency_map = {
            'immediate': 0,
            'within_24_hours': 1,
            'this_week': 2,
            'within_week': 2,  # Same as this_week
            'next_week': 3,
            'routine': 4
        }
        return urgency_map.get(urgency, 5)  # Default to lowest priority

    async def get_student_emotion_history(
        self, student_id: str, course_id: str) -> StudentEmotionHistory:
        """
        Retrieve a student's emotion history from the database

        Args:
            student_id: The student's ID
            course_id: The course ID

        Returns:
            StudentEmotionHistory object with the student's emotion data
        """
        # Query the database for student journey entries
        student_journeys = self.db.query(StudentJourney).filter(
            StudentJourney.student_id == student_id,
            StudentJourney.course_id == course_id
        ).order_by(StudentJourney.week_number).all()

        # Extract emotion data
        weeks = []
        frustration_levels = []
        engagement_levels = []
        confidence_levels = []
        satisfaction_levels = []
        emotional_trajectories = []
        hidden_dissatisfaction_flags = []
        urgency_levels = []
        emotional_temperatures = []
        emotional_volatilities = []

        for journey in student_journeys:
            weeks.append(journey.week_number)
            frustration_levels.append(journey.frustration_level or 0.5)
            engagement_levels.append(journey.engagement_level or 0.5)
            confidence_levels.append(journey.confidence_level or 0.5)
            satisfaction_levels.append(journey.satisfaction_level or 0.5)
            emotional_trajectories.append(journey.emotional_trajectory or 'neutral')
            hidden_dissatisfaction_flags.append(journey.hidden_dissatisfaction_flag or False)
            urgency_levels.append(journey.urgency_level or 'low')
            emotional_temperatures.append(journey.emotional_temperature or 0.5)
            emotional_volatilities.append(journey.emotional_volatility or 0.5)

        return StudentEmotionHistory(
            student_id=student_id,
            course_id=course_id,
            weeks=weeks,
            frustration_levels=frustration_levels,
            engagement_levels=engagement_levels,
            confidence_levels=confidence_levels,
            satisfaction_levels=satisfaction_levels,
            emotional_trajectories=emotional_trajectories,
            hidden_dissatisfaction_flags=hidden_dissatisfaction_flags,
            urgency_levels=urgency_levels,
            emotional_temperatures=emotional_temperatures,
            emotional_volatilities=emotional_volatilities
        )
