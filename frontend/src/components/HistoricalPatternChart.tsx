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

interface HistoricalPatternChartProps {
  studentId: string;
  timeRange?: 'week' | 'month' | 'semester';
}

export const HistoricalPatternChart: React.FC<HistoricalPatternChartProps> = ({ 
  studentId, 
  timeRange = 'month' 
}) => {
  const [historicalData, setHistoricalData] = React.useState<ChartData<'line'>>({
    labels: [],
    datasets: []
  });

  React.useEffect(() => {
    const fetchHistoricalData = async () => {
      // TODO: Replace with actual API call
      const mockData = {
        labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
        datasets: [
          {
            label: 'Emotional Complexity',
            data: [0.3, 0.5, 0.4, 0.6],
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.4
          },
          {
            label: 'Frustration Level',
            data: [0.2, 0.4, 0.3, 0.5],
            borderColor: 'rgb(255, 99, 132)',
            tension: 0.4
          }
        ]
      };
      setHistoricalData(mockData);
    };

    fetchHistoricalData();
  }, [studentId, timeRange]);

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Historical Emotion Patterns',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 1,
        title: {
          display: true,
          text: 'Intensity'
        }
      }
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Historical Patterns</h3>
        <div className="flex gap-2">
          {['week', 'month', 'semester'].map((range) => (
            <button
              key={range}
              className={`px-3 py-1 rounded-full text-sm ${
                timeRange === range
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700'
              }`}
              onClick={() => timeRange !== range}
            >
              {range.charAt(0).toUpperCase() + range.slice(1)}
            </button>
          ))}
        </div>
      </div>
      <div className="h-[300px]">
        <Line options={options} data={historicalData} />
      </div>
    </div>
  );
};
