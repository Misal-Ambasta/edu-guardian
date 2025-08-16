import React from 'react';

interface Threshold {
  metricName: string;
  currentValue: number;
  threshold: number;
  trend: 'increasing' | 'decreasing' | 'stable';
  timeToThreshold?: string;
}

interface EmotionalBoilingPointProps {
  studentId: string;
}

export const EmotionalBoilingPoint: React.FC<EmotionalBoilingPointProps> = ({ studentId }) => {
  const [thresholds, setThresholds] = React.useState<Threshold[]>([]);
  const [isLoading, setIsLoading] = React.useState(false);

  React.useEffect(() => {
    const fetchThresholds = async () => {
      setIsLoading(true);
      try {
        // TODO: Replace with actual API call
        const mockThresholds: Threshold[] = [
          {
            metricName: 'Frustration Level',
            currentValue: 0.75,
            threshold: 0.85,
            trend: 'increasing',
            timeToThreshold: '2 days'
          },
          {
            metricName: 'Emotional Temperature',
            currentValue: 0.68,
            threshold: 0.80,
            trend: 'increasing',
            timeToThreshold: '5 days'
          },
          {
            metricName: 'Stress Index',
            currentValue: 0.82,
            threshold: 0.90,
            trend: 'stable'
          }
        ];
        setThresholds(mockThresholds);
      } catch (error) {
        console.error('Failed to fetch thresholds:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchThresholds();
  }, [studentId]);

  const getTrendIcon = (trend: Threshold['trend']) => {
    switch (trend) {
      case 'increasing':
        return '↗️';
      case 'decreasing':
        return '↘️';
      default:
        return '→';
    }
  };

  const getProgressColor = (current: number, threshold: number) => {
    const ratio = current / threshold;
    if (ratio >= 0.9) return 'bg-red-500';
    if (ratio >= 0.75) return 'bg-orange-500';
    if (ratio >= 0.5) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  if (isLoading) {
    return <div className="animate-pulse">Loading thresholds...</div>;
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <h3 className="text-lg font-semibold mb-4">Emotional Boiling Points</h3>
      <div className="space-y-6">
        {thresholds.map((item, index) => (
          <div key={index} className="space-y-2">
            <div className="flex justify-between items-center">
              <div>
                <span className="font-medium">{item.metricName}</span>
                <span className="ml-2 text-gray-500">{getTrendIcon(item.trend)}</span>
              </div>
              <div className="text-sm text-gray-600">
                {item.timeToThreshold && (
                  <span className="text-orange-600 font-medium">
                    Critical in {item.timeToThreshold}
                  </span>
                )}
              </div>
            </div>
            
            <div className="relative pt-1">
              <div className="flex mb-2 items-center justify-between">
                <div>
                  <span className="text-xs font-semibold inline-block text-gray-600">
                    {Math.round(item.currentValue * 100)}%
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-xs font-semibold inline-block text-gray-600">
                    Threshold: {Math.round(item.threshold * 100)}%
                  </span>
                </div>
              </div>
              <div className="overflow-hidden h-2 text-xs flex rounded bg-gray-200">
                <div
                  style={{ width: `${(item.currentValue / item.threshold) * 100}%` }}
                  className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center ${getProgressColor(
                    item.currentValue,
                    item.threshold
                  )}`}
                ></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
