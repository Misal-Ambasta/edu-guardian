import React from 'react';
import { 
  ChartBarIcon, 
  ArrowTrendingUpIcon, 
  ArrowTrendingDownIcon 
} from '@heroicons/react/24/solid';
import { useEmotionStore } from '../store/emotionStore';

interface WeeklyReportHeaderProps {
  courseId: string;
  weekNumber: number;
}

export const WeeklyReportHeader: React.FC<WeeklyReportHeaderProps> = ({ 
  courseId, 
  weekNumber 
}) => {
  const { weeklyReport, fetchWeeklyReport, isLoading } = useEmotionStore();

  React.useEffect(() => {
    fetchWeeklyReport(courseId, weekNumber);
  }, [courseId, weekNumber, fetchWeeklyReport]);

  if (isLoading || !weeklyReport) {
    return (
      <div className="card animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-3/4 mb-4"></div>
        <div className="h-4 bg-gray-200 rounded w-1/2"></div>
      </div>
    );
  }

  const getTrendIcon = () => {
    switch (weeklyReport.trend) {
      case 'increasing':
        return <ArrowTrendingUpIcon className="h-6 w-6 text-green-500" />;
      case 'decreasing':
        return <ArrowTrendingDownIcon className="h-6 w-6 text-red-500" />;
      default:
        return null;
    }
  };

  const getRiskBadgeColor = () => {
    switch (weeklyReport.riskLevel) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <ChartBarIcon className="h-8 w-8 text-primary-600" />
          Weekly Report - {weeklyReport.courseName}
        </h2>
        <span className="text-sm text-gray-500">
          Week {weeklyReport.weekNumber} | {weeklyReport.reportDate}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="stat-card bg-white p-4 rounded-lg shadow">
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold">{weeklyReport.npsScore}</span>
            {getTrendIcon()}
          </div>
          <span className="text-sm text-gray-600">NPS Score</span>
        </div>

        <div className="stat-card bg-white p-4 rounded-lg shadow">
          <div className="flex items-center gap-2">
            <span className={`px-2 py-1 rounded text-sm ${getRiskBadgeColor()}`}>
              {weeklyReport.riskLevel.toUpperCase()}
            </span>
          </div>
          <span className="text-sm text-gray-600">Risk Level</span>
        </div>

        <div className="stat-card bg-white p-4 rounded-lg shadow">
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold">
              {weeklyReport.criticalCount}
            </span>
          </div>
          <span className="text-sm text-gray-600">Critical Cases</span>
        </div>
      </div>
    </div>
  );
};
