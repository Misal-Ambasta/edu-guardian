import React from 'react';
import { useEmotionStore } from '../store/emotionStore';

interface TimelineEvent {
  id: string;
  date: string;
  emotionLevel: number;
  event: string;
  impact: 'positive' | 'negative' | 'neutral';
  details: string;
}

interface EmotionalJourneyTimelineProps {
  studentId: string;
}

export const EmotionalJourneyTimeline: React.FC<EmotionalJourneyTimelineProps> = ({ studentId }) => {
  const [events, setEvents] = React.useState<TimelineEvent[]>([]);
  const [isLoading, setIsLoading] = React.useState(false);

  React.useEffect(() => {
    const fetchTimelineEvents = async () => {
      setIsLoading(true);
      try {
        // TODO: Replace with actual API call
        const mockEvents: TimelineEvent[] = [
          {
            id: '1',
            date: '2025-08-01',
            emotionLevel: 0.8,
            event: 'Course Started',
            impact: 'positive',
            details: 'High enthusiasm and engagement in first week'
          },
          {
            id: '2',
            date: '2025-08-05',
            emotionLevel: 0.4,
            event: 'Assignment Deadline',
            impact: 'negative',
            details: 'Showed signs of stress during project submission'
          },
          {
            id: '3',
            date: '2025-08-10',
            emotionLevel: 0.7,
            event: 'Intervention Session',
            impact: 'positive',
            details: 'Positive response to mentoring session'
          }
        ];
        setEvents(mockEvents);
      } catch (error) {
        console.error('Failed to fetch timeline events:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTimelineEvents();
  }, [studentId]);

  const getImpactColor = (impact: TimelineEvent['impact']) => {
    switch (impact) {
      case 'positive':
        return 'bg-green-500';
      case 'negative':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  if (isLoading) {
    return <div className="animate-pulse">Loading emotional journey...</div>;
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <h3 className="text-lg font-semibold mb-6">Emotional Journey Timeline</h3>
      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200"></div>

        {/* Timeline events */}
        <div className="space-y-8">
          {events.map((event) => (
            <div key={event.id} className="relative pl-12">
              {/* Event dot */}
              <div
                className={`absolute left-3 w-3 h-3 rounded-full ${getImpactColor(
                  event.impact
                )} -translate-x-1.5`}
              ></div>

              {/* Event content */}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-medium">{event.event}</h4>
                  <span className="text-sm text-gray-500">
                    {new Date(event.date).toLocaleDateString()}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-2">{event.details}</p>
                <div className="flex items-center">
                  <span className="text-sm font-medium mr-2">Emotion Level:</span>
                  <div className="flex-1 h-2 bg-gray-200 rounded">
                    <div
                      className="h-full rounded bg-blue-500"
                      style={{ width: `${event.emotionLevel * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
