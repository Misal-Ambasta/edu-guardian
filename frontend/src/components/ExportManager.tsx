import React from 'react';
import { Menu } from '@headlessui/react';
import { DocumentArrowDownIcon, ChevronDownIcon } from '@heroicons/react/24/outline';

interface ExportOption {
  id: string;
  name: string;
  format: 'pdf' | 'excel' | 'csv';
  description: string;
}

const exportOptions: ExportOption[] = [
  {
    id: 'full-report',
    name: 'Full Report',
    format: 'pdf',
    description: 'Complete emotional intelligence report with all metrics'
  },
  {
    id: 'emotion-summary',
    name: 'Emotion Summary',
    format: 'excel',
    description: 'Summary of emotional metrics and trends'
  },
  {
    id: 'intervention-history',
    name: 'Intervention History',
    format: 'csv',
    description: 'Detailed intervention tracking and outcomes'
  }
];

export const ExportManager: React.FC = () => {
  const [isExporting, setIsExporting] = React.useState(false);
  const [exportProgress, setExportProgress] = React.useState(0);

  const handleExport = async (option: ExportOption) => {
    setIsExporting(true);
    setExportProgress(0);

    try {
      // Simulated export progress
      for (let i = 0; i <= 100; i += 10) {
        await new Promise(resolve => setTimeout(resolve, 100));
        setExportProgress(i);
      }

      // TODO: Implement actual export logic here
      console.log(`Exporting ${option.name} in ${option.format} format`);

      // Show success message
      alert(`Successfully exported ${option.name}`);
    } catch (error) {
      console.error('Export failed:', error);
      alert('Export failed. Please try again.');
    } finally {
      setIsExporting(false);
      setExportProgress(0);
    }
  };

  return (
    <div className="relative inline-block text-left">
      <Menu as="div" className="relative inline-block text-left">
        <Menu.Button
          disabled={isExporting}
          className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <DocumentArrowDownIcon className="h-5 w-5 mr-2 text-gray-400" aria-hidden="true" />
          Export
          <ChevronDownIcon className="ml-2 h-5 w-5" aria-hidden="true" />
        </Menu.Button>

        <Menu.Items className="origin-top-right absolute right-0 mt-2 w-80 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 divide-y divide-gray-100 focus:outline-none">
          {exportOptions.map((option) => (
            <Menu.Item key={option.id}>
              {({ active }) => (
                <button
                  onClick={() => handleExport(option)}
                  disabled={isExporting}
                  className={`${
                    active ? 'bg-gray-100' : ''
                  } group flex items-start w-full px-4 py-3 text-left`}
                >
                  <div>
                    <p className="text-sm font-medium text-gray-900">{option.name}</p>
                    <p className="text-sm text-gray-500 mt-1">{option.description}</p>
                    <p className="text-xs text-gray-400 mt-1">Format: {option.format.toUpperCase()}</p>
                  </div>
                </button>
              )}
            </Menu.Item>
          ))}
        </Menu.Items>
      </Menu>

      {/* Export Progress Indicator */}
      {isExporting && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-6 rounded-lg shadow-xl w-96">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Exporting Report</h3>
            <div className="relative pt-1">
              <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-gray-200">
                <div
                  style={{ width: `${exportProgress}%` }}
                  className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-500 transition-all duration-500"
                ></div>
              </div>
              <div className="text-right">
                <span className="text-sm font-semibold inline-block text-blue-600">
                  {exportProgress}%
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
