import React from 'react';
import { useEmotionStore } from '../store/emotionStore';
import type { EmotionProfile } from '../types/emotion';

interface EmotionalGaugeProps {
  studentId: string;
}

export const EmotionalGauge: React.FC<EmotionalGaugeProps> = ({ studentId }) => {
  const { currentStudentEmotion, isLoading, error, fetchStudentEmotions } = useEmotionStore();

  React.useEffect(() => {
    fetchStudentEmotions(studentId);
  }, [studentId, fetchStudentEmotions]);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!currentStudentEmotion) return <div>No emotion data available</div>;

  const { emotionProfile } = currentStudentEmotion;

  return (
    <div className="emotional-gauge">
      <h3>Emotional Status</h3>
      <div className="gauge-metrics">
        <div className="metric">
          <label>Complexity:</label>
          <span>{emotionProfile.emotionalComplexity}</span>
        </div>
        <div className="metric">
          <label>Frustration Level:</label>
          <div 
            className="gauge-bar"
            style={{
              width: '100%',
              height: '20px',
              backgroundColor: '#e0e0e0',
            }}
          >
            <div
              style={{
                width: `${emotionProfile.frustrationLevel * 100}%`,
                height: '100%',
                backgroundColor: emotionProfile.frustrationLevel > 0.7 ? 'red' : 
                                emotionProfile.frustrationLevel > 0.4 ? 'yellow' : 'green',
                transition: 'width 0.5s ease-in-out',
              }}
            />
          </div>
        </div>
        {emotionProfile.hiddenDissatisfaction.flag && (
          <div className="alert">
            Hidden Dissatisfaction Detected!
            <br />
            Confidence: {(emotionProfile.hiddenDissatisfaction.confidence * 100).toFixed(1)}%
          </div>
        )}
      </div>
    </div>
  );
};
