import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface TemplateMetrics {
  templateId: string;
  name: string;
  successRate: number;
  engagementScore: number;
  emotionalResponse: number;
  usageCount: number;
}

interface TemplatePerformanceChartProps {
  courseId: string;
}

export const TemplatePerformanceChart: React.FC<TemplatePerformanceChartProps> = ({ courseId }) => {
  const [templates, setTemplates] = React.useState<TemplateMetrics[]>([]);
  const [selectedMetric, setSelectedMetric] = React.useState<keyof Omit<TemplateMetrics, 'templateId' | 'name'>>('successRate');

  React.useEffect(() => {
    const fetchTemplatePerformance = async () => {
      try {
        // TODO: Replace with actual API call
        const mockTemplates: TemplateMetrics[] = [
          {
            templateId: '1',
            name: 'Stress Management',
            successRate: 0.85,
            engagementScore: 0.92,
            emotionalResponse: 0.78,
            usageCount: 150
          },
          {
            templateId: '2',
            name: 'Progress Review',
            successRate: 0.75,
            engagementScore: 0.88,
            emotionalResponse: 0.82,
            usageCount: 200
          },
          {
            templateId: '3',
            name: 'Motivation Boost',
            successRate: 0.92,
            engagementScore: 0.95,
            emotionalResponse: 0.90,
            usageCount: 175
          }
        ];
        setTemplates(mockTemplates);
      } catch (error) {
        console.error('Failed to fetch template performance:', error);
      }
    };

    fetchTemplatePerformance();
  }, [courseId]);

  const chartData = {
    labels: templates.map(t => t.name),
    datasets: [
      {
        label: selectedMetric.split(/(?=[A-Z])/).join(' '),
        data: templates.map(t => t[selectedMetric] * 100),
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
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
        text: 'Template Performance Analysis',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        title: {
          display: true,
          text: selectedMetric === 'usageCount' ? 'Count' : 'Percentage (%)'
        }
      }
    }
  };

  const metrics = [
    { key: 'successRate', label: 'Success Rate' },
    { key: 'engagementScore', label: 'Engagement Score' },
    { key: 'emotionalResponse', label: 'Emotional Response' },
    { key: 'usageCount', label: 'Usage Count' },
  ];

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-semibold">Template Performance</h3>
        <div className="flex gap-2">
          {metrics.map(({ key, label }) => (
            <button
              key={key}
              className={`px-3 py-1 rounded-full text-sm ${
                selectedMetric === key
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700'
              }`}
              onClick={() => setSelectedMetric(key as typeof selectedMetric)}
            >
              {label}
            </button>
          ))}
        </div>
      </div>
      <div className="h-[300px]">
        <Bar options={options} data={chartData} />
      </div>
    </div>
  );
};
