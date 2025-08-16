import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  type ChartData
} from 'chart.js';
import { useEmotionStore } from '../store/emotionStore';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface FrustrationChartProps {
  studentId: string;
  weekCount?: number;
}

export const FrustrationChart: React.FC<FrustrationChartProps> = ({ 
  studentId, 
  weekCount = 8 
}) => {
  const { emotionalTrends, fetchEmotionalTrends, isLoading } = useEmotionStore();

  React.useEffect(() => {
    fetchEmotionalTrends(studentId);
  }, [studentId, fetchEmotionalTrends]);

  if (isLoading) return <div className="card animate-pulse">Loading chart data...</div>;

  const data: ChartData<'line'> = {
    labels: emotionalTrends.map(trend => `Week ${trend.weekNumber}`).slice(-weekCount),
    datasets: [
      {
        label: 'Average Frustration Level',
        data: emotionalTrends.map(trend => trend.frustrationLevel).slice(-weekCount),
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.5)',
        tension: 0.4,
      },
      {
        label: 'Hidden Dissatisfaction Rate',
        data: emotionalTrends.map(trend => trend.hiddenDissatisfactionRate).slice(-weekCount),
        borderColor: 'rgb(251, 191, 36)',
        backgroundColor: 'rgba(251, 191, 36, 0.5)',
        tension: 0.4,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Emotional Trends Over Time',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 1,
      },
    },
  };

  return (
    <div className="card">
      <Line data={data} options={options} />
    </div>
  );
};
