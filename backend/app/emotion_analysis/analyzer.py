
"""Analyzer module for the application.

This module provides functionality related to analyzer.
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Literal, Any, Tuple
import re
import json
from collections import Counter

class EmotionProfile(BaseModel):
    """
    Comprehensive emotion profile based on text analysis
    """
    # Primary Emotions
    frustration_level: float  # 0.0 = calm, 1.0 = extremely frustrated
    engagement_level: float   # 0.0 = disengaged, 1.0 = highly engaged
    confidence_level: float   # 0.0 = no confidence, 1.0 = very confident
    satisfaction_level: float # 0.0 = unsatisfied, 1.0 = very satisfied

    # Detailed Frustration Classification
    frustration_type: str  # 'technical', 'content', 'pace', 'support', 'mixed'
    frustration_intensity: str  # 'mild', 'moderate', 'severe', 'critical'
    frustration_trend: str  # 'increasing', 'decreasing', 'stable', 'spiking'

    # Urgency Indicators
    urgency_level: str  # 'low', 'medium', 'high', 'critical', 'immediate'
    urgency_signals: List[str]  # ['considering_dropping', 'missed_deadlines', 'help_requests']
    response_urgency: str  # 'within_hour', 'same_day', 'within_week', 'routine'

    # Emotional Temperature
    emotional_temperature: float  # 0.0 = cold/detached, 1.0 = hot/emotional
    emotional_volatility: float   # 0.0 = stable, 1.0 = highly volatile
    emotional_trajectory: str     # 'improving', 'declining', 'neutral', 'fluctuating'

    # Hidden Dissatisfaction Detection
    hidden_dissatisfaction_flag: bool  # True if dissatisfaction masked by politeness
    hidden_dissatisfaction_confidence: float  # 0.0-1.0 confidence in detection
    hidden_signals: List[str]  # ['praise_with_reservations', 'faint_praise', 'diplomatic_language']
    politeness_mask_level: float  # 0.0 = direct, 1.0 = heavily masked

    # Advanced Emotional Markers
    dropout_risk_emotions: List[str]  # ['helplessness', 'overwhelm', 'isolation']
    positive_recovery_indicators: List[str]  # ['hope', 'determination', 'gratitude']
    emotional_triggers: List[str]  # What specifically triggers negative emotions

    # Meta-emotional Analysis
    emotion_coherence: float  # How consistent emotions are across aspects
    sentiment_authenticity: float  # How genuine the emotional expression appears
    emotional_complexity: str  # 'simple', 'mixed', 'complex', 'conflicted'

class AdvancedEmotionAnalyzer:
    """
    Advanced emotion analysis engine for detecting complex emotions in student feedback
    """

    def __init__(self):
        # Initialize dictionaries for emotion analysis
        self.frustration_words = {
            "technical": ["website", "platform", "error", "bug", "login", "system", "lms", "interface", "broken", "glitch"],
            "content": ["material", "content", "lecture", "understand", "concept", "difficult", "confusing", "unclear"],
            "support": ["help", "support", "response", "answer", "question", "ignored", "waiting", "unresponsive"],
            "pace": ["fast", "slow", "pace", "speed", "keep up", "behind", "rushed", "dragging"]
        }

        self.urgency_phrases = {
            "immediate": ["immediately", "urgent", "asap", "right now", "can't wait", "emergency", "critical", "desperate"],
            "critical": ["very urgent", "need help now", "can't continue", "blocking me", "impossible", "giving up"],
            "high": ["soon", "quickly", "need help", "struggling", "important", "priority", "stuck"],
            "medium": ["when possible", "would like", "appreciate", "should be addressed", "needs attention"],
            "low": ["eventually", "minor", "small issue", "not urgent", "whenever", "no rush"]
        }

        self.hidden_dissatisfaction_patterns = [
            r"(it's|its) (fine|okay|alright)( I guess| I suppose)?",
            r"not (too|that) bad",
            r"could be (better|worse)",
            r"I (suppose|guess) it('s| is) (okay|fine|alright)",
            r"(works|functions) (well enough|adequately)",
            r"(somewhat|kind of|sort of) (helpful|useful)",
            r"(better than|not as bad as) (expected|anticipated)",
            r"(can't complain|no complaints) (too much|much)",
            r"(doing|trying) (my|their) best",
            r"(probably|maybe) just me"
        ]

        self.engagement_indicators = {
            "high": ["excited", "interested", "engaged", "fascinating", "love", "enjoy", "captivating"],
            "medium": ["good", "okay", "fine", "decent", "reasonable", "satisfactory"],
            "low": ["boring", "dull", "uninteresting", "tedious", "monotonous", "disengaged"]
        }

        self.confidence_indicators = {
            "high": ["confident", "sure", "certain", "understand", "grasp", "mastered", "clear"],
            "medium": ["somewhat understand", "getting it", "making progress", "improving"],
            "low": ["confused", "lost", "uncertain", "unclear", "don't understand", "struggling"]
        }

        self.dropout_risk_emotions = [
            "helplessness", "overwhelm", "isolation", "despair", "frustration",
            "anxiety", "hopelessness", "defeat", "inadequacy", "disconnection"
        ]

        self.positive_recovery_indicators = [
            "hope", "determination", "gratitude", "optimism", "relief",
            "confidence", "satisfaction", "enthusiasm", "motivation", "connection"
        ]

    def analyze_text(
        self, text: str, aspect_scores: Dict[str, int] = None, historical_data: List[Dict] = None) -> EmotionProfile:
        """
        Analyze text for emotions and return a comprehensive emotion profile

        Args:
            text: The feedback text to analyze
            aspect_scores: Optional dictionary of aspect scores (1-5 scale)
            historical_data: Optional list of previous emotion profiles for trend analysis

        Returns:
            EmotionProfile: Comprehensive emotion analysis
        """
        # Core emotion detection
        frustration_level = self._detect_frustration_level(text)
        engagement_level = self._detect_engagement_level(text)
        confidence_level = self._detect_confidence_level(text)
        satisfaction_level = self._calculate_satisfaction_level(text, aspect_scores)

        # Frustration analysis
        frustration_type = self._determine_frustration_type(text)
        frustration_intensity = self._determine_frustration_intensity(frustration_level)
        frustration_trend = self._determine_frustration_trend(historical_data)

        # Urgency analysis
        urgency_level = self._detect_urgency(text)
        urgency_signals = self._detect_urgency_signals(text)
        response_urgency = self._determine_response_urgency(urgency_level, frustration_level)

        # Emotional temperature analysis
        emotional_temperature = self._calculate_emotional_temperature(text)
        emotional_volatility = self._calculate_emotional_volatility(historical_data)
        emotional_trajectory = self._determine_emotional_trajectory(historical_data)

        # Hidden dissatisfaction analysis
        hidden_dissatisfaction, hidden_confidence, hidden_signals = self._analyze_hidden_dissatisfaction(text, satisfaction_level)
        politeness_mask_level = self._calculate_politeness_mask(text, hidden_dissatisfaction)

        # Advanced emotional markers
        dropout_risk_emotions = self._detect_dropout_risk_emotions(text)
        positive_recovery_indicators = self._detect_positive_recovery_indicators(text)
        emotional_triggers = self._identify_emotional_triggers(text)

        # Meta-emotional analysis
        emotion_coherence = self._calculate_emotion_coherence(
            frustration_level, engagement_level, confidence_level, satisfaction_level)
        sentiment_authenticity = self._calculate_sentiment_authenticity(
            text, hidden_dissatisfaction)
        emotional_complexity = self._determine_emotional_complexity(text)

        return EmotionProfile(
            # Primary Emotions
            frustration_level=frustration_level,
            engagement_level=engagement_level,
            confidence_level=confidence_level,
            satisfaction_level=satisfaction_level,

            # Detailed Frustration Classification
            frustration_type=frustration_type,
            frustration_intensity=frustration_intensity,
            frustration_trend=frustration_trend,

            # Urgency Indicators
            urgency_level=urgency_level,
            urgency_signals=urgency_signals,
            response_urgency=response_urgency,

            # Emotional Temperature
            emotional_temperature=emotional_temperature,
            emotional_volatility=emotional_volatility,
            emotional_trajectory=emotional_trajectory,

            # Hidden Dissatisfaction Detection
            hidden_dissatisfaction_flag=hidden_dissatisfaction,
            hidden_dissatisfaction_confidence=hidden_confidence,
            hidden_signals=hidden_signals,
            politeness_mask_level=politeness_mask_level,

            # Advanced Emotional Markers
            dropout_risk_emotions=dropout_risk_emotions,
            positive_recovery_indicators=positive_recovery_indicators,
            emotional_triggers=emotional_triggers,

            # Meta-emotional Analysis
            emotion_coherence=emotion_coherence,
            sentiment_authenticity=sentiment_authenticity,
            emotional_complexity=emotional_complexity
        )

    def _detect_frustration_level(self, text: str) -> float:
        """Detect frustration level in text"""
        # Combine all frustration words across categories
        all_frustration_words = []
        for category_words in self.frustration_words.values():
            all_frustration_words.extend(category_words)

        # Add general frustration words
        general_frustration = ["frustrating", "difficult", "confused", "struggle", "hard", "annoying",
                              "terrible", "awful", "horrible", "useless", "waste", "disappointed"]
        all_frustration_words.extend(general_frustration)

        # Count occurrences and weight by intensity
        strong_indicators = ["extremely", "very", "incredibly", "terribly", "absolutely"]

        base_count = sum(1 for word in all_frustration_words if word.lower() in text.lower())
        intensity_multiplier = 1.0 + (
            0.5 * sum(1 for word in strong_indicators if word.lower() in text.lower()))

        # Calculate frustration score (0-1 scale)
        frustration_score = min(base_count * 0.15 * intensity_multiplier, 1.0)

        # Check for explicit frustration statements
        explicit_patterns = [
            r"(I('m| am)|feeling) (very |really |extremely )?(frustrated|annoyed|upset)",
            r"this is (very |really |extremely )?(frustrating|annoying|infuriating)",
            r"(can't|cannot) (stand|handle|deal with) (this|it) (anymore)?"
        ]

        if any(re.search(pattern, text.lower()) for pattern in explicit_patterns):
            frustration_score = max(frustration_score, 0.7)  # Minimum 0.7 for explicit frustration

        return frustration_score

    def _detect_engagement_level(self, text: str) -> float:
        """Detect engagement level in text"""
        engagement_score = 0.5  # Default neutral engagement

        # Check for engagement indicators
        high_count = sum(
            1 for word in self.engagement_indicators["high"] if word.lower() in text.lower())
        medium_count = sum(
            1 for word in self.engagement_indicators["medium"] if word.lower() in text.lower())
        low_count = sum(
            1 for word in self.engagement_indicators["low"] if word.lower() in text.lower())

        # Calculate weighted score
        total_indicators = high_count + medium_count + low_count
        if total_indicators > 0:
            weighted_score = (
                high_count * 0.9 + medium_count * 0.5 + low_count * 0.1) / total_indicators
            engagement_score = weighted_score

        # Check for explicit engagement statements
        if re.search(r"(I (really |absolutely )?(love|enjoy|like))", text.lower()):
            engagement_score = max(engagement_score, 0.8)
        if re.search(r"(I (really |absolutely )?(hate|dislike|can't stand))", text.lower()):
            engagement_score = min(engagement_score, 0.2)

        return engagement_score

    def _detect_confidence_level(self, text: str) -> float:
        """Detect confidence level in text"""
        confidence_score = 0.5  # Default neutral confidence

        # Check for confidence indicators
        high_count = sum(
            1 for word in self.confidence_indicators["high"] if word.lower() in text.lower())
        medium_count = sum(
            1 for word in self.confidence_indicators["medium"] if word.lower() in text.lower())
        low_count = sum(
            1 for word in self.confidence_indicators["low"] if word.lower() in text.lower())

        # Calculate weighted score
        total_indicators = high_count + medium_count + low_count
        if total_indicators > 0:
            weighted_score = (
                high_count * 0.9 + medium_count * 0.5 + low_count * 0.1) / total_indicators
            confidence_score = weighted_score

        # Check for explicit confidence statements
        if re.search(
            r"(I('m| am) (very |really |extremely )?(confident|sure|certain))", text.lower()):
            confidence_score = max(confidence_score, 0.8)
        if re.search(
            r"(I('m| am) (very |really |extremely )?(confused|lost|unsure))", text.lower()):
            confidence_score = min(confidence_score, 0.2)

        return confidence_score

    def _calculate_satisfaction_level(
        self, text: str, aspect_scores: Dict[str, int] = None) -> float:
        """Calculate satisfaction level based on text and aspect scores"""
        text_satisfaction = 0.5  # Default neutral satisfaction

        # Satisfaction indicators in text
        positive_indicators = ["satisfied", "happy", "pleased", "great", "excellent", "good", "helpful"]
        negative_indicators = ["unsatisfied", "unhappy", "disappointed", "poor", "terrible", "bad", "unhelpful"]

        pos_count = sum(1 for word in positive_indicators if word.lower() in text.lower())
        neg_count = sum(1 for word in negative_indicators if word.lower() in text.lower())

        total_indicators = pos_count + neg_count
        if total_indicators > 0:
            text_satisfaction = pos_count / total_indicators

        # If aspect scores are provided, incorporate them
        if aspect_scores:
            # Convert 1-5 scale to 0-1 scale
            avg_aspect_score = sum(aspect_scores.values()) / len(aspect_scores)
            aspect_satisfaction = (avg_aspect_score - 1) / 4  # Convert 1-5 to 0-1

            # Combine text and aspect satisfaction (weighted average)
            satisfaction_level = (text_satisfaction * 0.6) + (aspect_satisfaction * 0.4)
        else:
            satisfaction_level = text_satisfaction

        return satisfaction_level

    def _determine_frustration_type(self, text: str) -> str:
        """Determine the type of frustration"""
        # Count matches for each frustration type
        matches = {}
        for ftype, keywords in self.frustration_words.items():
            matches[ftype] = sum(1 for word in keywords if word.lower() in text.lower())

        # Find the dominant frustration type
        if sum(matches.values()) == 0:
            return "mixed"  # Default if no matches

        max_type = max(matches, key=matches.get)

        # Check if it's truly dominant or mixed
        if matches[max_type] > 0 and sum(matches.values()) > matches[max_type] * 1.5:
            return "mixed"
        return max_type if matches[max_type] > 0 else "mixed"

    def _determine_frustration_intensity(self, frustration_level: float) -> str:
        """Determine frustration intensity based on level"""
        if frustration_level < 0.3:
            return "mild"
        elif frustration_level < 0.6:
            return "moderate"
        elif frustration_level < 0.85:
            return "severe"
        else:
            return "critical"

    def _determine_frustration_trend(self, historical_data: List[Dict] = None) -> str:
        """Determine frustration trend based on historical data"""
        if not historical_data or len(historical_data) < 2:
            return "stable"  # Default with insufficient data

        # Extract frustration levels from most recent entries (up to 3)
        recent_entries = sorted(
            historical_data, key=lambda x: x.get('timestamp', 0), reverse=True)[:3]
        frustration_levels = [entry.get('frustration_level', 0.5) for entry in recent_entries]

        # Calculate trend
        if len(frustration_levels) >= 2:
            latest = frustration_levels[0]
            previous = sum(
                frustration_levels[1:]) / len(frustration_levels[1:])  # Average of previous entries

            diff = latest - previous
            if diff > 0.15:
                return "increasing"
            elif diff < -0.15:
                return "decreasing"
            elif any(abs(latest - level) > 0.25 for level in frustration_levels[1:]):
                return "spiking"

        return "stable"

    def _detect_urgency(self, text: str) -> str:
        """Detect urgency level in text"""
        # Check for urgency phrases from most urgent to least
        for level, phrases in self.urgency_phrases.items():
            if any(phrase in text.lower() for phrase in phrases):
                return level

        return "low"  # Default urgency level

    def _detect_urgency_signals(self, text: str) -> List[str]:
        """Detect specific urgency signals in text"""
        signals = []

        # Check for specific urgency signals
        if re.search(r"(thinking|considering) (of )?(dropping|quitting|leaving)", text.lower()):
            signals.append("considering_dropping")

        if re.search(
            r"(missed|missing|late|behind on) (deadline|assignment|submission|work)", text.lower()):
            signals.append("missed_deadlines")

        if re.search(r"(need|asking for|requesting) help", text.lower()):
            signals.append("help_requests")

        if re.search(
            r"(can't|cannot|unable to) (continue|proceed|move forward|progress)", text.lower()):
            signals.append("progress_blocked")

        if re.search(r"(deadline|due date) (approaching|coming up|soon)", text.lower()):
            signals.append("timeline_pressure")

        if re.search(r"(tried|attempted) (multiple times|several times|many times)", text.lower()):
            signals.append("repeated_attempts")

        return signals

    def _determine_response_urgency(self, urgency_level: str, frustration_level: float) -> str:
        """Determine how quickly a response is needed"""
        # Map urgency levels to response timeframes
        urgency_mapping = {
            "immediate": "within_hour",
            "critical": "within_hour",
            "high": "same_day",
            "medium": "within_week",
            "low": "routine"
        }

        # Get base response urgency from mapping
        response_urgency = urgency_mapping.get(urgency_level, "routine")

        # Escalate based on frustration level
        if frustration_level > 0.8 and response_urgency != "within_hour":
            # Escalate one level for high frustration
            if response_urgency == "same_day":
                response_urgency = "within_hour"
            elif response_urgency == "within_week":
                response_urgency = "same_day"
            elif response_urgency == "routine":
                response_urgency = "within_week"

        return response_urgency

    def _calculate_emotional_temperature(self, text: str) -> float:
        """Calculate emotional temperature (hot vs cold emotions)"""
        # Hot emotion words (intense, activated)
        hot_words = ["angry", "furious", "excited", "thrilled", "frustrated", "enraged",
                    "anxious", "stressed", "panicked", "desperate", "urgent", "passionate"]

        # Cold emotion words (detached, deactivated)
        cold_words = ["calm", "detached", "indifferent", "bored", "tired", "exhausted",
                     "apathetic", "disinterested", "resigned", "defeated", "numb"]

        # Intensity modifiers
        intensifiers = ["very", "extremely", "incredibly", "absolutely", "completely", "totally"]

        # Count occurrences
        hot_count = sum(1 for word in hot_words if word.lower() in text.lower())
        cold_count = sum(1 for word in cold_words if word.lower() in text.lower())
        intensifier_count = sum(1 for word in intensifiers if word.lower() in text.lower())

        # Calculate base temperature
        total_emotion_words = hot_count + cold_count
        if total_emotion_words == 0:
            base_temp = 0.5  # Neutral temperature
        else:
            base_temp = hot_count / total_emotion_words

        # Apply intensifier effect
        intensity_factor = 1.0 + (0.1 * intensifier_count)

        # Calculate final temperature (ensure it stays in 0-1 range)
        temperature = min(max(base_temp * intensity_factor, 0.0), 1.0)

        # Adjust for exclamation marks and capitalization
        exclamation_count = text.count('!')
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)

        temperature += min(exclamation_count * 0.05, 0.25)  # Up to 0.25 boost for exclamations
        temperature += min(caps_ratio * 0.5, 0.25)  # Up to 0.25 boost for ALL CAPS

        return min(temperature, 1.0)  # Ensure final value is at most 1.0

    def _calculate_emotional_volatility(self, historical_data: List[Dict] = None) -> float:
        """Calculate emotional volatility based on historical data"""
        if not historical_data or len(historical_data) < 2:
            return 0.3  # Default moderate volatility with insufficient data

        # Extract emotion measures from recent entries (up to 5)
        recent_entries = sorted(
            historical_data, key=lambda x: x.get('timestamp', 0), reverse=True)[:5]

        # Track changes in key emotional dimensions
        emotion_dimensions = ['frustration_level', 'satisfaction_level', 'emotional_temperature']
        changes = []

        # Calculate changes between consecutive entries
        for i in range(len(recent_entries) - 1):
            for dimension in emotion_dimensions:
                current = recent_entries[i].get(dimension, 0.5)
                previous = recent_entries[i+1].get(dimension, 0.5)
                changes.append(abs(current - previous))

        # Calculate volatility as average change magnitude
        if changes:
            volatility = sum(changes) / len(changes)
            # Scale to appropriate range (0-1)
            scaled_volatility = min(volatility * 2.5, 1.0)
            return scaled_volatility

        return 0.3  # Default with insufficient change data

    def _determine_emotional_trajectory(self, historical_data: List[Dict] = None) -> str:
        """Determine emotional trajectory based on historical data"""
        if not historical_data or len(historical_data) < 2:
            return "neutral"  # Default with insufficient data

        # Extract satisfaction and frustration from recent entries (up to 3)
        recent_entries = sorted(
            historical_data, key=lambda x: x.get('timestamp', 0), reverse=True)[:3]

        # Calculate emotional valence (satisfaction - frustration)
        valences = []
        for entry in recent_entries:
            satisfaction = entry.get('satisfaction_level', 0.5)
            frustration = entry.get('frustration_level', 0.5)
            valences.append(satisfaction - frustration)

        # Determine trajectory based on valence changes
        if len(valences) >= 2:
            latest = valences[0]
            previous_avg = sum(valences[1:]) / len(valences[1:])  # Average of previous entries

            diff = latest - previous_avg
            if diff > 0.15:
                return "improving"
            elif diff < -0.15:
                return "declining"
            elif any(abs(latest - v) > 0.25 for v in valences[1:]):
                return "fluctuating"

        return "neutral"

    def _analyze_hidden_dissatisfaction(
        self, text: str, satisfaction_level: float) -> Tuple[bool, float, List[str]]:
        """Analyze hidden dissatisfaction in text"""
        hidden_signals = []

        # Check for hidden dissatisfaction patterns
        for pattern in self.hidden_dissatisfaction_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                pattern_name = pattern.split(
                    '|')[0].replace('(', '').replace(')', '').replace('r"', '')
                hidden_signals.append(pattern_name)

        # Check for praise with reservations
        if re.search(r"(good|great|nice) but", text.lower()):
            hidden_signals.append("praise_with_reservations")

        if re.search(r"(like|enjoy).*(however|though|but)", text.lower()):
            hidden_signals.append("praise_with_reservations")

        # Check for faint praise
        if re.search(r"(somewhat|kind of|sort of) (good|helpful|useful)", text.lower()):
            hidden_signals.append("faint_praise")

        # Check for diplomatic language
        if re.search(r"(I appreciate|thank you for) (the effort|trying|attempting)", text.lower()):
            hidden_signals.append("diplomatic_language")

        # Determine if hidden dissatisfaction is present
        hidden_dissatisfaction = len(hidden_signals) > 0

        # Calculate confidence based on number and type of signals
        base_confidence = min(len(hidden_signals) * 0.25, 0.75)  # More signals = higher confidence

        # Adjust confidence based on satisfaction level
        # If satisfaction is high but we detected hidden signals, reduce confidence
        if satisfaction_level > 0.7 and hidden_dissatisfaction:
            confidence_adjustment = -0.3
        # If satisfaction is low and we detected hidden signals, increase confidence
        elif satisfaction_level < 0.4 and hidden_dissatisfaction:
            confidence_adjustment = 0.2
        else:
            confidence_adjustment = 0

        hidden_confidence = max(min(base_confidence + confidence_adjustment, 1.0), 0.0)

        return hidden_dissatisfaction, hidden_confidence, hidden_signals

    def _calculate_politeness_mask(self, text: str, hidden_dissatisfaction: bool) -> float:
        """Calculate politeness mask level (how much politeness masks true feelings)"""
        if not hidden_dissatisfaction:
            return 0.0  # No mask if no hidden dissatisfaction

        # Polite phrases that might mask negative feelings
        polite_phrases = [
            "thank you", "thanks for", "appreciate", "grateful",
            "please", "if possible", "if you could", "would be nice",
            "understand that", "I know that", "I realize"
        ]

        # Count polite phrases
        polite_count = sum(1 for phrase in polite_phrases if phrase in text.lower())

        # Calculate base mask level
        mask_level = min(polite_count * 0.2, 0.8)  # Scale up to 0.8 max

        # Check for excessive politeness markers
        if re.search(r"(very|really|truly|so) (grateful|thankful|appreciative)", text.lower()):
            mask_level += 0.1

        if re.search(r"(sorry to|apologize for) (bother|trouble|disturb)", text.lower()):
            mask_level += 0.15

        return min(mask_level, 1.0)  # Ensure final value is at most 1.0

    def _detect_dropout_risk_emotions(self, text: str) -> List[str]:
        """Detect emotions that indicate dropout risk"""
        detected_emotions = []

        # Check for each dropout risk emotion
        for emotion in self.dropout_risk_emotions:
            if emotion in text.lower():
                detected_emotions.append(emotion)

        # Check for specific phrases indicating emotional states
        emotion_phrases = {
            "helplessness": ["can't do this", "beyond me", "impossible for me", "no way I can"],
            "overwhelm": ["too much", "overwhelming", "drowning in", "can't keep up", "too difficult"],
            "isolation": ["all alone", "no one helps", "no support", "by myself", "no one responds"],
            "despair": ["giving up", "no point", "useless to try", "hopeless", "waste of time"],
            "anxiety": ["anxious", "worried", "stressed", "panic", "fear", "dread"]
        }

        for emotion, phrases in emotion_phrases.items():
            if any(
                phrase in text.lower() for phrase in phrases) and emotion not in detected_emotions:
                detected_emotions.append(emotion)

        return detected_emotions

    def _detect_positive_recovery_indicators(self, text: str) -> List[str]:
        """Detect positive emotions that indicate recovery potential"""
        detected_indicators = []

        # Check for each positive recovery indicator
        for indicator in self.positive_recovery_indicators:
            if indicator in text.lower():
                detected_indicators.append(indicator)

        # Check for specific phrases indicating positive states
        positive_phrases = {
            "hope": ["hoping", "look forward to", "optimistic", "better next time"],
            "determination": ["determined", "will try again", "not giving up", "keep working"],
            "gratitude": ["thankful", "appreciate", "grateful", "thanks for"],
            "confidence": ["confident", "I can do this", "getting better at", "improving"],
            "enthusiasm": ["excited", "looking forward", "can't wait", "eager"]
        }

        for indicator, phrases in positive_phrases.items():
            if any(
                phrase in text.lower(
                    ) for phrase in phrases) and indicator not in detected_indicators:
                detected_indicators.append(indicator)

        return detected_indicators

    def _identify_emotional_triggers(self, text: str) -> List[str]:
        """Identify specific triggers for negative emotions"""
        triggers = []

        # Common trigger patterns
        trigger_patterns = {
            "deadline_pressure": [r"deadline", r"due date", r"running out of time", r"not enough time"],
            "technical_issues": [r"(website|system|platform) (doesn't work|isn't working|broken)", r"technical (issue|problem|error)"],
            "content_difficulty": [r"(too|very) (difficult|hard|complex)", r"don't understand", r"confused by"],
            "lack_of_support": [r"no (help|support|response)", r"no one (answers|responds)", r"waiting for (help|response)"],
            "peer_comparison": [r"everyone else (gets it|understands)", r"falling behind", r"only one struggling"],
            "feedback_issues": [r"(no|unclear|unhelpful) feedback", r"don't know (how|what) I'm doing wrong"],
            "workload_issues": [r"too (much|many) (assignments|tasks|work)", r"workload is (overwhelming|too much)"],
            "instructor_issues": [r"instructor (doesn't|isn't) (explain|clear|helpful)", r"teaching style"]
        }

        # Check for each trigger pattern
        for trigger, patterns in trigger_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text.lower()):
                    triggers.append(trigger)
                    break  # Only add each trigger once

        return triggers

    def _calculate_emotion_coherence(
        self, frustration: float, engagement: float, confidence: float, satisfaction: float) -> float:
        """Calculate how coherent/consistent the emotional profile is"""
        # Coherent profiles should show alignment between related emotions
        # e.g., high frustration typically aligns with low satisfaction

        # Expected relationships:
        # 1. Frustration and satisfaction should be inversely related
        # 2. Engagement and confidence often positively correlated

        coherence = 1.0  # Start with perfect coherence

        # Check frustration-satisfaction relationship
        # If both high or both low, reduce coherence
        frustration_satisfaction_coherence = 1.0 - abs((1 - satisfaction) - frustration)

        # Check engagement-confidence relationship
        # If very different, reduce coherence
        engagement_confidence_coherence = 1.0 - abs(engagement - confidence)

        # Combine coherence scores (weighted)
        coherence = (
            frustration_satisfaction_coherence * 0.6) + (engagement_confidence_coherence * 0.4)

        return coherence

    def _calculate_sentiment_authenticity(self, text: str, hidden_dissatisfaction: bool) -> float:
        """Calculate how authentic/genuine the emotional expression appears"""
        # Start with base authenticity
        authenticity = 0.8  # Assume mostly authentic by default

        # Reduce authenticity for hidden dissatisfaction
        if hidden_dissatisfaction:
            authenticity -= 0.3

        # Check for authenticity markers
        authentic_markers = [
            r"honestly", r"to be honest", r"frankly", r"to tell the truth",
            r"I (really|truly) (feel|think|believe)", r"I'm not going to lie"
        ]

        # Increase authenticity for explicit authenticity markers
        for marker in authentic_markers:
            if re.search(marker, text.lower()):
                authenticity += 0.1
                break  # Only apply this bonus once

        # Check for mixed messages that reduce authenticity
        mixed_message_patterns = [
            r"(good|great|excellent).*(but|however|though)",
            r"(like|enjoy).*(but|however|though)",
            r"(not complaining|don't want to complain).*(but|however|though)"
        ]

        for pattern in mixed_message_patterns:
            if re.search(pattern, text.lower()):
                authenticity -= 0.15
                break  # Only apply this penalty once

        return max(min(authenticity, 1.0), 0.0)  # Ensure value is between 0 and 1

    def _determine_emotional_complexity(self, text: str) -> str:
        """Determine the complexity of the emotional expression"""
        # Count distinct emotion words
        emotion_words = [
            "happy", "sad", "angry", "frustrated", "confused", "anxious", "excited",
            "bored", "interested", "confident", "worried", "overwhelmed", "satisfied",
            "disappointed", "hopeful", "discouraged", "grateful", "annoyed", "proud"
        ]

        # Count distinct emotions expressed
        distinct_emotions = set(word for word in emotion_words if word in text.lower())
        emotion_count = len(distinct_emotions)

        # Check for emotional contradictions
        positive_emotions = ["happy", "excited", "interested", "confident", "satisfied", "hopeful", "grateful", "proud"]
        negative_emotions = ["sad", "angry", "frustrated", "confused", "anxious", "bored", "worried", "overwhelmed", "disappointed", "discouraged", "annoyed"]

        has_positive = any(emotion in text.lower() for emotion in positive_emotions)
        has_negative = any(emotion in text.lower() for emotion in negative_emotions)
        has_contradiction = has_positive and has_negative

        # Check for explicit mixed feelings
        mixed_feelings_patterns = [
            r"mixed feelings", r"conflicted", r"torn", r"on one hand.*(on the other)",
            r"part of me.*(another part)", r"both happy and", r"both frustrated and"
        ]

        has_explicit_conflict = any(
            re.search(pattern, text.lower()) for pattern in mixed_feelings_patterns)

        # Determine complexity
        if has_explicit_conflict or (has_contradiction and emotion_count >= 3):
            return "conflicted"
        elif emotion_count >= 4 or (has_contradiction and emotion_count >= 2):
            return "complex"
        elif emotion_count >= 2:
            return "mixed"
        else:
            return "simple"
