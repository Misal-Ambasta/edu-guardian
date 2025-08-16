
"""Report Generator module for the application.

This module provides functionality related to report generator.
"""
from typing import List, Dict, Any, Optional, Union, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, date
import uuid
import statistics
from collections import Counter

from ..models.weekly_report import WeeklyNPSReport, WeeklyNPSReportCreate, WeeklyNPSReportInDB
from ..models.student_journey import StudentJourney
from ..models.intervention import Intervention
from ..emotion_analysis.analyzer import EmotionProfile
from .historical_pattern import HistoricalPatternService
from .intervention_tracker import EmotionBasedInterventionTracker

class WeeklyNPSReportGenerator:
    """
    Generates comprehensive weekly NPS reports with emotion analysis, risk prediction,
    historical comparison, and intervention tracking.
    """

    def __init__(self, db: Session):
        self.db = db
        self.historical_pattern_service = HistoricalPatternService()
        self.intervention_tracker = EmotionBasedInterventionTracker(db)

    async def generate_comprehensive_report(
        self, course_id: str, week_number: int) -> WeeklyNPSReport:
        """
        Generate a comprehensive weekly NPS report with emotion analysis, risk prediction,
        historical comparison, and intervention tracking.

        Args:
            course_id: The ID of the course to generate the report for
            week_number: The week number to generate the report for

        Returns:
            A WeeklyNPSReport object containing the comprehensive report
        """
        # Collect all data for the week
        student_data = await self.get_week_student_data(course_id, week_number)
        emotion_analysis = await self.analyze_weekly_emotions(student_data)
        risk_predictions = await self.predict_weekly_risks(student_data)
        historical_comparison = await self.compare_with_historical_data(
            course_id, week_number, student_data)
        intervention_tracking = await self.track_weekly_interventions(course_id, week_number)

        # Generate AI insights
        ai_insights = await self.generate_ai_insights(student_data, historical_comparison)

        # Create structured report
        report_date = datetime.now().date()

        # Calculate core NPS metrics
        overall_nps, nps_trend, response_rate, total_responses = self._calculate_core_nps_metrics(
            student_data, course_id, week_number)

        # Calculate aspect scores and trends
        aspect_scores, aspect_trends, critical_aspects = self._calculate_aspect_metrics(
            student_data, course_id, week_number)

        # Create report object
        report = WeeklyNPSReport(
            id=uuid.uuid4(),
            course_id=course_id,
            week_number=week_number,
            report_date=report_date,

            # Core NPS Metrics
            overall_nps=overall_nps,
            nps_trend=nps_trend,
            response_rate=response_rate,
            total_responses=total_responses,

            # Aspect Performance
            aspect_scores=aspect_scores,
            aspect_trends=aspect_trends,
            critical_aspects=critical_aspects,

            # Emotion Intelligence
            average_frustration_level=emotion_analysis.get("average_frustration_level"),
            frustration_distribution=emotion_analysis.get("frustration_distribution"),
            urgency_distribution=emotion_analysis.get("urgency_distribution"),
            emotional_temperature_avg=emotion_analysis.get("emotional_temperature_avg"),
            hidden_dissatisfaction_count=emotion_analysis.get("hidden_dissatisfaction_count"),
            hidden_dissatisfaction_rate=emotion_analysis.get("hidden_dissatisfaction_rate"),

            # Risk Analysis
            high_risk_students=risk_predictions.get("high_risk_students"),
            critical_risk_students=risk_predictions.get("critical_risk_students"),
            dropout_prediction_summary=risk_predictions.get("dropout_prediction_summary"),
            intervention_candidates=risk_predictions.get("intervention_candidates"),

            # Historical Comparison
            similar_historical_periods=historical_comparison.get("similar_historical_periods"),
            historical_pattern_match_confidence=historical_comparison.get(
                "historical_pattern_match_confidence"),
            predicted_outcomes=historical_comparison.get("predicted_outcomes"),

            # Intervention Tracking
            interventions_applied=intervention_tracking.get("interventions_applied"),
            intervention_success_rate=intervention_tracking.get("intervention_success_rate"),
            intervention_types_used=intervention_tracking.get("intervention_types_used"),
            pending_interventions=intervention_tracking.get("pending_interventions"),

            # Report Metadata
            report_confidence=self._calculate_report_confidence(student_data),
            data_quality_score=self._calculate_data_quality_score(student_data),
            recommendations=self.generate_recommendations(risk_predictions, ai_insights),
            executive_summary=self.create_executive_summary(student_data, ai_insights)
        )

        # Store the report in the database
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)

        return report

    async def get_week_student_data(self, course_id: str, week_number: int) -> List[StudentJourney]:
        """
        Get all student journey data for a specific course and week

        Args:
            course_id: The ID of the course
            week_number: The week number

        Returns:
            List of StudentJourney objects for the specified course and week
        """
        student_data = self.db.query(StudentJourney).filter(
            StudentJourney.course_id == course_id,
            StudentJourney.week_number == week_number
        ).all()

        return student_data

    async def analyze_weekly_emotions(self, student_data: List[StudentJourney]) -> Dict[str, Any]:
        """
        Analyze emotions across all students for the week

        Args:
            student_data: List of StudentJourney objects

        Returns:
            Dict containing emotion analysis metrics
        """
        if not student_data:
            return self._get_empty_emotion_analysis()

        # Calculate average frustration level
        frustration_levels = [s.frustration_level for s in student_data if s.frustration_level is not None]
        average_frustration_level = statistics.mean(
            frustration_levels) if frustration_levels else 0.0

        # Calculate frustration distribution
        frustration_types = [s.frustration_type for s in student_data if s.frustration_type is not None]
        frustration_distribution = dict(Counter(frustration_types))

        # Calculate urgency distribution
        urgency_levels = [s.urgency_level for s in student_data if s.urgency_level is not None]
        urgency_distribution = dict(Counter(urgency_levels))

        # Calculate emotional temperature average
        emotional_temperatures = [s.emotional_temperature for s in student_data if s.emotional_temperature is not None]
        emotional_temperature_avg = statistics.mean(
            emotional_temperatures) if emotional_temperatures else 0.0

        # Count hidden dissatisfaction
        hidden_dissatisfaction_count = sum(1 for s in student_data if s.hidden_dissatisfaction_flag)
        hidden_dissatisfaction_rate = hidden_dissatisfaction_count / len(
            student_data) if student_data else 0.0

        return {
            "average_frustration_level": average_frustration_level,
            "frustration_distribution": frustration_distribution,
            "urgency_distribution": urgency_distribution,
            "emotional_temperature_avg": emotional_temperature_avg,
            "hidden_dissatisfaction_count": hidden_dissatisfaction_count,
            "hidden_dissatisfaction_rate": hidden_dissatisfaction_rate
        }

    async def predict_weekly_risks(self, student_data: List[StudentJourney]) -> Dict[str, Any]:
        """
        Predict risks based on student emotion data

        Args:
            student_data: List of StudentJourney objects

        Returns:
            Dict containing risk prediction metrics
        """
        if not student_data:
            return self._get_empty_risk_predictions()

        # Count high risk students (high frustration + high urgency)
        high_risk_students = sum(1 for s in student_data
                               if (
                                   s.frustration_level is not None and s.frustration_level > 0.7) and
                                  (s.urgency_level in ["high", "critical", "immediate"]))

        # Count critical risk students (critical frustration + immediate urgency + dropout risk emotions)
        critical_risk_students = sum(1 for s in student_data
                                  if (s.frustration_intensity == "critical") and
                                     (s.urgency_level == "immediate") and
                                     (s.emotional_trajectory == "declining"))

        # Create dropout prediction summary
        dropout_prediction_summary = {
            "low_risk": sum(
                1 for s in student_data if s.frustration_level is not None and s.frustration_level < 0.3),
            "medium_risk": sum(
                1 for s in student_data if s.frustration_level is not None and 0.3 <= s.frustration_level <= 0.7),
            "high_risk": high_risk_students,
            "critical_risk": critical_risk_students
        }

        # Count intervention candidates (students who need immediate intervention)
        intervention_candidates = sum(1 for s in student_data
                                    if (s.urgency_level in ["high", "critical", "immediate"]) or
                                       (s.frustration_intensity in ["severe", "critical"]) or
                                       (
                                           s.hidden_dissatisfaction_flag and s.hidden_dissatisfaction_confidence > 0.7))

        return {
            "high_risk_students": high_risk_students,
            "critical_risk_students": critical_risk_students,
            "dropout_prediction_summary": dropout_prediction_summary,
            "intervention_candidates": intervention_candidates
        }

    async def compare_with_historical_data(self, course_id: str, week_number: int,
                                         student_data: List[StudentJourney]) -> Dict[str, Any]:
        """
        Compare current week data with historical data

        Args:
            course_id: The ID of the course
            week_number: The week number
            student_data: List of StudentJourney objects

        Returns:
            Dict containing historical comparison metrics
        """
        if not student_data:
            return self._get_empty_historical_comparison()

        # Find similar historical periods using the historical pattern service
        similar_periods = []
        historical_pattern_match_confidence = 0.0
        predicted_outcomes = {}

        # For each student, find similar historical patterns
        for student in student_data:
            try:
                # Find historical patterns for this student
                historical_pattern = await self.historical_pattern_service.find_emotion_patterns(
                    student_id=student.student_id,
                    course_id=course_id,
                    week_number=week_number
                )

                # If we found a pattern with matches, add it to our similar periods
                if historical_pattern and hasattr(
                    historical_pattern, 'pattern_matches') and historical_pattern.pattern_matches:
                    for match in historical_pattern.pattern_matches:
                        similar_period = {
                            "course_id": match.course_id,
                            "week_number": match.week_number,
                            "similarity_score": match.similarity_score,
                            "outcome": match.outcome if hasattr(match, 'outcome') else None
                        }
                        similar_periods.append(similar_period)

                    # Update confidence based on pattern match confidence
                    if hasattr(historical_pattern, 'match_confidence'):
                        historical_pattern_match_confidence = max(
                            historical_pattern_match_confidence,
                            historical_pattern.match_confidence
                        )

                    # Get predicted outcomes if available
                    if hasattr(historical_pattern, 'predicted_outcomes'):
                        predicted_outcomes = historical_pattern.predicted_outcomes
            except Exception as e:
                # Log the error but continue processing other students
                print(
                    f"Error finding historical patterns for student {student.student_id}: {str(e)}")
                continue

        # Limit to top 5 similar periods
        similar_periods = sorted(
            similar_periods, key=lambda x: x.get("similarity_score", 0), reverse=True)[:5]

        return {
            "similar_historical_periods": similar_periods,
            "historical_pattern_match_confidence": historical_pattern_match_confidence,
            "predicted_outcomes": predicted_outcomes
        }

    async def track_weekly_interventions(self, course_id: str, week_number: int) -> Dict[str, Any]:
        """
        Track interventions applied during the week

        Args:
            course_id: The ID of the course
            week_number: The week number

        Returns:
            Dict containing intervention tracking metrics
        """
        # Get all interventions for this course and week
        interventions = self.db.query(Intervention).filter(
            Intervention.course_id == course_id,
            Intervention.week_number == week_number
        ).all()

        if not interventions:
            return self._get_empty_intervention_tracking()

        # Count total interventions applied
        interventions_applied = len(interventions)

        # Calculate intervention success rate
        successful_interventions = sum(1 for i in interventions if i.success_flag)
        intervention_success_rate = successful_interventions / interventions_applied if interventions_applied > 0 else 0.0

        # Count intervention types used
        intervention_types = [i.intervention_type for i in interventions if i.intervention_type is not None]
        intervention_types_used = dict(Counter(intervention_types))

        # Count pending interventions
        pending_interventions = sum(1 for i in interventions if not i.completed_flag)

        return {
            "interventions_applied": interventions_applied,
            "intervention_success_rate": intervention_success_rate,
            "intervention_types_used": intervention_types_used,
            "pending_interventions": pending_interventions
        }

    async def generate_ai_insights(self, student_data: List[StudentJourney],
                                 historical_comparison: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate AI insights based on student data and historical comparison

        Args:
            student_data: List of StudentJourney objects
            historical_comparison: Dict containing historical comparison metrics

        Returns:
            List of AI insights
        """
        insights = []

        if not student_data:
            return insights

        # Insight 1: Frustration patterns
        frustration_types = [s.frustration_type for s in student_data if s.frustration_type is not None]
        if frustration_types:
            most_common_frustration = Counter(frustration_types).most_common(1)[0][0]
            insights.append({
                "title": "Dominant Frustration Pattern",
                "description": f"The most common frustration type is '{most_common_frustration}', indicating potential issues in this area.",
                "confidence": 0.85,
                "action_items": [
                    {
                        "title": f"Address {most_common_frustration} issues",
                        "description": f"Develop targeted interventions for {most_common_frustration}-related frustrations."
                    }
                ]
            })

        # Insight 2: Hidden dissatisfaction
        hidden_dissatisfaction_students = [s for s in student_data if s.hidden_dissatisfaction_flag]
        if hidden_dissatisfaction_students:
            insights.append({
                "title": "Hidden Dissatisfaction Detected",
                "description": f"Detected {len(
                    hidden_dissatisfaction_students)} students with hidden dissatisfaction that may escalate if not addressed.",
                "confidence": 0.75,
                "action_items": [
                    {
                        "title": "Proactive outreach",
                        "description": "Conduct proactive outreach to students with hidden dissatisfaction before issues escalate."
                    }
                ]
            })

        # Insight 3: Historical pattern match
        if historical_comparison.get(
            "similar_historical_periods") and historical_comparison.get(
                "historical_pattern_match_confidence", 0) > 0.7:
            insights.append({
                "title": "Historical Pattern Match",
                "description": "Current emotional patterns match historical data that led to specific outcomes. Review predicted outcomes for proactive planning.",
                "confidence": historical_comparison.get("historical_pattern_match_confidence", 0),
                "action_items": [
                    {
                        "title": "Apply successful historical interventions",
                        "description": "Implement interventions that were successful in similar historical situations."
                    }
                ]
            })

        # Insight 4: Emotional trajectory
        declining_trajectories = sum(
            1 for s in student_data if s.emotional_trajectory == "declining")
        if declining_trajectories > 0:
            insights.append({
                "title": "Declining Emotional Trajectories",
                "description": f"Detected {declining_trajectories} students with declining emotional trajectories, indicating increasing frustration or disengagement.",
                "confidence": 0.8,
                "action_items": [
                    {
                        "title": "Targeted support for declining students",
                        "description": "Provide additional support and check-ins for students with declining emotional trajectories."
                    }
                ]
            })

        return insights

    def create_executive_summary(self, student_data: List[StudentJourney],
                               ai_insights: List[Dict[str, Any]]) -> str:
        """
        Create an executive summary of the weekly report

        Args:
            student_data: List of StudentJourney objects
            ai_insights: List of AI insights

        Returns:
            Executive summary as a string
        """
        if not student_data:
            return "Insufficient data available for this week."

        # Calculate key metrics for the summary
        nps_scores = [s.nps_score for s in student_data if s.nps_score is not None]
        avg_nps = statistics.mean(nps_scores) if nps_scores else 0

        high_urgency_count = sum(
            1 for s in student_data if s.urgency_level in ["high", "critical", "immediate"])
        high_urgency_percentage = (
            high_urgency_count / len(student_data)) * 100 if student_data else 0

        hidden_dissatisfaction_count = sum(1 for s in student_data if s.hidden_dissatisfaction_flag)

        # Create the summary
        summary = f"""Weekly NPS Report Executive Summary

Overall NPS: {avg_nps:.1f}/10
Total Responses: {len(student_data)}
High Urgency Students: {high_urgency_count} ({high_urgency_percentage:.1f}%)
Hidden Dissatisfaction Detected: {hidden_dissatisfaction_count}

Key Insights:
"""

        # Add insights to the summary
        for i, insight in enumerate(ai_insights[:3], 1):  # Include up to 3 insights
            summary += f"\n{i}. {insight['title']}: {insight['description']}"

        return summary

    def generate_recommendations(self, risk_predictions: Dict[str, Any],
                               ai_insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on risk predictions and AI insights

        Args:
            risk_predictions: Dict containing risk prediction metrics
            ai_insights: List of AI insights

        Returns:
            List of recommendations
        """
        recommendations = []

        # Add recommendations from AI insights
        for insight in ai_insights:
            for action_item in insight.get("action_items", []):
                recommendations.append({
                    "title": action_item.get("title"),
                    "description": action_item.get("description"),
                    "priority": "high" if insight.get("confidence", 0) > 0.8 else "medium",
                    "source": "ai_insight"
                })

        # Add recommendations based on risk predictions
        if risk_predictions.get("critical_risk_students", 0) > 0:
            recommendations.append({
                "title": "Immediate intervention for critical risk students",
                "description": f"Provide immediate support to {risk_predictions.get(
                    'critical_risk_students')} students at critical risk of dropping out.",
                "priority": "high",
                "source": "risk_prediction"
            })

        if risk_predictions.get("high_risk_students", 0) > 0:
            recommendations.append({
                "title": "Support for high risk students",
                "description": f"Develop targeted support plan for {risk_predictions.get(
                    'high_risk_students')} high-risk students.",
                "priority": "high",
                "source": "risk_prediction"
            })

        return recommendations

    def _calculate_core_nps_metrics(self, student_data: List[StudentJourney],
                                  course_id: str, week_number: int) -> Tuple[float, float, float, int]:
        """
        Calculate core NPS metrics

        Args:
            student_data: List of StudentJourney objects
            course_id: The ID of the course
            week_number: The week number

        Returns:
            Tuple containing (overall_nps, nps_trend, response_rate, total_responses)
        """
        # Calculate overall NPS
        nps_scores = [s.nps_score for s in student_data if s.nps_score is not None]
        overall_nps = statistics.mean(nps_scores) if nps_scores else 0.0

        # Calculate NPS trend (compare with previous week)
        previous_week_data = self.db.query(StudentJourney).filter(
            StudentJourney.course_id == course_id,
            StudentJourney.week_number == week_number - 1
        ).all()

        previous_nps_scores = [s.nps_score for s in previous_week_data if s.nps_score is not None]
        previous_overall_nps = statistics.mean(
            previous_nps_scores) if previous_nps_scores else overall_nps

        nps_trend = overall_nps - previous_overall_nps

        # Calculate response rate and total responses
        total_responses = len(nps_scores)

        # Get total enrolled students (approximation based on previous weeks)
        all_students_query = self.db.query(StudentJourney.student_id).distinct().filter(
            StudentJourney.course_id == course_id,
            StudentJourney.week_number <= week_number
        )
        total_enrolled = all_students_query.count()

        response_rate = total_responses / total_enrolled if total_enrolled > 0 else 1.0

        return overall_nps, nps_trend, response_rate, total_responses

    def _calculate_aspect_metrics(self, student_data: List[StudentJourney],
                                course_id: str, week_number: int) -> Tuple[Dict[str, float], Dict[str, float], List[str]]:
        """
        Calculate aspect scores, trends, and identify critical aspects

        Args:
            student_data: List of StudentJourney objects
            course_id: The ID of the course
            week_number: The week number

        Returns:
            Tuple containing (aspect_scores, aspect_trends, critical_aspects)
        """
        # Define aspect fields
        aspect_fields = {
            "lms_usability": "lms_usability_score",
            "instructor_quality": "instructor_quality_score",
            "content_difficulty": "content_difficulty_score",
            "support_quality": "support_quality_score",
            "course_pace": "course_pace_score"
        }

        # Calculate current aspect scores
        aspect_scores = {}
        for aspect, field in aspect_fields.items():
            scores = [getattr(s, field) for s in student_data if getattr(s, field) is not None]
            aspect_scores[aspect] = statistics.mean(scores) if scores else 0.0

        # Get previous week data for trend calculation
        previous_week_data = self.db.query(StudentJourney).filter(
            StudentJourney.course_id == course_id,
            StudentJourney.week_number == week_number - 1
        ).all()

        # Calculate aspect trends
        aspect_trends = {}
        previous_aspect_scores = {}

        for aspect, field in aspect_fields.items():
            previous_scores = [getattr(
                s, field) for s in previous_week_data if getattr(s, field) is not None]
            previous_aspect_scores[aspect] = statistics.mean(
                previous_scores) if previous_scores else aspect_scores[aspect]
            aspect_trends[aspect] = aspect_scores[aspect] - previous_aspect_scores[aspect]

        # Identify critical aspects (below 3.0 or declining by more than 0.5)
        critical_aspects = [
            aspect for aspect, score in aspect_scores.items()
            if score < 3.0 or (aspect in aspect_trends and aspect_trends[aspect] < -0.5)
        ]

        return aspect_scores, aspect_trends, critical_aspects

    def _calculate_report_confidence(self, student_data: List[StudentJourney]) -> float:
        """
        Calculate overall confidence in the report accuracy

        Args:
            student_data: List of StudentJourney objects

        Returns:
            Report confidence score (0.0-1.0)
        """
        if not student_data:
            return 0.0

        # Base confidence on sample size
        sample_size_factor = min(1.0, len(student_data) / 30)  # Max confidence at 30+ responses

        # Check data completeness
        completeness_scores = []
        for student in student_data:
            fields_present = sum(1 for f in [
                student.nps_score,
                student.frustration_level,
                student.engagement_level,
                student.confidence_level,
                student.satisfaction_level,
                student.emotional_temperature
            ] if f is not None)
            completeness_scores.append(fields_present / 6)  # 6 key fields

        data_completeness_factor = statistics.mean(
            completeness_scores) if completeness_scores else 0.0

        # Calculate overall confidence
        report_confidence = (sample_size_factor * 0.7) + (data_completeness_factor * 0.3)

        return report_confidence

    def _calculate_data_quality_score(self, student_data: List[StudentJourney]) -> float:
        """
        Calculate data quality score

        Args:
            student_data: List of StudentJourney objects

        Returns:
            Data quality score (0.0-1.0)
        """
        if not student_data:
            return 0.0

        # Check for missing values in key fields
        missing_values_count = 0
        total_fields = 0

        for student in student_data:
            for field in [
                "nps_score", "frustration_level", "engagement_level",
                "confidence_level", "satisfaction_level", "emotional_temperature"
            ]:
                total_fields += 1
                if getattr(student, field) is None:
                    missing_values_count += 1

        completeness_score = 1.0 - (
            missing_values_count / total_fields if total_fields > 0 else 0.0)

        # Check for consistency in data
        consistency_scores = []
        for student in student_data:
            if all(f is not None for f in [
                student.frustration_level, student.satisfaction_level
            ]):
                # Check if frustration and satisfaction are inversely related (as expected)
                expected_inverse = student.frustration_level + student.satisfaction_level
                # Should be close to 1.0 if perfectly inverse
                consistency = 1.0 - abs(expected_inverse - 1.0)
                consistency_scores.append(consistency)

        consistency_score = statistics.mean(consistency_scores) if consistency_scores else 0.5

        # Calculate overall data quality score
        data_quality_score = (completeness_score * 0.7) + (consistency_score * 0.3)

        return data_quality_score

    def _get_empty_emotion_analysis(self) -> Dict[str, Any]:
        """
        Return empty emotion analysis structure
        """
        return {
            "average_frustration_level": 0.0,
            "frustration_distribution": {},
            "urgency_distribution": {},
            "emotional_temperature_avg": 0.0,
            "hidden_dissatisfaction_count": 0,
            "hidden_dissatisfaction_rate": 0.0
        }

    def _get_empty_risk_predictions(self) -> Dict[str, Any]:
        """
        Return empty risk predictions structure
        """
        return {
            "high_risk_students": 0,
            "critical_risk_students": 0,
            "dropout_prediction_summary": {
                "low_risk": 0,
                "medium_risk": 0,
                "high_risk": 0,
                "critical_risk": 0
            },
            "intervention_candidates": 0
        }

    def _get_empty_historical_comparison(self) -> Dict[str, Any]:
        """
        Return empty historical comparison structure
        """
        return {
            "similar_historical_periods": [],
            "historical_pattern_match_confidence": 0.0,
            "predicted_outcomes": {}
        }

    def _get_empty_intervention_tracking(self) -> Dict[str, Any]:
        """
        Return empty intervention tracking structure
        """
        return {
            "interventions_applied": 0,
            "intervention_success_rate": 0.0,
            "intervention_types_used": {},
            "pending_interventions": 0
        }
