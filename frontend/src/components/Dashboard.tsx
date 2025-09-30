import React from 'react';
import { 
  ChartBarIcon, 
  BriefcaseIcon, 
  DocumentTextIcon, 
  UserGroupIcon 
} from '@heroicons/react/24/outline';

const Dashboard: React.FC = () => {
  const stats = [
    {
      name: 'Total Jobs',
      value: '12',
      icon: BriefcaseIcon,
      color: 'bg-blue-500',
    },
    {
      name: 'Resume Count',
      value: '8',
      icon: DocumentTextIcon,
      color: 'bg-green-500',
    },
    {
      name: 'Matching Analysis',
      value: '24',
      icon: ChartBarIcon,
      color: 'bg-purple-500',
    },
    {
      name: 'Active Users',
      value: '156',
      icon: UserGroupIcon,
      color: 'bg-orange-500',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page title */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-600">
          Welcome to AI Smart Recruitment System Demo
        </p>
      </div>

      {/* Statistics cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div
            key={stat.name}
            className="relative overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:px-6 sm:py-6"
          >
            <dt>
              <div className={`absolute rounded-md ${stat.color} p-3`}>
                <stat.icon className="h-6 w-6 text-white" aria-hidden="true" />
              </div>
              <p className="ml-16 truncate text-sm font-medium text-gray-500">
                {stat.name}
              </p>
            </dt>
            <dd className="ml-16 flex items-baseline">
              <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
            </dd>
          </div>
        ))}
      </div>

      {/* Quick actions */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg font-medium leading-6 text-gray-900">
            Quick Actions
          </h3>
          <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div className="rounded-lg border border-gray-200 p-4 hover:bg-gray-50 cursor-pointer">
              <div className="flex items-center">
                <DocumentTextIcon className="h-8 w-8 text-blue-500" />
                <div className="ml-3">
                  <h4 className="text-sm font-medium text-gray-900">Upload Resume</h4>
                  <p className="text-sm text-gray-500">Add new job seeker resume</p>
                </div>
              </div>
            </div>
            
            <div className="rounded-lg border border-gray-200 p-4 hover:bg-gray-50 cursor-pointer">
              <div className="flex items-center">
                <BriefcaseIcon className="h-8 w-8 text-green-500" />
                <div className="ml-3">
                  <h4 className="text-sm font-medium text-gray-900">Post Job</h4>
                  <p className="text-sm text-gray-500">Create new job position</p>
                </div>
              </div>
            </div>
            
            <div className="rounded-lg border border-gray-200 p-4 hover:bg-gray-50 cursor-pointer">
              <div className="flex items-center">
                <ChartBarIcon className="h-8 w-8 text-purple-500" />
                <div className="ml-3">
                  <h4 className="text-sm font-medium text-gray-900">Matching Analysis</h4>
                  <p className="text-sm text-gray-500">Perform intelligent matching analysis</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* System status */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg font-medium leading-6 text-gray-900">
            System Status
          </h3>
          <div className="mt-5">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">AI Matching Service</span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Running
              </span>
            </div>
            <div className="mt-3 flex items-center justify-between">
              <span className="text-sm text-gray-500">Database Connection</span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Connected
              </span>
            </div>
            <div className="mt-3 flex items-center justify-between">
              <span className="text-sm text-gray-500">API Service</span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Active
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;