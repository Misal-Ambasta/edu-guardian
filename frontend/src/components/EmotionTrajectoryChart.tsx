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
  Filler
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface EmotionTrajectoryChartProps {
  studentId: string;
  predictionWindow?: number; // number of weeks to predict
}

interface TrajectoryData {
  timestamp: string;
  predictedEmotion: number;
  confidenceUpper: number;
  confidenceLower: number;
  actualEmotion?: number;
}

export const EmotionTrajectoryChart: React.FC<EmotionTrajectoryChartProps> = ({ 
  studentId, 
  predictionWindow = 4 
}) => {
  const [trajectoryData, setTrajectoryData] = React.useState<TrajectoryData[]>([]);
  const [isLoading, setIsLoading] = React.useState(false);

  React.useEffect(() => {
    const fetchTrajectoryData = async () => {
      setIsLoading(true);
      try {
        // TODO: Replace with actual API call
        const mockData: TrajectoryData[] = [
          {
            timestamp: '2025-08-01',
            predictedEmotion: 0.7,
            confidenceUpper: 0.8,
            confidenceLower: 0.6,
            actualEmotion: 0.75
          },
          {
            timestamp: '2025-08-08',
            predictedEmotion: 0.65,
            confidenceUpper: 0.75,
            confidenceLower: 0.55,
            actualEmotion: 0.68
          },
          {
            timestamp: '2025-08-15',
            predictedEmotion: 0.62,
            confidenceUpper: 0.72,
            confidenceLower: 0.52
          },
          {
            timestamp: '2025-08-22',
            predictedEmotion: 0.58,
            confidenceUpper: 0.68,
            confidenceLower: 0.48
          }
        ];
        setTrajectoryData(mockData);
      } catch (error) {
        console.error('Failed to fetch trajectory data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTrajectoryData();
  }, [studentId, predictionWindow]);

  const chartData = {
    labels: trajectoryData.map(d => new Date(d.timestamp).toLocaleDateString()),
    datasets: [
      {
        label: 'Predicted Emotion',
        data: trajectoryData.map(d => d.predictedEmotion),
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.4,
        fill: false
      },
      {
        label: 'Actual Emotion',
        data: trajectoryData.map(d => d.actualEmotion),
        borderColor: 'rgb(54, 162, 235)',
        pointBackgroundColor: 'rgb(54, 162, 235)',
        tension: 0.4,
        fill: false
      },
      {
        label: 'Confidence Interval',
        data: trajectoryData.map(d => d.confidenceUpper),
        borderColor: 'rgba(75, 192, 192, 0.2)',
        backgroundColor: 'rgba(75, 192, 192, 0.1)',
        fill: '+1',
        pointRadius: 0
      },
      {
        label: 'Confidence Interval',
        data: trajectoryData.map(d => d.confidenceLower),
        borderColor: 'rgba(75, 192, 192, 0.2)',
        fill: false,
        pointRadius: 0
      }
    ]
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Emotion Trajectory Prediction'
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      }
    },
    scales: {
      y: {
        min: 0,
        max: 1,
        title: {
          display: true,
          text: 'Emotion Level'
        }
      }
    }
  };

  if (isLoading) {
    return <div className="animate-pulse">Loading trajectory data...</div>;
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Emotion Trajectory</h3>
        <div className="flex gap-2">
          {[2, 4, 8].map((weeks) => (
            <button
              key={weeks}
              className={`px-3 py-1 rounded-full text-sm ${
                predictionWindow === weeks
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700'
              }`}
              onClick={() => weeks !== predictionWindow}
            >
              {weeks} Weeks
            </button>
          ))}
        </div>
      </div>
      <div className="h-[300px]">
        <Line options={options} data={chartData} />
      </div>
    </div>
  );
};
