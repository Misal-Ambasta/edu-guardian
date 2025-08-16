import React from 'react';
import { useEmotionStore } from '../store/emotionStore';

interface Intervention {
  id: string;
  date: string;
  type: string;
  description: string;
  status: 'pending' | 'in-progress' | 'completed' | 'failed';
  impact: number;
}

interface InterventionTrackerProps {
  studentId: string;
}

export const InterventionTracker: React.FC<InterventionTrackerProps> = ({ studentId }) => {
  const [interventions, setInterventions] = React.useState<Intervention[]>([]);
  const [isLoading, setIsLoading] = React.useState(false);

  React.useEffect(() => {
    const fetchInterventions = async () => {
      setIsLoading(true);
      try {
        // TODO: Replace with actual API call
        const mockInterventions: Intervention[] = [
          {
            id: '1',
            date: '2025-08-10',
            type: 'Counseling Session',
            description: 'One-on-one session to address rising frustration levels',
            status: 'completed',
            impact: 0.7,
          },
          {
            id: '2',
            date: '2025-08-12',
            type: 'Course Adjustment',
            description: 'Modified course pace based on emotional feedback',
            status: 'in-progress',
            impact: 0.5,
          },
        ];
        setInterventions(mockInterventions);
      } catch (error) {
        console.error('Failed to fetch interventions:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchInterventions();
  }, [studentId]);

  const getStatusColor = (status: Intervention['status']) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in-progress':
        return 'bg-blue-100 text-blue-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getImpactColor = (impact: number) => {
    if (impact >= 0.7) return 'text-green-600';
    if (impact >= 0.4) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (isLoading) {
    return <div className="animate-pulse">Loading interventions...</div>;
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <h3 className="text-lg font-semibold mb-4">Intervention Tracking</h3>
      <div className="space-y-4">
        {interventions.map((intervention) => (
          <div
            key={intervention.id}
            className="border rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex justify-between items-start">
              <div>
                <h4 className="font-medium">{intervention.type}</h4>
                <p className="text-sm text-gray-600">{intervention.description}</p>
                <p className="text-xs text-gray-500 mt-1">
                  Date: {new Date(intervention.date).toLocaleDateString()}
                </p>
              </div>
              <div className="flex flex-col items-end space-y-2">
                <span
                  className={`px-2 py-1 rounded-full text-xs ${getStatusColor(
                    intervention.status
                  )}`}
                >
                  {intervention.status.charAt(0).toUpperCase() + intervention.status.slice(1)}
                </span>
                <span className={`text-sm font-medium ${getImpactColor(intervention.impact)}`}>
                  Impact: {Math.round(intervention.impact * 100)}%
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
