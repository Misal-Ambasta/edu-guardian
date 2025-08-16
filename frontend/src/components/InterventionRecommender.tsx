import React from 'react';
import { CheckCircleIcon, ClockIcon } from '@heroicons/react/24/solid';

interface Recommendation {
  id: string;
  type: 'immediate' | 'scheduled' | 'monitoring';
  action: string;
  impact: number;
  timeframe: string;
  reasoning: string[];
  status: 'pending' | 'approved' | 'in-progress' | 'completed';
}

interface InterventionRecommenderProps {
  studentId: string;
}

export const InterventionRecommender: React.FC<InterventionRecommenderProps> = ({ studentId }) => {
  const [recommendations, setRecommendations] = React.useState<Recommendation[]>([]);
  const [isLoading, setIsLoading] = React.useState(false);
  const [activeFilter, setActiveFilter] = React.useState<Recommendation['type']>('immediate');

  React.useEffect(() => {
    const fetchRecommendations = async () => {
      setIsLoading(true);
      try {
        // TODO: Replace with actual API call
        const mockRecommendations: Recommendation[] = [
          {
            id: '1',
            type: 'immediate',
            action: 'Schedule emergency counseling session',
            impact: 0.85,
            timeframe: 'Within 24 hours',
            reasoning: [
              'Sharp increase in frustration levels',
              'Multiple missed assignments',
              'Negative sentiment in recent communications'
            ],
            status: 'pending'
          },
          {
            id: '2',
            type: 'scheduled',
            action: 'Adjust course pace and workload',
            impact: 0.75,
            timeframe: 'Next week',
            reasoning: [
              'Consistent pattern of late submissions',
              'Reported difficulty with current pace'
            ],
            status: 'approved'
          },
          {
            id: '3',
            type: 'monitoring',
            action: 'Track engagement with support resources',
            impact: 0.65,
            timeframe: 'Ongoing',
            reasoning: [
              'Limited use of available help resources',
              'Could benefit from proactive support'
            ],
            status: 'in-progress'
          }
        ];
        setRecommendations(mockRecommendations);
      } catch (error) {
        console.error('Failed to fetch recommendations:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchRecommendations();
  }, [studentId]);

  const getTypeColor = (type: Recommendation['type']) => {
    switch (type) {
      case 'immediate':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'scheduled':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'monitoring':
        return 'bg-green-100 text-green-800 border-green-200';
    }
  };

  const getStatusIcon = (status: Recommendation['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'in-progress':
        return <ClockIcon className="h-5 w-5 text-blue-500" />;
      default:
        return null;
    }
  };

  if (isLoading) {
    return <div className="animate-pulse">Loading recommendations...</div>;
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-semibold">Intervention Recommendations</h3>
        <div className="flex gap-2">
          {(['immediate', 'scheduled', 'monitoring'] as const).map((type) => (
            <button
              key={type}
              className={`px-3 py-1 rounded-full text-sm ${
                activeFilter === type
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700'
              }`}
              onClick={() => setActiveFilter(type)}
            >
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        {recommendations
          .filter((rec) => rec.type === activeFilter)
          .map((recommendation) => (
            <div
              key={recommendation.id}
              className={`border rounded-lg p-4 ${getTypeColor(recommendation.type)}`}
            >
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-medium">{recommendation.action}</h4>
                  <p className="text-sm mt-1">
                    Timeline: {recommendation.timeframe} | Impact: {Math.round(recommendation.impact * 100)}%
                  </p>
                </div>
                {getStatusIcon(recommendation.status)}
              </div>

              <div className="mt-4">
                <h5 className="text-sm font-medium mb-2">Reasoning:</h5>
                <ul className="text-sm space-y-1">
                  {recommendation.reasoning.map((reason, idx) => (
                    <li key={idx} className="flex items-center">
                      • {reason}
                    </li>
                  ))}
                </ul>
              </div>

              {recommendation.status === 'pending' && (
                <div className="mt-4 flex gap-2">
                  <button className="px-4 py-2 bg-blue-500 text-white rounded-lg text-sm hover:bg-blue-600">
                    Approve
                  </button>
                  <button className="px-4 py-2 bg-gray-500 text-white rounded-lg text-sm hover:bg-gray-600">
                    Postpone
                  </button>
                </div>
              )}
            </div>
          ))}
      </div>
    </div>
  );
};
