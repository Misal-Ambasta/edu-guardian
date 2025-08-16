import React, { useState } from 'react';
import {
  HomeIcon,
  ChartBarIcon,
  UserGroupIcon,
  DocumentTextIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline';

const navigation = [
  { 
    name: 'Overview', 
    href: '#', 
    icon: HomeIcon
  },
  { 
    name: 'Analytics', 
    href: '#', 
    icon: ChartBarIcon
  },
  { 
    name: 'Students', 
    href: '#', 
    icon: UserGroupIcon
  },
  { 
    name: 'Reports', 
    href: '#', 
    icon: DocumentTextIcon
  },
  { 
    name: 'Settings', 
    href: '#', 
    icon: Cog6ToothIcon
  }
];

export const Sidebar = () => {
  const [activeItem, setActiveItem] = useState('Overview');

  return (
    <nav className="fixed inset-y-0 left-0 w-16 bg-white shadow-lg flex flex-col items-center py-6 space-y-8"
      {/* Mobile Sidebar */}
      <Transition.Root show={sidebarOpen} as={React.Fragment}>
        <Dialog
          as="div"
          className="fixed inset-0 flex z-40 md:hidden"
          onClose={setSidebarOpen}
        >
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75" />
          <Dialog.Panel className="relative flex-1 flex flex-col max-w-xs w-full bg-white dark:bg-gray-800">
            <div className="absolute top-0 right-0 -mr-12 pt-2">
              <button
                type="button"
                className="ml-1 flex items-center justify-center h-10 w-10 rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500"
                onClick={() => setSidebarOpen(false)}
              >
                <XMarkIcon className="h-6 w-6 text-gray-600" aria-hidden="true" />
              </button>
            </div>
            <div className="flex-1 h-0 pt-5 pb-4 overflow-y-auto">
              <div className="flex-shrink-0 flex items-center px-4 mb-8">
                <img
                  className="h-10 w-auto"
                  src="/logo.svg"
                  alt="Edu Guardian"
                />
              </div>
              <nav className="mt-5 px-4 space-y-2">
                {navigation.map((item) => (
                  <a
                    key={item.name}
                    href={item.href}
                    className="group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg text-gray-700 hover:bg-gray-100 hover:text-indigo-600 transition-all duration-200"
                  >
                    <item.icon
                      className="mr-3 h-5 w-5 text-gray-400 group-hover:text-indigo-500"
                      aria-hidden="true"
                    />
                    <div>
                      <div className="text-sm font-semibold">{item.name}</div>
                      <div className="text-xs text-gray-500 group-hover:text-indigo-400">{item.description}</div>
                    </div>
                  </a>
                ))}
              </nav>
            </div>
            <div className="flex-shrink-0 flex border-t border-indigo-800 p-4">
              <div className="flex items-center">
                <div>
                  <img
                    className="inline-block h-10 w-10 rounded-full"
                    src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80"
                    alt=""
                  />
                </div>
                <div className="ml-3">
                  <p className="text-base font-medium text-white">Admin User</p>
                  <p className="text-sm font-medium text-indigo-200">View profile</p>
                </div>
              </div>
            </div>
          </Dialog.Panel>
        </Dialog>
      </Transition.Root>

      {/* Desktop Sidebar */}
      <div className="hidden md:flex md:w-56 md:flex-col md:fixed md:inset-y-0">
        <div className="flex-1 flex flex-col min-h-0 bg-white border-r border-gray-200">
          <div className="flex-1 flex flex-col pt-4 pb-2 overflow-y-auto">
            <div className="flex items-center flex-shrink-0 px-4 mb-4">
              <img
                className="h-8 w-auto"
                src="/logo.svg"
                alt="Edu Guardian"
              />
            </div>
            <nav className="flex-1 px-3 space-y-1">
              {navigation.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  className="group flex items-center px-2 py-2 text-xs font-medium rounded-md text-gray-700 hover:bg-gray-50 hover:text-indigo-600 transition-colors"
                >
                  <item.icon
                    className="mr-2 h-4 w-4 text-gray-400 group-hover:text-indigo-500"
                    aria-hidden="true"
                  />
                  <div className="truncate">
                    <div className="text-xs font-medium">{item.name}</div>
                  </div>
                </a>
              ))}
            </nav>
          </div>
          <div className="flex-shrink-0 flex border-t border-gray-200 p-4">
            <div className="flex items-center w-full">
              <div className="flex-shrink-0">
                <img
                  className="h-8 w-8 rounded-full object-cover"
                  src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80"
                  alt=""
                />
              </div>
              <div className="ml-2 flex-1 min-w-0">
                <p className="text-xs font-medium text-gray-900 truncate">Admin User</p>
                <p className="text-[10px] text-gray-500">View profile</p>
              </div>
              <button className="ml-auto flex-shrink-0 text-gray-400 hover:text-gray-500">
                <Cog6ToothIcon className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile menu button */}
      <div className="sticky top-0 z-10 md:hidden pl-1 pt-1 sm:pl-3 sm:pt-3 bg-gray-100">
        <button
          type="button"
          className="-ml-0.5 -mt-0.5 h-12 w-12 inline-flex items-center justify-center rounded-md text-gray-500 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500"
          onClick={() => setSidebarOpen(true)}
        >
          <span className="sr-only">Open sidebar</span>
          <Bars3Icon className="h-6 w-6" aria-hidden="true" />
        </button>
      </div>
    </>
  );
};
