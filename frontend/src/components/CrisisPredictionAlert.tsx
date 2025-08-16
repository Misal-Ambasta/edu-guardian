import React from 'react';
import { ExclamationTriangleIcon, ChevronRightIcon } from '@heroicons/react/24/solid';

interface CrisisRisk {
  id: string;
  studentId: string;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  predictedTimeline: string;
  indicators: string[];
  recommendedActions: string[];
  confidence: number;
}

interface CrisisPredictionAlertProps {
  studentId: string;
}

export const CrisisPredictionAlert: React.FC<CrisisPredictionAlertProps> = ({ studentId }) => {
  const [predictions, setPredictions] = React.useState<CrisisRisk[]>([]);
  const [isLoading, setIsLoading] = React.useState(false);

  React.useEffect(() => {
    const fetchPredictions = async () => {
      setIsLoading(true);
      try {
        // TODO: Replace with actual API call
        const mockPredictions: CrisisRisk[] = [
          {
            id: '1',
            studentId,
            riskLevel: 'high',
            predictedTimeline: '2 weeks',
            indicators: [
              'Declining participation rate',
              'Increasing frustration levels',
              'Missed assignments'
            ],
            recommendedActions: [
              'Schedule immediate counseling session',
              'Review course workload',
              'Initiate peer support program'
            ],
            confidence: 0.85
          },
          {
            id: '2',
            studentId,
            riskLevel: 'medium',
            predictedTimeline: '4 weeks',
            indicators: [
              'Slight drop in engagement',
              'Inconsistent attendance'
            ],
            recommendedActions: [
              'Monitor progress closely',
              'Schedule check-in meeting'
            ],
            confidence: 0.75
          }
        ];
        setPredictions(mockPredictions);
      } catch (error) {
        console.error('Failed to fetch crisis predictions:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPredictions();
  }, [studentId]);

  const getRiskColor = (level: CrisisRisk['riskLevel']) => {
    switch (level) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      default:
        return 'bg-green-100 text-green-800 border-green-300';
    }
  };

  if (isLoading) {
    return <div className="animate-pulse">Loading predictions...</div>;
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <h3 className="text-lg font-semibold mb-4">Crisis Predictions</h3>
      <div className="space-y-4">
        {predictions.map((prediction) => (
          <div
            key={prediction.id}
            className={`border rounded-lg p-4 ${getRiskColor(prediction.riskLevel)}`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center">
                <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
                <div>
                  <h4 className="font-medium">
                    {prediction.riskLevel.charAt(0).toUpperCase() + prediction.riskLevel.slice(1)} Risk
                  </h4>
                  <p className="text-sm">Predicted within {prediction.predictedTimeline}</p>
                </div>
              </div>
              <span className="text-sm font-medium">
                {Math.round(prediction.confidence * 100)}% confidence
              </span>
            </div>

            <div className="mt-4 space-y-3">
              <div>
                <h5 className="text-sm font-medium mb-1">Risk Indicators:</h5>
                <ul className="text-sm space-y-1">
                  {prediction.indicators.map((indicator, idx) => (
                    <li key={idx} className="flex items-center">
                      <ChevronRightIcon className="h-3 w-3 mr-1" />
                      {indicator}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h5 className="text-sm font-medium mb-1">Recommended Actions:</h5>
                <ul className="text-sm space-y-1">
                  {prediction.recommendedActions.map((action, idx) => (
                    <li key={idx} className="flex items-center">
                      <ChevronRightIcon className="h-3 w-3 mr-1" />
                      {action}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
