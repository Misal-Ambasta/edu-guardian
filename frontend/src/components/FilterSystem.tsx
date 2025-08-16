import React from 'react';
import { Fragment } from 'react';
import { Menu, Transition } from '@headlessui/react';
import { ChevronDownIcon, FunnelIcon } from '@heroicons/react/24/outline';

interface Filter {
  id: string;
  name: string;
  options: { value: string; label: string }[];
}

const filters: Filter[] = [
  {
    id: 'emotionLevel',
    name: 'Emotion Level',
    options: [
      { value: 'high', label: 'High' },
      { value: 'medium', label: 'Medium' },
      { value: 'low', label: 'Low' }
    ]
  },
  {
    id: 'riskLevel',
    name: 'Risk Level',
    options: [
      { value: 'critical', label: 'Critical' },
      { value: 'high', label: 'High' },
      { value: 'medium', label: 'Medium' },
      { value: 'low', label: 'Low' }
    ]
  },
  {
    id: 'interventionStatus',
    name: 'Intervention Status',
    options: [
      { value: 'pending', label: 'Pending' },
      { value: 'in-progress', label: 'In Progress' },
      { value: 'completed', label: 'Completed' }
    ]
  }
];

export const FilterSystem: React.FC = () => {
  const [activeFilters, setActiveFilters] = React.useState<Record<string, string[]>>({});

  const handleFilterChange = (filterId: string, value: string) => {
    setActiveFilters(prev => ({
      ...prev,
      [filterId]: prev[filterId]?.includes(value)
        ? prev[filterId].filter(v => v !== value)
        : [...(prev[filterId] || []), value]
    }));
  };

  const clearFilters = () => {
    setActiveFilters({});
  };

  return (
    <div className="relative inline-block text-left">
      <Menu as="div" className="relative inline-block text-left">
        <div>
          <Menu.Button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
            <FunnelIcon className="h-5 w-5 mr-2 text-gray-400" aria-hidden="true" />
            Filters
            <ChevronDownIcon className="ml-2 h-5 w-5" aria-hidden="true" />
          </Menu.Button>
        </div>

        <Transition
          as={Fragment}
          enter="transition ease-out duration-100"
          enterFrom="transform opacity-0 scale-95"
          enterTo="transform opacity-100 scale-100"
          leave="transition ease-in duration-75"
          leaveFrom="transform opacity-100 scale-100"
          leaveTo="transform opacity-0 scale-95"
        >
          <Menu.Items className="origin-top-right absolute right-0 mt-2 w-96 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 divide-y divide-gray-100 focus:outline-none">
            {filters.map((filter) => (
              <div key={filter.id} className="px-4 py-3">
                <h3 className="text-sm font-medium text-gray-900">{filter.name}</h3>
                <div className="mt-2 space-y-2">
                  {filter.options.map((option) => (
                    <label key={option.value} className="flex items-center">
                      <input
                        type="checkbox"
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        checked={activeFilters[filter.id]?.includes(option.value) || false}
                        onChange={() => handleFilterChange(filter.id, option.value)}
                      />
                      <span className="ml-2 text-sm text-gray-700">{option.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            ))}
            <div className="px-4 py-3">
              <button
                type="button"
                onClick={clearFilters}
                className="w-full px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-50 rounded-md"
              >
                Clear all filters
              </button>
            </div>
          </Menu.Items>
        </Transition>
      </Menu>

      {/* Active Filters Display */}
      {Object.keys(activeFilters).length > 0 && (
        <div className="mt-2 flex flex-wrap gap-2">
          {Object.entries(activeFilters).map(([filterId, values]) =>
            values.map((value) => (
              <span
                key={`${filterId}-${value}`}
                className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
              >
                {filters.find(f => f.id === filterId)?.name}: {value}
                <button
                  type="button"
                  onClick={() => handleFilterChange(filterId, value)}
                  className="ml-1 inline-flex items-center p-0.5 text-blue-400 hover:bg-blue-200 hover:text-blue-600 rounded-full"
                >
                  <span className="sr-only">Remove filter</span>
                  ×
                </button>
              </span>
            ))
          )}
        </div>
      )}
    </div>
  );
};
