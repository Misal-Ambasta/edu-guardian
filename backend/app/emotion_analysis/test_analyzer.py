from analyzer import AdvancedEmotionAnalyzer, EmotionProfile

def test_emotion_analyzer():
    """Test the AdvancedEmotionAnalyzer with various text inputs"""
    analyzer = AdvancedEmotionAnalyzer()

    # Test case 1: Frustrated student with technical issues
    text1 = \
        "I'm extremely frustrated with the website. It keeps crashing when I try to submit my assignment and I've already tried multiple times. This is urgent as the deadline is tomorrow!"

    profile1 = analyzer.analyze_text(text1)
    print("\nTest Case 1: Frustrated student with technical issues")
    print(f"Frustration Level: {profile1.frustration_level:.2f}")
    print(f"Frustration Type: {profile1.frustration_type}")
    print(f"Urgency Level: {profile1.urgency_level}")
    print(f"Response Urgency: {profile1.response_urgency}")
    print(f"Emotional Temperature: {profile1.emotional_temperature:.2f}")
    print(f"Urgency Signals: {profile1.urgency_signals}")

    # Test case 2: Hidden dissatisfaction
    text2 = \
        "The course is fine I guess. The materials are somewhat helpful, but I'm not really making progress as quickly as I'd like. It's probably just me though. Thanks for checking in."

    profile2 = analyzer.analyze_text(text2)
    print("\nTest Case 2: Hidden dissatisfaction")
    print(f"Satisfaction Level: {profile2.satisfaction_level:.2f}")
    print(f"Hidden Dissatisfaction: {profile2.hidden_dissatisfaction_flag}")
    print(f"Hidden Dissatisfaction Confidence: {profile2.hidden_dissatisfaction_confidence:.2f}")
    print(f"Hidden Signals: {profile2.hidden_signals}")
    print(f"Politeness Mask Level: {profile2.politeness_mask_level:.2f}")

    # Test case 3: Engaged but struggling student
    text3 = \
        "I really love this course and find the material fascinating, but I'm struggling to keep up with the pace. I'm feeling a bit overwhelmed by the workload but I'm determined to succeed. Could you provide some additional resources?"

    profile3 = analyzer.analyze_text(text3)
    print("\nTest Case 3: Engaged but struggling student")
    print(f"Engagement Level: {profile3.engagement_level:.2f}")
    print(f"Confidence Level: {profile3.confidence_level:.2f}")
    print(f"Frustration Level: {profile3.frustration_level:.2f}")
    print(f"Emotional Complexity: {profile3.emotional_complexity}")
    print(f"Dropout Risk Emotions: {profile3.dropout_risk_emotions}")
    print(f"Positive Recovery Indicators: {profile3.positive_recovery_indicators}")

    # Test case 4: At-risk student showing signs of giving up
    text4 = \
        "I don't think I can do this anymore. I'm completely lost and feel like I'm the only one not understanding the material. I've fallen so far behind that it seems hopeless to catch up now. No one responds to my questions."

    profile4 = analyzer.analyze_text(text4)
    print("\nTest Case 4: At-risk student showing signs of giving up")
    print(f"Dropout Risk Emotions: {profile4.dropout_risk_emotions}")
    print(f"Emotional Temperature: {profile4.emotional_temperature:.2f}")
    print(f"Emotional Triggers: {profile4.emotional_triggers}")
    print(f"Frustration Intensity: {profile4.frustration_intensity}")
    print(f"Confidence Level: {profile4.confidence_level:.2f}")

    # Test with aspect scores
    aspect_scores = {"content": 3, "instructor": 2, "platform": 1, "support": 2}
    profile5 = analyzer.analyze_text(text3, aspect_scores=aspect_scores)
    print("\nTest Case 5: With aspect scores")
    print(f"Satisfaction Level: {profile5.satisfaction_level:.2f}")

if __name__ == "__main__":
    test_emotion_analyzer()
