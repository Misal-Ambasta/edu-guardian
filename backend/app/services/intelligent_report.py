
"""Intelligent Report module for the application.

This module provides functionality related to intelligent report.
"""
from typing import List, Dict, Any, Optional, Union
from sqlalchemy.orm import Session
from datetime import datetime, date
import uuid
import statistics
from collections import Counter
from textblob import TextBlob

import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

from ..models.weekly_report import WeeklyNPSReport
from ..models.student_journey import StudentJourney
from ..models.intervention import Intervention
from ..models.historical_pattern import HistoricalPattern
from ..emotion_analysis.analyzer import EmotionProfile
from .historical_pattern import HistoricalPatternService
from .intervention_tracker import EmotionBasedInterventionTracker
class IntelligentReportGenerator:
    """
    Generates AI-powered insights through advanced pattern recognition,
    historical context analysis, and natural language insight generation.
    """

    def __init__(self, db: Session):
        self.db = db
        self.historical_pattern_service = HistoricalPatternService()
        self.intervention_tracker = EmotionBasedInterventionTracker(db)

    async def generate_ai_powered_insights(self, weekly_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI-powered insights through advanced pattern recognition,
        historical context analysis, and natural language insight generation.

        Args:
            weekly_data: Dictionary containing weekly student data, emotion analytics, etc.

        Returns:
            Dictionary containing AI-powered insights
        """
        # Advanced pattern recognition
        unusual_patterns = await self.detect_anomalous_patterns(weekly_data)
        emerging_risks = await self.identify_emerging_risk_patterns(weekly_data)
        intervention_opportunities = await self.find_intervention_opportunities(weekly_data)

        # Historical context analysis
        historical_context = await self.analyze_historical_context(weekly_data)
        predictive_insights = await self.generate_predictive_insights(
            weekly_data, historical_context)

        # Generate natural language insights
        ai_insights = await self.generate_natural_language_insights({
            'patterns': unusual_patterns,
            'risks': emerging_risks,
            'opportunities': intervention_opportunities,
            'predictions': predictive_insights
        })

        return {
            'unusual_patterns': unusual_patterns,
            'emerging_risks': emerging_risks,
            'intervention_opportunities': intervention_opportunities,
            'historical_context': historical_context,
            'predictive_insights': predictive_insights,
            'ai_insights': ai_insights
        }

    async def detect_anomalous_patterns(self, weekly_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect anomalous patterns in weekly data using clustering and statistical analysis.

        Args:
            weekly_data: Dictionary containing weekly student data

        Returns:
            List of anomalous patterns detected
        """
        anomalous_patterns = []
        student_data = weekly_data.get('student_data', [])

        if not student_data:
            return anomalous_patterns

        # Extract numerical features for clustering
        features = []
        for student in student_data:
            # Extract relevant numerical features
            student_features = [
                student.nps_score if hasattr(student, 'nps_score') else 5,
                student.frustration_level if hasattr(student, 'frustration_level') else 0.5,
                student.emotional_temperature if hasattr(student, 'emotional_temperature') else 0.5,
                student.hidden_dissatisfaction_confidence if hasattr(
                    student, 'hidden_dissatisfaction_confidence') else 0.0
            ]
            features.append(student_features)

        if not features:
            return anomalous_patterns

        # Standardize features
        X = StandardScaler().fit_transform(features)

        # Perform DBSCAN clustering to identify outliers
        db = DBSCAN(eps=0.5, min_samples=3).fit(X)
        labels = db.labels_

        # Identify outliers (points labeled as -1)
        outlier_indices = [i for i, label in enumerate(labels) if label == -1]

        # Create anomalous pattern entries
        for idx in outlier_indices:
            student = student_data[idx]
            pattern = {
                'student_id': student.student_id if hasattr(student, 'student_id') else 'unknown',
                'pattern_type': 'anomalous_emotion_profile',
                'confidence': 0.85,
                'description': f"Unusual emotion pattern detected for student {student.student_id if hasattr(student, 'student_id') else 'unknown'}",
                'features': {
                    'nps_score': student.nps_score if hasattr(student, 'nps_score') else None,
                    'frustration_level': student.frustration_level if hasattr(
                        student, 'frustration_level') else None,
                    'emotional_temperature': student.emotional_temperature if hasattr(
                        student, 'emotional_temperature') else None,
                    'hidden_dissatisfaction': student.hidden_dissatisfaction_flag if hasattr(
                        student, 'hidden_dissatisfaction_flag') else None
                }
            }
            anomalous_patterns.append(pattern)

        # Detect temporal anomalies if historical data is available
        if 'historical_data' in weekly_data:
            temporal_anomalies = self._detect_temporal_anomalies(
                weekly_data['student_data'], weekly_data['historical_data'])
            anomalous_patterns.extend(temporal_anomalies)

        return anomalous_patterns

    def _detect_temporal_anomalies(
        self, current_data: List[Any], historical_data: List[Any]) -> List[Dict[str, Any]]:
        """
        Helper method to detect temporal anomalies by comparing current data with historical data.

        Args:
            current_data: Current week's student data
            historical_data: Historical student data

        Returns:
            List of temporal anomalies detected
        """
        temporal_anomalies = []

        # Group data by student_id
        current_by_student = {}
        for student in current_data:
            if hasattr(student, 'student_id'):
                current_by_student[student.student_id] = student

        historical_by_student = {}
        for student in historical_data:
            if hasattr(student, 'student_id'):
                if student.student_id not in historical_by_student:
                    historical_by_student[student.student_id] = []
                historical_by_student[student.student_id].append(student)

        # Compare current with historical for each student
        for student_id, current in current_by_student.items():
            if student_id in historical_by_student:
                history = historical_by_student[student_id]

                # Calculate average historical values
                avg_nps = statistics.mean(
                    [h.nps_score for h in history if hasattr(h, 'nps_score')]) if history else 5
                avg_frustration = statistics.mean(
                    [h.frustration_level for h in history if hasattr(
                        h, 'frustration_level')]) if history else 0.5

                # Check for significant deviations
                if hasattr(current, 'nps_score') and abs(current.nps_score - avg_nps) > 3:
                    temporal_anomalies.append({
                        'student_id': student_id,
                        'pattern_type': 'temporal_nps_anomaly',
                        'confidence': 0.9,
                        'description': f"Significant change in NPS score for student {student_id}",
                        'features': {
                            'current_nps': current.nps_score,
                            'avg_historical_nps': avg_nps,
                            'deviation': current.nps_score - avg_nps
                        }
                    })

                if hasattr(
                    current, 'frustration_level') and abs(
                        current.frustration_level - avg_frustration) > 0.3:
                    temporal_anomalies.append({
                        'student_id': student_id,
                        'pattern_type': 'temporal_frustration_anomaly',
                        'confidence': 0.85,
                        'description': f"Significant change in frustration level for student {student_id}",
                        'features': {
                            'current_frustration': current.frustration_level,
                            'avg_historical_frustration': avg_frustration,
                            'deviation': current.frustration_level - avg_frustration
                        }
                    })

        return temporal_anomalies

    async def identify_emerging_risk_patterns(
        self, weekly_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify emerging risk patterns in weekly data.

        Args:
            weekly_data: Dictionary containing weekly student data

        Returns:
            List of emerging risk patterns identified
        """
        emerging_risks = []
        student_data = weekly_data.get('student_data', [])

        if not student_data:
            return emerging_risks

        # Group students by risk factors
        frustration_types = Counter(
            [s.frustration_type for s in student_data if hasattr(
                s, 'frustration_type') and s.frustration_type])
        high_frustration_students = [s for s in student_data if hasattr(
            s, 'frustration_level') and s.frustration_level and s.frustration_level > 0.7]
        hidden_dissatisfaction_students = [s for s in student_data if hasattr(
            s, 'hidden_dissatisfaction_flag') and s.hidden_dissatisfaction_flag]

        # Identify emerging risk patterns based on frequency and severity
        for frustration_type, count in frustration_types.items():
            if count >= 3:  # Threshold for considering it an emerging pattern
                emerging_risks.append({
                    'pattern_type': 'emerging_frustration_type',
                    'frustration_type': frustration_type,
                    'count': count,
                    'confidence': min(
                        0.5 + (count / 10), 0.95),  # Higher confidence with more occurrences
                    'description': f"Emerging pattern of '{frustration_type}' frustration detected in {count} students"
                })

        if len(high_frustration_students) >= 3:
            emerging_risks.append({
                'pattern_type': 'high_frustration_cluster',
                'count': len(high_frustration_students),
                'confidence': min(0.6 + (len(high_frustration_students) / 20), 0.95),
                'description': f"Cluster of {len(
                    high_frustration_students)} students with high frustration levels detected",
                'affected_students': [s.student_id for s in high_frustration_students if hasattr(
                    s, 'student_id')]
            })

        if len(hidden_dissatisfaction_students) >= 2:
            emerging_risks.append({
                'pattern_type': 'hidden_dissatisfaction_cluster',
                'count': len(hidden_dissatisfaction_students),
                'confidence': min(0.7 + (len(hidden_dissatisfaction_students) / 15), 0.95),
                'description': f"Cluster of {len(
                    hidden_dissatisfaction_students)} students with hidden dissatisfaction detected",
                'affected_students': [s.student_id for s in hidden_dissatisfaction_students if hasattr(s, 'student_id')]
            })

        # Analyze comment sentiment if available
        sentiment_risks = self._analyze_comment_sentiment(student_data)
        if sentiment_risks:
            emerging_risks.extend(sentiment_risks)

        return emerging_risks

    def _analyze_comment_sentiment(self, student_data: List[Any]) -> List[Dict[str, Any]]:
        """
        Analyze sentiment in student comments to identify potential risks.

        Args:
            student_data: List of student data objects

        Returns:
            List of sentiment-based risk patterns
        """
        sentiment_risks = []
        negative_comments = []

        for student in student_data:
            if hasattr(student, 'comments') and student.comments:
                # Use TextBlob for sentiment analysis
                sentiment = TextBlob(student.comments).sentiment

                # Check for strongly negative sentiment
                if sentiment.polarity < -0.3:
                    negative_comments.append({
                        'student_id': student.student_id if hasattr(
                            student, 'student_id') else 'unknown',
                        'comment': student.comments,
                        'sentiment_score': sentiment.polarity,
                        'subjectivity': sentiment.subjectivity
                    })

        if len(negative_comments) >= 2:
            sentiment_risks.append({
                'pattern_type': 'negative_sentiment_cluster',
                'count': len(negative_comments),
                'confidence': min(0.6 + (len(negative_comments) / 15), 0.9),
                'description': f"Cluster of {len(
                    negative_comments)} students with strongly negative comments detected",
                'examples': negative_comments[:3]  # Include a few examples
            })

        return sentiment_risks

    async def find_intervention_opportunities(
        self, weekly_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find intervention opportunities based on weekly data.

        Args:
            weekly_data: Dictionary containing weekly student data

        Returns:
            List of intervention opportunities
        """
        intervention_opportunities = []
        student_data = weekly_data.get('student_data', [])

        if not student_data:
            return intervention_opportunities

        # Identify students who need interventions
        for student in student_data:
            if not hasattr(student, 'student_id'):
                continue

            student_id = student.student_id
            intervention_needed = False
            intervention_type = None
            urgency = 'medium'
            confidence = 0.7
            reasons = []

            # Check frustration level
            if hasattr(student, 'frustration_level') and student.frustration_level:
                if student.frustration_level > 0.8:
                    intervention_needed = True
                    intervention_type = 'frustration_reduction'
                    urgency = 'high'
                    confidence = 0.9
                    reasons.append('Very high frustration level')
                elif student.frustration_level > 0.6:
                    intervention_needed = True
                    intervention_type = 'frustration_reduction'
                    reasons.append('High frustration level')

            # Check hidden dissatisfaction
            if hasattr(
                student, 'hidden_dissatisfaction_flag') and student.hidden_dissatisfaction_flag:
                intervention_needed = True
                intervention_type = 'hidden_dissatisfaction_resolution'
                confidence = max(confidence, 0.85)
                reasons.append('Hidden dissatisfaction detected')

            # Check NPS score
            if hasattr(student, 'nps_score') and student.nps_score is not None:
                if student.nps_score <= 3:
                    intervention_needed = True
                    intervention_type = intervention_type or 'satisfaction_improvement'
                    urgency = 'high'
                    confidence = max(confidence, 0.85)
                    reasons.append('Very low NPS score')
                elif student.nps_score <= 5:
                    intervention_needed = True
                    intervention_type = intervention_type or 'satisfaction_improvement'
                    reasons.append('Low NPS score')

            if intervention_needed:
                # Check if student already has an active intervention
                existing_intervention = await self._check_existing_intervention(student_id)

                if not existing_intervention:
                    intervention_opportunities.append({
                        'student_id': student_id,
                        'intervention_type': intervention_type,
                        'urgency': urgency,
                        'confidence': confidence,
                        'reasons': reasons,
                        'description': f"Intervention opportunity for student {student_id}: {', '.join(reasons)}"
                    })

        return intervention_opportunities

    async def _check_existing_intervention(self, student_id: str) -> bool:
        """
        Check if a student already has an active intervention.

        Args:
            student_id: The ID of the student to check

        Returns:
            True if the student has an active intervention, False otherwise
        """
        # Query the database for active interventions for this student
        # This is a simplified implementation
        interventions = self.db.query(Intervention).filter(
            Intervention.student_id == student_id,
            Intervention.outcome_status.is_(None)  # No outcome status means it's still active
        ).all()

        return len(interventions) > 0

    async def analyze_historical_context(self, weekly_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze historical context for the current weekly data.

        Args:
            weekly_data: Dictionary containing weekly student data

        Returns:
            Dictionary containing historical context analysis
        """
        historical_context = {
            'similar_periods': [],
            'historical_patterns': [],
            'trend_analysis': {},
            'confidence': 0.0
        }

        student_data = weekly_data.get('student_data', [])
        historical_data = weekly_data.get('historical_data', [])
        course_id = weekly_data.get('course_id')
        week_number = weekly_data.get('week_number')

        if not student_data or not historical_data or not course_id or not week_number:
            return historical_context

        # Find similar historical periods
        similar_periods = await self._find_similar_periods(
            student_data, historical_data, course_id, week_number)
        historical_context['similar_periods'] = similar_periods

        # Get relevant historical patterns
        historical_patterns = await self.historical_pattern_service.get_relevant_patterns(
            student_data)
        historical_context['historical_patterns'] = historical_patterns

        # Analyze trends over time
        trend_analysis = self._analyze_trends(student_data, historical_data)
        historical_context['trend_analysis'] = trend_analysis

        # Calculate confidence based on data quality and similarity
        confidence = 0.5  # Base confidence
        if similar_periods:
            # Higher confidence with more similar periods and higher similarity scores
            avg_similarity = statistics.mean(
                [p.get('similarity_score', 0) for p in similar_periods])
            confidence = min(0.5 + (len(similar_periods) / 10) + (avg_similarity / 2), 0.95)

        historical_context['confidence'] = confidence

        return historical_context

    async def _find_similar_periods(self, current_data: List[Any], historical_data: List[Any],
                                  course_id: str, week_number: int) -> List[Dict[str, Any]]:
        """
        Find similar historical periods to the current week.

        Args:
            current_data: Current week's student data
            historical_data: Historical student data
            course_id: The ID of the current course
            week_number: The current week number

        Returns:
            List of similar historical periods
        """
        similar_periods = []

        # Group historical data by course and week
        historical_by_period = {}
        for student in historical_data:
            if hasattr(student, 'course_id') and hasattr(student, 'week_number'):
                key = f"{student.course_id}_{student.week_number}"
                if key not in historical_by_period:
                    historical_by_period[key] = []
                historical_by_period[key].append(student)

        # Calculate current period metrics
        current_metrics = self._calculate_period_metrics(current_data)

        # Compare with each historical period
        for period_key, period_data in historical_by_period.items():
            # Skip current period
            if period_key == f"{course_id}_{week_number}":
                continue

            period_metrics = self._calculate_period_metrics(period_data)
            similarity_score = self._calculate_similarity(current_metrics, period_metrics)

            if similarity_score > 0.7:  # Threshold for considering it similar
                course_id, week_number = period_key.split('_')
                similar_periods.append({
                    'course_id': course_id,
                    'week_number': int(week_number),
                    'similarity_score': similarity_score,
                    'key_similarities': self._get_key_similarities(current_metrics, period_metrics)
                })

        # Sort by similarity score (descending)
        similar_periods.sort(key=lambda x: x['similarity_score'], reverse=True)

        return similar_periods[:5]  # Return top 5 similar periods

    def _calculate_period_metrics(self, student_data: List[Any]) -> Dict[str, float]:
        """
        Calculate metrics for a period based on student data.

        Args:
            student_data: List of student data objects

        Returns:
            Dictionary of period metrics
        """
        metrics = {}

        # Calculate average NPS score
        nps_scores = [s.nps_score for s in student_data if hasattr(
            s, 'nps_score') and s.nps_score is not None]
        if nps_scores:
            metrics['avg_nps'] = statistics.mean(nps_scores)

        # Calculate average frustration level
        frustration_levels = [s.frustration_level for s in student_data if hasattr(
            s, 'frustration_level') and s.frustration_level is not None]
        if frustration_levels:
            metrics['avg_frustration'] = statistics.mean(frustration_levels)

        # Calculate hidden dissatisfaction rate
        hidden_dissatisfaction_count = sum(
            1 for s in student_data if hasattr(
                s, 'hidden_dissatisfaction_flag') and s.hidden_dissatisfaction_flag)
        metrics['hidden_dissatisfaction_rate'] = hidden_dissatisfaction_count / len(
            student_data) if student_data else 0

        # Calculate aspect scores if available
        for aspect in ['lms_usability_score', 'instructor_quality_score', 'content_difficulty_score', 'support_quality_score', 'course_pace_score']:
            aspect_scores = [getattr(
                s, aspect) for s in student_data if hasattr(
                    s, aspect) and getattr(s, aspect) is not None]
            if aspect_scores:
                metrics[f'avg_{aspect}'] = statistics.mean(aspect_scores)

        return metrics

    def _calculate_similarity(
        self, metrics1: Dict[str, float], metrics2: Dict[str, float]) -> float:
        """
        Calculate similarity between two sets of metrics.

        Args:
            metrics1: First set of metrics
            metrics2: Second set of metrics

        Returns:
            Similarity score between 0 and 1
        """
        # Find common metrics
        common_metrics = set(metrics1.keys()) & set(metrics2.keys())

        if not common_metrics:
            return 0.0

        # Calculate Euclidean distance for common metrics
        squared_diff_sum = 0.0
        for metric in common_metrics:
            # Normalize the values based on expected ranges
            if metric == 'avg_nps':
                # NPS is 0-10
                squared_diff_sum += ((metrics1[metric] - metrics2[metric]) / 10) ** 2
            elif metric.startswith('avg_') and metric.endswith('_score'):
                # Aspect scores are 1-5
                squared_diff_sum += ((metrics1[metric] - metrics2[metric]) / 5) ** 2
            else:
                # Other metrics are typically 0-1
                squared_diff_sum += (metrics1[metric] - metrics2[metric]) ** 2

        # Convert distance to similarity (1 for identical, 0 for maximally different)
        distance = (squared_diff_sum / len(common_metrics)) ** 0.5
        similarity = 1 - min(distance, 1.0)  # Cap at 0

        return similarity

    def _get_key_similarities(
        self, metrics1: Dict[str, float], metrics2: Dict[str, float]) -> List[str]:
        """
        Identify key similarities between two sets of metrics.

        Args:
            metrics1: First set of metrics
            metrics2: Second set of metrics

        Returns:
            List of key similarity descriptions
        """
        key_similarities = []
        common_metrics = set(metrics1.keys()) & set(metrics2.keys())

        for metric in common_metrics:
            # Check if the metrics are very similar
            if metric == 'avg_nps':
                if abs(metrics1[metric] - metrics2[metric]) < 0.5:
                    key_similarities.append(
                        f"Similar average NPS score: {metrics1[metric]:.1f} vs {metrics2[metric]:.1f}")
            elif metric == 'avg_frustration':
                if abs(metrics1[metric] - metrics2[metric]) < 0.1:
                    key_similarities.append(
                        f"Similar frustration levels: {metrics1[metric]:.2f} vs {metrics2[metric]:.2f}")
            elif metric == 'hidden_dissatisfaction_rate':
                if abs(metrics1[metric] - metrics2[metric]) < 0.05:
                    key_similarities.append(
                        f"Similar hidden dissatisfaction rate: {metrics1[metric]:.1%} vs {metrics2[metric]:.1%}")
            elif metric.startswith('avg_') and metric.endswith('_score'):
                if abs(metrics1[metric] - metrics2[metric]) < 0.3:
                    aspect = metric[4:-6]  # Extract aspect name
                    key_similarities.append(
                        f"Similar {aspect} scores: {metrics1[metric]:.1f} vs {metrics2[metric]:.1f}")

        return key_similarities[:3]  # Return top 3 similarities

    def _analyze_trends(
        self, current_data: List[Any], historical_data: List[Any]) -> Dict[str, Any]:
        """
        Analyze trends over time based on current and historical data.

        Args:
            current_data: Current week's student data
            historical_data: Historical student data

        Returns:
            Dictionary containing trend analysis
        """
        trends = {}

        # Group historical data by week
        data_by_week = {}
        for student in historical_data:
            if hasattr(student, 'week_number'):
                week = student.week_number
                if week not in data_by_week:
                    data_by_week[week] = []
                data_by_week[week].append(student)

        # Add current data to the mix
        current_week = current_data[0].week_number if current_data and hasattr(
            current_data[0], 'week_number') else max(data_by_week.keys()) + 1
        data_by_week[current_week] = current_data

        # Calculate metrics for each week
        metrics_by_week = {}
        for week, data in data_by_week.items():
            metrics_by_week[week] = self._calculate_period_metrics(data)

        # Analyze trends for each metric
        all_weeks = sorted(metrics_by_week.keys())
        for metric in metrics_by_week[all_weeks[0]].keys():
            # Get values for this metric across all weeks
            values = [metrics_by_week[week].get(
                metric) for week in all_weeks if metric in metrics_by_week[week]]
            weeks = [week for week in all_weeks if metric in metrics_by_week[week]]

            if len(values) >= 3:  # Need at least 3 points for trend analysis
                # Calculate trend direction and magnitude
                trend_direction = 'stable'
                if values[-1] > values[-2]:
                    trend_direction = 'increasing'
                elif values[-1] < values[-2]:
                    trend_direction = 'decreasing'

                # Calculate trend consistency
                increases = sum(1 for i in range(1, len(values)) if values[i] > values[i-1])
                decreases = sum(1 for i in range(1, len(values)) if values[i] < values[i-1])
                consistency = max(increases, decreases) / (len(values) - 1)

                trends[metric] = {
                    'direction': trend_direction,
                    'consistency': consistency,
                    'values': values,
                    'weeks': weeks,
                    'current_value': values[-1],
                    'previous_value': values[-2],
                    'change': values[-1] - values[-2],
                    'percent_change': (
                        values[-1] - values[-2]) / values[-2] if values[-2] != 0 else 0
                }

        return trends

    async def generate_predictive_insights(self, weekly_data: Dict[str, Any],
                                         historical_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate predictive insights based on weekly data and historical context.

        Args:
            weekly_data: Dictionary containing weekly student data
            historical_context: Dictionary containing historical context analysis

        Returns:
            List of predictive insights
        """
        predictive_insights = []

        # Use historical patterns to generate predictions
        for pattern in historical_context.get('historical_patterns', []):
            if 'typical_outcome' in pattern and pattern.get('confidence_threshold', 0) > 0.7:
                predictive_insights.append({
                    'pattern_name': pattern.get('pattern_name', 'Unknown pattern'),
                    'prediction_type': 'outcome_prediction',
                    'predicted_outcome': pattern.get('typical_outcome'),
                    'confidence': pattern.get('confidence_threshold', 0.7),
                    'description': f"Based on the '{pattern.get(
                        'pattern_name')}' pattern, the likely outcome is {pattern.get(
                            'typical_outcome')}"
                })

        # Use similar periods to generate predictions
        for period in historical_context.get('similar_periods', []):
            if period.get('similarity_score', 0) > 0.8:
                # Query the database for the outcome of this similar period
                # This is a simplified implementation
                outcome = "successful completion"  # Default outcome
                predictive_insights.append({
                    'similar_period': f"{period.get('course_id')}_{period.get('week_number')}",
                    'prediction_type': 'similar_period_prediction',
                    'predicted_outcome': outcome,
                    'confidence': period.get('similarity_score', 0.8),
                    'description': f"Based on similarity to {period.get(
                        'course_id')} week {period.get(
                            'week_number')}, the likely outcome is {outcome}"
                })

        # Use trend analysis to generate predictions
        trend_analysis = historical_context.get('trend_analysis', {})
        for metric, trend in trend_analysis.items():
            if trend.get('consistency', 0) > 0.7:
                # Predict future value based on recent trend
                current_value = trend.get('current_value', 0)
                change = trend.get('change', 0)
                predicted_value = current_value + change  # Simple linear projection

                predictive_insights.append({
                    'metric': metric,
                    'prediction_type': 'trend_prediction',
                    'current_value': current_value,
                    'predicted_value': predicted_value,
                    'confidence': trend.get('consistency', 0.7),
                    'description': f"Based on consistent {trend.get(
                        'direction')} trend, {metric} is predicted to be {predicted_value:.2f} next week"
                })

        return predictive_insights

    async def generate_natural_language_insights(
        self, insights_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate natural language insights based on the collected insights data.

        Args:
            insights_data: Dictionary containing various insights data

        Returns:
            List of natural language insights
        """
        natural_language_insights = []

        # Process anomalous patterns
        for pattern in insights_data.get('patterns', []):
            if pattern.get('pattern_type') == 'anomalous_emotion_profile':
                insight = {
                    'insight_text': f"Student {pattern.get(
                        'student_id')} shows an unusual emotional profile that requires attention.",
                    'confidence_level': pattern.get('confidence', 0.7),
                    'supporting_evidence': [
                        f"Anomalous values detected in emotional metrics",
                        f"Pattern differs significantly from peer group"
                    ],
                    'impact_assessment': 'Medium',
                    'action_items': [
                        {
                            'action_description': f"Schedule a check-in with student {pattern.get(
                                'student_id')}",
                            'priority': 'High',
                            'timeline': 'This week'
                        }
                    ]
                }
                natural_language_insights.append(insight)
            elif pattern.get('pattern_type') == 'temporal_nps_anomaly':
                direction = \
                    'increase' if pattern.get(
                        'features', {}).get('deviation', 0) > 0 else 'decrease'

                insight = {
                    'insight_text': f"Student {pattern.get(
                        'student_id')} shows a significant {direction} in satisfaction compared to their history.",
                    'confidence_level': pattern.get('confidence', 0.7),
                    'supporting_evidence': [
                        f"Current NPS: {pattern.get('features', {}).get('current_nps')}",
                        f"Historical average: {pattern.get(
                            'features', {}).get('avg_historical_nps')}",
                        f"Change: {abs(pattern.get('features', {}).get('deviation', 0)):.1f} points"
                    ],
                    'impact_assessment': 'Medium',
                    'action_items': []
                }

                # Add appropriate action items based on direction
                if direction == 'decrease':
                    insight['action_items'].append({
                        'action_description': f"Investigate cause of satisfaction drop for student {pattern.get('student_id')}",
                        'priority': 'High',
                        'timeline': 'This week'
                    })
                else:
                    insight['action_items'].append({
                        'action_description': f"Document successful strategies that improved satisfaction for student {pattern.get('student_id')}",
                        'priority': 'Medium',
                        'timeline': 'Next two weeks'
                    })

                natural_language_insights.append(insight)

        # Process emerging risks
        for risk in insights_data.get('risks', []):
            if risk.get('pattern_type') == 'emerging_frustration_type':
                insight = {
                    'insight_text': f"An emerging pattern of '{risk.get(
                        'frustration_type')}' frustration has been detected across multiple students.",
                    'confidence_level': risk.get('confidence', 0.7),
                    'supporting_evidence': [
                        f"{risk.get('count')} students showing this frustration type",
                        f"This represents a significant cluster in the current data"
                    ],
                    'impact_assessment': 'High',
                    'action_items': [
                        {
                            'action_description': f"Develop targeted intervention for '{risk.get(
                                'frustration_type')}' frustration",
                            'priority': 'High',
                            'timeline': 'Immediate'
                        },
                        {
                            'action_description': f"Review course materials related to '{risk.get(
                                'frustration_type')}'",
                            'priority': 'Medium',
                            'timeline': 'This week'
                        }
                    ]
                }
                natural_language_insights.append(insight)
            elif risk.get('pattern_type') == 'negative_sentiment_cluster':
                insight = {
                    'insight_text': f"A cluster of {risk.get(
                        'count')} students have expressed strongly negative sentiments in their comments.",
                    'confidence_level': risk.get('confidence', 0.7),
                    'supporting_evidence': [
                        f"Multiple students with negative sentiment scores below -0.3",
                        f"Example: '{risk.get('examples', [{}])[0].get('comment', '')[0:50]}...'"
                    ],
                    'impact_assessment': 'High',
                    'action_items': [
                        {
                            'action_description': "Conduct sentiment analysis review of all student comments",
                            'priority': 'High',
                            'timeline': 'This week'
                        },
                        {
                            'action_description': "Schedule focus group to address common concerns",
                            'priority': 'Medium',
                            'timeline': 'Next two weeks'
                        }
                    ]
                }
                natural_language_insights.append(insight)

        # Process intervention opportunities
        for opportunity in insights_data.get('opportunities', []):
            reasons = opportunity.get('reasons', [])
            reasons_text = ", ".join(reasons)

            insight = {
                'insight_text': f"Student {opportunity.get(
                    'student_id')} requires intervention due to: {reasons_text}.",
                'confidence_level': opportunity.get('confidence', 0.7),
                'supporting_evidence': reasons,
                'impact_assessment': 'High' if opportunity.get('urgency') == 'high' else 'Medium',
                'action_items': [
                    {
                        'action_description': f"Implement {opportunity.get(
                            'intervention_type')} intervention for student {opportunity.get(
                                'student_id')}",
                        'priority': 'High' if opportunity.get('urgency') == 'high' else 'Medium',
                        'timeline': 'Immediate' if opportunity.get(
                            'urgency') == 'high' else 'This week'
                    }
                ]
            }
            natural_language_insights.append(insight)

        # Process predictive insights
        for prediction in insights_data.get('predictions', []):
            if prediction.get('prediction_type') == 'outcome_prediction':
                insight = {
                    'insight_text': f"Based on historical patterns, the course is likely to result in: {prediction.get('predicted_outcome')}.",
                    'confidence_level': prediction.get('confidence', 0.7),
                    'supporting_evidence': [
                        f"Match to historical pattern: '{prediction.get('pattern_name')}'"
                    ],
                    'impact_assessment': 'Medium',
                    'historical_validation': f"Similar pattern observed in previous courses with {prediction.get('confidence', 0.7):.0%} accuracy",
                    'action_items': [
                        {
                            'action_description': f"Review historical interventions for '{prediction.get('pattern_name')}' pattern",
                            'priority': 'Medium',
                            'timeline': 'This week'
                        }
                    ]
                }
                natural_language_insights.append(insight)
            elif prediction.get('prediction_type') == 'trend_prediction':
                insight = {
                    'insight_text': f"The {prediction.get(
                        'metric')} is predicted to be {prediction.get(
                            'predicted_value'):.2f} next week, {prediction.get(
                                'predicted_value') - prediction.get(
                                    'current_value'):.2f} {prediction.get(
                                        'predicted_value') > prediction.get(
                                            'current_value') and 'higher' or 'lower'} than current value.",
                    'confidence_level': prediction.get('confidence', 0.7),
                    'supporting_evidence': [
                        f"Current value: {prediction.get('current_value'):.2f}",
                        f"Consistent trend observed in recent weeks"
                    ],
                    'impact_assessment': 'Medium',
                    'action_items': []
                }

                # Add appropriate action items based on metric and direction
                if 'frustration' in prediction.get(
                    'metric', '') and prediction.get(
                        'predicted_value', 0) > prediction.get('current_value', 0):
                    insight['action_items'].append({
                        'action_description': "Prepare additional support resources for increasing frustration",
                        'priority': 'High',
                        'timeline': 'This week'
                    })
                elif 'nps' in prediction.get(
                    'metric', '') and prediction.get(
                        'predicted_value', 0) < prediction.get('current_value', 0):
                    insight['action_items'].append({
                        'action_description': "Investigate factors contributing to predicted NPS decline",
                        'priority': 'High',
                        'timeline': 'Immediate'
                    })

                natural_language_insights.append(insight)

        return natural_language_insights

    async def create_dynamic_recommendations(self, insights: List[Dict[str, Any]],
                                           current_resources: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create dynamic, resource-aware recommendations based on insights.

        Args:
            insights: List of AI insights
            current_resources: Dictionary containing information about current resources

        Returns:
            List of dynamic recommendations
        """
        recommendations = []

        # Extract action items from insights
        all_actions = []
        for insight in insights:
            for action in insight.get('action_items', []):
                all_actions.append({
                    'action': action,
                    'source_insight': insight,
                    'priority_score': self._calculate_priority_score(action, insight)
                })

        # Sort actions by priority score (descending)
        all_actions.sort(key=lambda x: x['priority_score'], reverse=True)

        # Create recommendations based on available resources
        available_staff = current_resources.get('available_staff', 1)
        available_hours = current_resources.get('available_hours', 10)

        # Estimate resource requirements for each action
        total_resources_used = 0
        for action_item in all_actions:
            action = action_item['action']
            insight = action_item['source_insight']

            # Estimate resource requirements (simplified)
            resource_requirement = 1  # Default
            if action.get('priority') == 'High':
                resource_requirement = 2
            elif action.get('priority') == 'Critical':
                resource_requirement = 3

            # Check if we have enough resources
            if total_resources_used + resource_requirement <= available_staff * available_hours:
                recommendations.append({
                    'action_description': action.get('action_description'),
                    'priority': action.get('priority'),
                    'timeline': action.get('timeline'),
                    'resource_requirements': f"{resource_requirement} staff hours",
                    'expected_impact': 'High' if insight.get(
                        'impact_assessment') == 'High' else 'Medium',
                    'source_insight': insight.get('insight_text'),
                    'confidence': insight.get('confidence_level', 0.7)
                })

                total_resources_used += resource_requirement
            else:
                # We've run out of resources, but still include critical actions
                if action.get('priority') == 'Critical':
                    recommendations.append({
                        'action_description': action.get('action_description'),
                        'priority': action.get('priority'),
                        'timeline': action.get('timeline'),
                        'resource_requirements': f"{resource_requirement} staff hours (exceeds current capacity)",
                        'expected_impact': 'High',
                        'source_insight': insight.get('insight_text'),
                        'confidence': insight.get('confidence_level', 0.7),
                        'resource_warning': "This action exceeds current resource capacity but is critical"
                    })

        return recommendations

    def _calculate_priority_score(self, action: Dict[str, Any], insight: Dict[str, Any]) -> float:
        """
        Calculate a priority score for an action based on its priority, timeline, and source insight.

        Args:
            action: Action item dictionary
            insight: Source insight dictionary

        Returns:
            Priority score (higher is more important)
        """
        priority_score = 0.0

        # Priority contribution
        if action.get('priority') == 'Critical':
            priority_score += 10.0
        elif action.get('priority') == 'High':
            priority_score += 7.0
        elif action.get('priority') == 'Medium':
            priority_score += 4.0
        elif action.get('priority') == 'Low':
            priority_score += 1.0

        # Timeline contribution
        if action.get('timeline') == 'Immediate':
            priority_score += 5.0
        elif action.get('timeline') == 'Today':
            priority_score += 4.0
        elif action.get('timeline') == 'This week':
            priority_score += 3.0
        elif action.get('timeline') == 'Next two weeks':
            priority_score += 2.0
        elif action.get('timeline') == 'This month':
            priority_score += 1.0

        # Insight confidence contribution
        priority_score += insight.get('confidence_level', 0.7) * 3.0

        # Impact assessment contribution
        if insight.get('impact_assessment') == 'High':
            priority_score += 3.0
        elif insight.get('impact_assessment') == 'Medium':
            priority_score += 2.0
        elif insight.get('impact_assessment') == 'Low':
            priority_score += 1.0

        return priority_score
