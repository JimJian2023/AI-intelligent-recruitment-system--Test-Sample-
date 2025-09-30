import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  BriefcaseIcon,
  DocumentTextIcon,
  ChartBarIcon,
  UserGroupIcon,
  EyeIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  PlusIcon,
  ArrowTrendingUpIcon,
} from '@heroicons/react/24/outline';
import { useAuth } from '../../contexts/AuthContext';
import { authAPI, jobAPI, applicationAPI, matchingAPI } from '../../services/api';
import { DashboardStats, Job, Application } from '../../types';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentJobs, setRecentJobs] = useState<Job[]>([]);
  const [recentApplications, setRecentApplications] = useState<Application[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        
        // Get dashboard statistics
        const dashboardResponse = await authAPI.getDashboard();
        setStats(dashboardResponse.data);

        // Get relevant data based on user type
        if (user?.user_type === 'student') {
          // Student: get latest jobs and application records
          const [jobsResponse, applicationsResponse] = await Promise.all([
            jobAPI.getRecentJobs(),
            applicationAPI.getApplications({ page_size: 5 }),
          ]);
          setRecentJobs(jobsResponse.data);
          setRecentApplications(applicationsResponse.data.results);
        } else if (user?.user_type === 'employer') {
          // Employer: get my jobs and received applications
          const [jobsResponse, applicationsResponse] = await Promise.all([
            jobAPI.getMyJobs({ page_size: 5 }),
            applicationAPI.getApplications({ page_size: 5 }),
          ]);
          setRecentJobs(jobsResponse.data.results);
          setRecentApplications(applicationsResponse.data.results);
        }
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, [user]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const getQuickActions = () => {
    if (user?.user_type === 'student') {
      return [
        { name: 'Search Jobs', href: '/jobs', icon: BriefcaseIcon, color: 'bg-blue-500' },
        { name: 'View Applications', href: '/applications', icon: DocumentTextIcon, color: 'bg-green-500' },
        { name: 'Match Recommendations', href: '/recommendations', icon: ChartBarIcon, color: 'bg-purple-500' },
        { name: 'Complete Profile', href: '/profile', icon: UserGroupIcon, color: 'bg-orange-500' },
      ];
    } else {
      return [
        { name: 'Post Job', href: '/jobs/create', icon: PlusIcon, color: 'bg-blue-500' },
        { name: 'Manage Jobs', href: '/my-jobs', icon: BriefcaseIcon, color: 'bg-green-500' },
        { name: 'Application Management', href: '/applications', icon: DocumentTextIcon, color: 'bg-purple-500' },
        { name: 'Matching Analysis', href: '/matching', icon: ChartBarIcon, color: 'bg-orange-500' },
      ];
    }
  };

  const getStatCards = () => {
    if (user?.user_type === 'student') {
      return [
        {
          name: 'Job Applications',
          value: stats?.applications_count || 0,
          icon: DocumentTextIcon,
          color: 'text-blue-600',
          bgColor: 'bg-blue-50',
          change: '+12%',
          changeType: 'positive',
        },
        {
          name: 'Interview Invitations',
          value: stats?.interviews_count || 0,
          icon: UserGroupIcon,
          color: 'text-green-600',
          bgColor: 'bg-green-50',
          change: '+8%',
          changeType: 'positive',
        },
        {
          name: 'Matched Jobs',
          value: stats?.matches_count || 0,
          icon: ChartBarIcon,
          color: 'text-purple-600',
          bgColor: 'bg-purple-50',
          change: '+15%',
          changeType: 'positive',
        },
        {
          name: 'Profile Completeness',
          value: `${stats?.profile_completeness || 0}%`,
          icon: CheckCircleIcon,
          color: 'text-orange-600',
          bgColor: 'bg-orange-50',
          change: '+5%',
          changeType: 'positive',
        },
      ];
    } else {
      return [
        {
          name: 'Posted Jobs',
          value: stats?.jobs_count || 0,
          icon: BriefcaseIcon,
          color: 'text-blue-600',
          bgColor: 'bg-blue-50',
          change: '+3',
          changeType: 'positive',
        },
        {
          name: 'Received Applications',
          value: stats?.applications_count || 0,
          icon: DocumentTextIcon,
          color: 'text-green-600',
          bgColor: 'bg-green-50',
          change: '+25%',
          changeType: 'positive',
        },
        {
          name: 'Job Views',
          value: stats?.views_count || 0,
          icon: EyeIcon,
          color: 'text-purple-600',
          bgColor: 'bg-purple-50',
          change: '+18%',
          changeType: 'positive',
        },
        {
          name: 'Matched Candidates',
          value: stats?.matches_count || 0,
          icon: UserGroupIcon,
          color: 'text-orange-600',
          bgColor: 'bg-orange-50',
          change: '+12%',
          changeType: 'positive',
        },
      ];
    }
  };

  const quickActions = getQuickActions();
  const statCards = getStatCards();

  return (
    <div className="space-y-6">
      {/* Welcome area */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">
              {getGreeting()}, {user?.first_name}!
            </h1>
            <p className="text-blue-100 mt-1">
              {user?.user_type === 'student' 
                ? 'Discover new career opportunities waiting for you today' 
                : 'Manage your recruitment process and find the best candidates'}
            </p>
          </div>
          <div className="hidden sm:block">
            <ArrowTrendingUpIcon className="h-16 w-16 text-blue-200" />
          </div>
        </div>
      </div>

      {/* Statistics cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat) => (
          <div key={stat.name} className="card">
            <div className="flex items-center">
              <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                <stat.icon className={`h-6 w-6 ${stat.color}`} />
              </div>
              <div className="ml-4 flex-1">
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <div className="flex items-baseline">
                  <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
                  <p className={`ml-2 text-sm font-medium ${
                    stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {stat.change}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick actions */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Quick Actions</h2>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {quickActions.map((action) => (
            <Link
              key={action.name}
              to={action.href}
              className="flex flex-col items-center p-4 rounded-lg border border-gray-200 hover:border-gray-300 hover:shadow-md transition-all duration-200 group"
            >
              <div className={`p-3 rounded-lg ${action.color} group-hover:scale-110 transition-transform duration-200`}>
                <action.icon className="h-6 w-6 text-white" />
              </div>
              <span className="mt-2 text-sm font-medium text-gray-700 text-center">
                {action.name}
              </span>
            </Link>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent jobs/My jobs */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">
              {user?.user_type === 'student' ? 'Latest Jobs' : 'My Jobs'}
            </h2>
            <Link
              to={user?.user_type === 'student' ? '/jobs' : '/my-jobs'}
              className="text-sm text-blue-600 hover:text-blue-500"
            >
              View All
            </Link>
          </div>
          <div className="space-y-3">
            {recentJobs.length > 0 ? (
              recentJobs.slice(0, 5).map((job) => (
                <div key={job.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {job.title}
                    </p>
                    <p className="text-xs text-gray-500">
                      {job.employer?.company_name} • {job.location}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800`}>
                      Hiring
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-6 text-gray-500">
                <BriefcaseIcon className="mx-auto h-12 w-12 text-gray-400" />
                <p className="mt-2 text-sm">
                  {user?.user_type === 'student' ? 'No latest jobs available' : 'You haven\'t posted any jobs yet'}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Recent applications */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">
              {user?.user_type === 'student' ? 'My Applications' : 'Received Applications'}
            </h2>
            <Link
              to="/applications"
              className="text-sm text-blue-600 hover:text-blue-500"
            >
              View All
            </Link>
          </div>
          <div className="space-y-3">
            {recentApplications.length > 0 ? (
              recentApplications.slice(0, 5).map((application) => (
                <div key={application.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      Job Application
                    </p>
                    <p className="text-sm text-gray-600">
                      {user?.user_type === 'student'
                        ? 'Employer Information'
                        : 'Student Information'
                      }
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      application.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      application.status === 'reviewing' ? 'bg-blue-100 text-blue-800' :
                      application.status === 'interview' ? 'bg-purple-100 text-purple-800' :
                      application.status === 'accepted' ? 'bg-green-100 text-green-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {application.status === 'pending' ? 'Pending' :
                       application.status === 'reviewing' ? 'Under Review' :
                       application.status === 'interview' ? 'Interview' :
                       application.status === 'accepted' ? 'Accepted' : 'Rejected'}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-6 text-gray-500">
                <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
                <p className="mt-2 text-sm">
                  {user?.user_type === 'student' ? 'You haven\'t applied to any jobs yet' : 'No applications received yet'}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;