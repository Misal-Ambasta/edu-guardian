import React from 'react';
import { EmotionalGauge } from './EmotionalGauge';
import { EmotionalTemperatureGauge } from './EmotionalTemperatureGauge';
import { HistoricalPatternChart } from './HistoricalPatternChart';
import { EmotionTrajectoryChart } from './EmotionTrajectoryChart';
import { CrisisPredictionAlert } from './CrisisPredictionAlert';
import { InterventionRecommender } from './InterventionRecommender';
import { EmotionalBoilingPoint } from './EmotionalBoilingPoint';
import { useEmotionStore } from '../store/emotionStore';

export const Dashboard: React.FC = () => {
  const { isLoading, error } = useEmotionStore();
  const [activeTab, setActiveTab] = React.useState<'overview' | 'student-journeys' | 'interventions' | 'reports'>('overview');
  const [selectedTimeRange, setSelectedTimeRange] = React.useState<'week' | 'month' | 'semester'>('week');
  const studentId = 'student_123';

  const metrics = [
    { 
      label: 'Emotional Health',
      value: '6.8',
      change: -7,
      icon: '🧠',
      description: 'Overall emotional wellbeing score'
    },
    { 
      label: 'Hidden Issues',
      value: '17%',
      change: 5,
      icon: '🎭',
      description: '12 students showing concerns'
    },
    { 
      label: 'Crisis Risk',
      value: '5',
      change: 2,
      icon: '⚠️',
      description: 'Students needing intervention'
    },
    { 
      label: 'Frustration',
      value: '6.2',
      change: 13,
      icon: '💢',
      description: 'Average frustration score'
    },
    { 
      label: 'Response Time',
      value: '78%',
      change: -12,
      icon: '⏱️',
      description: 'Intervention performance'
    }
  ];

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-screen items-center justify-center text-red-500">
        Error loading dashboard data
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-14 items-center">
            <div className="flex space-x-4">
              {(['overview', 'student-journeys', 'interventions', 'reports'] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    activeTab === tab
                      ? 'bg-indigo-50 text-indigo-700'
                      : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  {tab.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                </button>
              ))}
            </div>
            <div className="flex items-center space-x-3">
              <select 
                value={selectedTimeRange}
                onChange={(e) => setSelectedTimeRange(e.target.value as 'week' | 'month' | 'semester')}
                className="text-sm border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              >
                <option value="week">This Week</option>
                <option value="month">This Month</option>
                <option value="semester">This Semester</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto bg-gray-50 p-4">
        <div className="max-w-7xl mx-auto space-y-4">
          {/* Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {metrics.map((metric) => (
              <div 
                key={metric.label} 
                className="bg-white rounded-lg shadow-sm p-3 border border-gray-200"
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-lg">{metric.icon}</span>
                  <span className="text-sm font-medium text-gray-900">{metric.label}</span>
                </div>
                <div className="flex items-baseline justify-between mt-1">
                  <span className="text-xl font-semibold text-gray-900">{metric.value}</span>
                  <span className={`text-sm font-medium ${
                    metric.change >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {metric.change >= 0 ? '↑' : '↓'}{Math.abs(metric.change)}%
                  </span>
                </div>
                <p className="mt-1 text-xs text-gray-500 line-clamp-2">{metric.description}</p>
              </div>
            ))}
          </div>

          {/* Charts Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white rounded-lg shadow-sm p-4">
              <h3 className="text-sm font-medium text-gray-900 mb-3">Emotional Health</h3>
              <div className="h-48">
                <EmotionalGauge studentId={studentId} />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-4">
              <h3 className="text-sm font-medium text-gray-900 mb-3">Temperature</h3>
              <div className="h-48">
                <EmotionalTemperatureGauge studentId={studentId} />
              </div>
            </div>
          </div>

          {/* History Chart */}
          <div className="bg-white rounded-lg shadow-sm p-4">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Historical Patterns</h3>
            <div className="h-64">
              <HistoricalPatternChart studentId={studentId} timeRange={selectedTimeRange} />
            </div>
          </div>

          {/* Predictions Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2 bg-white rounded-lg shadow-sm p-4">
              <h3 className="text-sm font-medium text-gray-900 mb-3">Emotion Trajectory</h3>
              <div className="h-48">
                <EmotionTrajectoryChart studentId={studentId} />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-4">
              <h3 className="text-sm font-medium text-gray-900 mb-3">Recommended Actions</h3>
              <div className="h-48 overflow-auto">
                <InterventionRecommender studentId={studentId} />
              </div>
            </div>
          </div>

          {/* Crisis Prediction */}
          <div className="bg-white rounded-lg shadow-sm p-4">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Crisis Prediction</h3>
            <div className="h-40">
              <CrisisPredictionAlert studentId={studentId} />
            </div>
          </div>

          {/* Boiling Point Analysis */}
          <div className="bg-white rounded-lg shadow-sm p-4">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Emotional Boiling Points</h3>
            <div className="h-40">
              <EmotionalBoilingPoint studentId={studentId} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
