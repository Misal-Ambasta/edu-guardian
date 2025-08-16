import React from 'react';
import { useEmotionStore } from '../store/emotionStore';

interface EmotionalTemperatureGaugeProps {
  studentId: string;
}

export const EmotionalTemperatureGauge: React.FC<EmotionalTemperatureGaugeProps> = ({ studentId }) => {
  const { currentStudentEmotion } = useEmotionStore();

  if (!currentStudentEmotion) return null;

  const { emotionProfile } = currentStudentEmotion;
  const temperature = emotionProfile.emotionalTemperature;

  // Calculate color based on temperature
  const getTemperatureColor = (temp: number): string => {
    if (temp < 0.3) return 'bg-blue-500';
    if (temp < 0.5) return 'bg-green-500';
    if (temp < 0.7) return 'bg-yellow-500';
    if (temp < 0.9) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getTemperatureLabel = (temp: number): string => {
    if (temp < 0.3) return 'Cool';
    if (temp < 0.5) return 'Stable';
    if (temp < 0.7) return 'Warm';
    if (temp < 0.9) return 'Hot';
    return 'Critical';
  };

  return (
    <div className="emotional-temperature-gauge">
      <h3 className="text-lg font-semibold mb-4">Emotional Temperature</h3>
      
      {/* Circular Gauge */}
      <div className="relative w-48 h-48 mx-auto">
        <div className="absolute inset-0 rounded-full border-4 border-gray-200">
          <div 
            className={`absolute inset-0 rounded-full ${getTemperatureColor(temperature)} transition-all duration-500`}
            style={{
              clipPath: `polygon(50% 50%, -50% -50%, ${Math.cos(temperature * Math.PI * 2) * 100}% ${Math.sin(temperature * Math.PI * 2) * 100}%)`
            }}
          />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <span className="text-2xl font-bold">{Math.round(temperature * 100)}°</span>
              <p className="text-sm text-gray-600">{getTemperatureLabel(temperature)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Temperature Scale */}
      <div className="mt-4 flex justify-between text-sm text-gray-600">
        <span>Cool</span>
        <span>Stable</span>
        <span>Warm</span>
        <span>Hot</span>
        <span>Critical</span>
      </div>
    </div>
  );
};
