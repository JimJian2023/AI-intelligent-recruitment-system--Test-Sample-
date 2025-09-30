import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Bars3Icon,
  XMarkIcon,
  DocumentTextIcon,
  ChartBarIcon,
  CloudArrowUpIcon,
} from '@heroicons/react/24/outline';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  // Demo mode navigation menu
  const navigationItems = [
    { name: 'Resume Upload', href: '/resume-upload', icon: DocumentTextIcon },
    { name: 'Job Description Upload', href: '/job-upload', icon: CloudArrowUpIcon },
    { name: 'Matching Analysis', href: '/matching', icon: ChartBarIcon },
  ];
  const isActivePath = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Logo area */}
          <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
            <Link to="/dashboard" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">AI</span>
              </div>
              <span className="text-xl font-bold text-gray-900">Smart Recruitment</span>
            </Link>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-1 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          {/* User info */}
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <span className="text-white font-medium text-sm">Demo</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  Demo User
                </p>
                <p className="text-xs text-gray-500 truncate">
                  Demo Mode
                </p>
              </div>
            </div>
          </div>

          {/* Navigation menu */}
          <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
            {navigationItems.map((item) => {
              const isActive = isActivePath(item.href);
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-200 ${
                    isActive
                      ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
                      : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                  }`}
                  onClick={() => setSidebarOpen(false)}
                >
                  <item.icon
                    className={`mr-3 h-5 w-5 flex-shrink-0 ${
                      isActive ? 'text-white' : 'text-gray-400 group-hover:text-gray-500'
                    }`}
                  />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          {/* Footer info */}
          <div className="px-4 py-4 border-t border-gray-200">
            <div className="text-center text-xs text-gray-500">
              AI Smart Recruitment Demo System
            </div>
          </div>
        </div>
      </div>

      {/* Main content area */}
      <div className="lg:pl-64">
        {/* Top navigation bar */}
        <div className="sticky top-0 z-30 bg-white shadow-sm border-b border-gray-200">
          <div className="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
            >
              <Bars3Icon className="h-6 w-6" />
            </button>

            <div className="flex-1 lg:flex lg:items-center lg:justify-between">
              <div className="flex-1 min-w-0">
                <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate">
                  {getPageTitle(location.pathname)}
                </h1>
              </div>


            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="flex-1">
          <div className="py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              {children}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

// Get page title based on path
const getPageTitle = (pathname: string): string => {
  const titleMap: { [key: string]: string } = {
    '/dashboard': 'Dashboard',
    '/jobs': 'Job List',
    '/resume-upload': 'Resume Upload',
    '/job-upload': 'Job Description Upload',
    '/matching': 'Matching Analysis',
  };

  // Exact match
  if (titleMap[pathname]) {
    return titleMap[pathname];
  }

  // Fuzzy match
  for (const [path, title] of Object.entries(titleMap)) {
    if (pathname.startsWith(path + '/')) {
      return title;
    }
  }

  return 'AI Smart Recruitment Demo System';
};

export default Layout;