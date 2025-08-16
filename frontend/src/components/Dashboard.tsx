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
    <div className="min-h-full">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="px-3">
          <div className="flex justify-between h-12 items-center">
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
                className="text-xs border border-gray-200 rounded px-2 py-1 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
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
      <div className="flex-1 overflow bg-gray-50 p-3">
        <div className="max-w-[1400px] mx-auto space-y-3">
          {/* Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
            {metrics.map((metric) => (
              <div 
                key={metric.label} 
                className="bg-white rounded-lg shadow-sm p-2.5 border border-gray-200 hover:border-gray-300 transition-colors"
              >
                <div className="flex items-center gap-1.5">
                  <span className="text-base">{metric.icon}</span>
                  <span className="text-xs font-medium text-gray-700">{metric.label}</span>
                </div>
                <div className="flex items-baseline justify-between mt-2">
                  <span className="text-lg font-semibold text-gray-900">{metric.value}</span>
                  <span className={`text-xs font-medium ${
                    metric.change >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {metric.change >= 0 ? '↑' : '↓'}{Math.abs(metric.change)}%
                  </span>
                </div>
                <p className="mt-1 text-xs text-gray-500 truncate">{metric.description}</p>
              </div>
            ))}
          </div>

          {/* Charts Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="bg-white rounded-lg shadow-sm p-3">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-xs font-medium text-gray-900">Emotional Health</h3>
                <button className="text-xs text-gray-400 hover:text-gray-600">•••</button>
              </div>
              <div className="h-32">
                <EmotionalGauge studentId={studentId} />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-3">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-xs font-medium text-gray-900">Temperature</h3>
                <button className="text-xs text-gray-400 hover:text-gray-600">•••</button>
              </div>
              <div className="h-32">
                <EmotionalTemperatureGauge studentId={studentId} />
              </div>
            </div>
          </div>

          {/* History Chart */}
          <div className="bg-white rounded-lg shadow-sm p-3">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-xs font-medium text-gray-900">Historical Patterns</h3>
              <div className="flex items-center space-x-2">
                <button className="text-xs text-gray-400 hover:text-gray-600">
                  <span className="sr-only">View details</span>
                  •••
                </button>
              </div>
            </div>
            <div className="h-36">
              <HistoricalPatternChart studentId={studentId} timeRange={selectedTimeRange} />
            </div>
          </div>

          {/* Predictions Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="md:col-span-2 bg-white rounded-lg shadow-sm p-3">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-xs font-medium text-gray-900">Emotion Trajectory</h3>
                <button className="text-xs text-gray-400 hover:text-gray-600">•••</button>
              </div>
              <div className="h-32">
                <EmotionTrajectoryChart studentId={studentId} />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-3">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-xs font-medium text-gray-900">Recommended Actions</h3>
                <button className="text-xs text-gray-400 hover:text-gray-600">•••</button>
              </div>
              <div className="h-32 overflow-auto">
                <InterventionRecommender studentId={studentId} />
              </div>
            </div>
          </div>

          {/* Crisis Prediction */}
          <div className="bg-white rounded-lg shadow-sm p-3">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-xs font-medium text-gray-900">Crisis Prediction</h3>
              <button className="text-xs text-gray-400 hover:text-gray-600">•••</button>
            </div>
            <div className="h-28">
              <CrisisPredictionAlert studentId={studentId} />
            </div>
          </div>

          {/* Boiling Point Analysis */}
          <div className="bg-white rounded-lg shadow-sm p-3">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-xs font-medium text-gray-900">Emotional Boiling Points</h3>
              <button className="text-xs text-gray-400 hover:text-gray-600">•••</button>
            </div>
            <div className="h-36">
              <EmotionalBoilingPoint studentId={studentId} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
