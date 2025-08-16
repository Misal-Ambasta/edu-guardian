import React from 'react';
import { ExclamationTriangleIcon } from '@heroicons/react/24/solid';
import { useEmotionStore } from '../store/emotionStore';

interface HiddenDissatisfactionAlertProps {
  studentId: string;
}

export const HiddenDissatisfactionAlert: React.FC<HiddenDissatisfactionAlertProps> = ({ 
  studentId 
}) => {
  const { currentStudentEmotion } = useEmotionStore();

  if (!currentStudentEmotion?.emotionProfile.hiddenDissatisfaction.flag) {
    return null;
  }

  const confidence = currentStudentEmotion.emotionProfile.hiddenDissatisfaction.confidence;
  const severity = confidence > 0.8 ? 'high' : confidence > 0.5 ? 'medium' : 'low';

  return (
    <div className={`alert-box alert-${severity === 'high' ? 'danger' : 'warning'}`}>
      <ExclamationTriangleIcon className="h-6 w-6 text-yellow-500" />
      <div>
        <h4 className="font-semibold">Hidden Dissatisfaction Detected</h4>
        <p className="text-sm mt-1">
          Our analysis indicates potential hidden dissatisfaction 
          (Confidence: {(confidence * 100).toFixed(1)}%)
        </p>
        {severity === 'high' && (
          <div className="mt-2">
            <button className="btn-primary text-sm">
              Schedule Intervention
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
