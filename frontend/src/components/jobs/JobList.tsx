import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  MagnifyingGlassIcon,
  MapPinIcon,
  CurrencyDollarIcon,
  ClockIcon,
  BriefcaseIcon,
  FunnelIcon,
  HeartIcon,
  EyeIcon,
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartSolidIcon } from '@heroicons/react/24/solid';
import { jobAPI, applicationAPI, commonAPI } from '../../services/api';
import { Job, JobSearchForm, PaginatedResponse } from '../../types';
import { useAuth } from '../../contexts/AuthContext';

const JobList: React.FC = () => {
  const { user } = useAuth();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({
    count: 0,
    next: null as string | null,
    previous: null as string | null,
    current_page: 1,
    total_pages: 1,
  });
  const [savedJobs, setSavedJobs] = useState<Set<number>>(new Set());
  const [categories, setCategories] = useState<any[]>([]);
  const [searchForm, setSearchForm] = useState<JobSearchForm>({
    search: '',
    location: '',
    job_type: '',
    salary_min: undefined as number | undefined,
    salary_max: undefined as number | undefined,
    category: undefined as number | undefined,
    experience_level: '',
  });
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    fetchJobs();
    fetchCategories();
    if (user?.user_type === 'student') {
      fetchSavedJobs();
    }
  }, []);

  const fetchJobs = async (page = 1, filters = searchForm) => {
    try {
      setLoading(true);
      const response = await jobAPI.getJobs({
        ...filters,
        page,
        page_size: 12,
      });
      setJobs(response.data.results);
      setPagination({
        count: response.data.count,
        next: response.data.next || null,
        previous: response.data.previous || null,
        current_page: page,
        total_pages: Math.ceil(response.data.count / 12),
      });
    } catch (error) {
      console.error('Failed to fetch jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await commonAPI.getJobCategories();
      setCategories(response.data);
    } catch (error) {
      console.error('Failed to fetch categories:', error);
    }
  };

  const fetchSavedJobs = async () => {
    try {
      const response = await applicationAPI.getSavedJobs();
      const savedJobIds = new Set(response.data.results.map((item: any) => item.job.id));
      setSavedJobs(savedJobIds);
    } catch (error) {
      console.error('Failed to fetch saved jobs:', error);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchJobs(1, searchForm);
  };

  const handleFilterChange = (key: keyof JobSearchForm, value: string | number | undefined) => {
    setSearchForm(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  const handlePageChange = (page: number) => {
    fetchJobs(page, searchForm);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSaveJob = async (jobId: number) => {
    if (!user || user.user_type !== 'student') return;

    try {
      if (savedJobs.has(jobId)) {
        // Unsave job
        const savedJobsResponse = await applicationAPI.getSavedJobs();
        const savedJob = savedJobsResponse.data.results.find((item: any) => item.job.id === jobId);
        if (savedJob) {
          await applicationAPI.unsaveJob(savedJob.id);
          setSavedJobs(prev => {
            const newSet = new Set(prev);
            newSet.delete(jobId);
            return newSet;
          });
        }
      } else {
        // Save job
        await applicationAPI.saveJob({ job_id: jobId });
        setSavedJobs(prev => new Set(prev).add(jobId));
      }
    } catch (error) {
      console.error('Failed to save/unsave job:', error);
    }
  };

  const formatSalary = (min?: number, max?: number) => {
    if (!min && !max) return 'Salary Negotiable';
    if (min && max) return `${min}k - ${max}k`;
    if (min) return `${min}k+`;
    return `Up to ${max}k`;
  };

  const getJobTypeLabel = (type: string) => {
    const types: { [key: string]: string } = {
      'full-time': 'Full-time',
      'part-time': 'Part-time',
      'internship': 'Internship',
      'contract': 'Contract',
      'remote': 'Remote',
    };
    return types[type] || type;
  };

  const getExperienceLevelLabel = (level: string) => {
    const levels: { [key: string]: string } = {
      'entry': 'Entry Level',
      'junior': 'Junior',
      'mid': 'Mid Level',
      'senior': 'Senior',
      'lead': 'Expert Level',
    };
    return levels[level] || level;
  };

  return (
    <div className="space-y-6">
      {/* Search Bar */}
      <div className="card">
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search jobs, companies or skills..."
                  value={searchForm.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                  className="input-field pl-10"
                />
              </div>
            </div>
            <div className="md:w-64">
              <div className="relative">
                <MapPinIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Location"
                  value={searchForm.location}
                  onChange={(e) => handleFilterChange('location', e.target.value)}
                  className="input-field pl-10"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setShowFilters(!showFilters)}
                className="btn-secondary flex items-center"
              >
                <FunnelIcon className="h-5 w-5 mr-2" />
                Filters
              </button>
              <button type="submit" className="btn-primary">
                Search
              </button>
            </div>
          </div>

          {/* Advanced Filters */}
          {showFilters && (
            <div className="border-t pt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Job Type
                </label>
                <select
                  value={searchForm.job_type}
                  onChange={(e) => handleFilterChange('job_type', e.target.value)}
                  className="input-field"
                >
                  <option value="">All Types</option>
                  <option value="full-time">Full-time</option>
                  <option value="part-time">Part-time</option>
                  <option value="internship">Internship</option>
                  <option value="contract">Contract</option>
                  <option value="remote">Remote</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Job Category
                </label>
                <select
                  value={searchForm.category}
                  onChange={(e) => handleFilterChange('category', e.target.value)}
                  className="input-field"
                >
                  <option value="">All Categories</option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Experience Level
                </label>
                <select
                  value={searchForm.experience_level}
                  onChange={(e) => handleFilterChange('experience_level', e.target.value)}
                  className="input-field"
                >
                  <option value="">All Levels</option>
                  <option value="entry">Entry Level</option>
                  <option value="junior">Junior</option>
                  <option value="mid">Mid Level</option>
                  <option value="senior">Senior</option>
                  <option value="lead">Expert Level</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Salary Range (k)
                </label>
                <div className="flex gap-2">
                  <input
                    type="number"
                    placeholder="Min"
                    value={searchForm.salary_min || ''}
                    onChange={(e) => handleFilterChange('salary_min', e.target.value ? Number(e.target.value) : undefined)}
                    className="input-field"
                  />
                  <input
                    type="number"
                    placeholder="Max"
                    value={searchForm.salary_max || ''}
                    onChange={(e) => handleFilterChange('salary_max', e.target.value ? Number(e.target.value) : undefined)}
                    className="input-field"
                  />
                </div>
              </div>
            </div>
          )}
        </form>
      </div>

      {/* Search Results Statistics */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-600">
          Found <span className="font-medium">{pagination.count}</span> jobs
        </p>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">Sort by:</span>
          <select className="text-sm border-gray-300 rounded-md">
            <option>Latest</option>
            <option>Highest Salary</option>
            <option>Relevance</option>
          </select>
        </div>
      </div>

      {/* Job List */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, index) => (
            <div key={index} className="card animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2 mb-4"></div>
              <div className="space-y-2">
                <div className="h-3 bg-gray-200 rounded"></div>
                <div className="h-3 bg-gray-200 rounded w-5/6"></div>
              </div>
            </div>
          ))}
        </div>
      ) : jobs.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {jobs.map((job) => (
            <div key={job.id} className="card hover:shadow-lg transition-shadow duration-200">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <Link
                    to={`/jobs/${job.id}`}
                    className="text-lg font-semibold text-gray-900 hover:text-blue-600 transition-colors duration-200"
                  >
                    {job.title}
                  </Link>
                  <p className="text-sm text-gray-600 mt-1">
                    {job.employer?.company_name}
                  </p>
                </div>
                {user?.user_type === 'student' && (
                  <button
                    onClick={() => handleSaveJob(job.id)}
                    className="p-2 text-gray-400 hover:text-red-500 transition-colors duration-200"
                  >
                    {savedJobs.has(job.id) ? (
                      <HeartSolidIcon className="h-5 w-5 text-red-500" />
                    ) : (
                      <HeartIcon className="h-5 w-5" />
                    )}
                  </button>
                )}
              </div>

              <div className="space-y-2 mb-4">
                <div className="flex items-center text-sm text-gray-600">
                  <MapPinIcon className="h-4 w-4 mr-1" />
                  {job.location}
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <CurrencyDollarIcon className="h-4 w-4 mr-1" />
                  {formatSalary(job.salary_min, job.salary_max)}
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <BriefcaseIcon className="h-4 w-4 mr-1" />
                  {getJobTypeLabel(job.job_type)} • {getExperienceLevelLabel(job.experience_level)}
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <ClockIcon className="h-4 w-4 mr-1" />
                  {new Date(job.created_at).toLocaleDateString('en-US')}
                </div>
              </div>

              <p className="text-sm text-gray-700 mb-4 line-clamp-3">
                {job.description}
              </p>

              {/* Skill Tags */}
              {job.skill_requirements && job.skill_requirements.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-4">
                  {job.skill_requirements.slice(0, 3).map((skillReq) => (
                    <span key={skillReq.id} className="tag">
                      {skillReq.skill.name}
                    </span>
                  ))}
                  {job.skill_requirements.length > 3 && (
                    <span className="tag">
                      +{job.skill_requirements.length - 3}
                    </span>
                  )}
                </div>
              )}

              <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                <div className="flex items-center space-x-4 text-xs text-gray-500">
                  <div className="flex items-center">
                    <EyeIcon className="h-4 w-4 mr-1" />
                    {job.views_count || 0}
                  </div>
                  <div className="flex items-center">
                    <BriefcaseIcon className="h-4 w-4 mr-1" />
                    {job.applications_count || 0} applications
                  </div>
                </div>
                <Link
                  to={`/jobs/${job.id}`}
                  className="btn-primary text-sm"
                >
                  View Details
                </Link>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <BriefcaseIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No jobs found</h3>
          <p className="mt-1 text-sm text-gray-500">
            Try adjusting your search criteria or filters
          </p>
        </div>
      )}

      {/* Pagination */}
      {pagination.total_pages > 1 && (
        <div className="flex items-center justify-between">
          <div className="flex-1 flex justify-between sm:hidden">
            <button
              onClick={() => handlePageChange(pagination.current_page - 1)}
              disabled={!pagination.previous}
              className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <button
              onClick={() => handlePageChange(pagination.current_page + 1)}
              disabled={!pagination.next}
              className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
          <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-gray-700">
                Showing{' '}
                <span className="font-medium">
                  {(pagination.current_page - 1) * 12 + 1}
                </span>{' '}
                to{' '}
                <span className="font-medium">
                  {Math.min(pagination.current_page * 12, pagination.count)}
                </span>{' '}
                of{' '}
                <span className="font-medium">{pagination.count}</span> results
              </p>
            </div>
            <div>
              <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                <button
                  onClick={() => handlePageChange(pagination.current_page - 1)}
                  disabled={!pagination.previous}
                  className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                {[...Array(Math.min(5, pagination.total_pages))].map((_, index) => {
                  const page = index + 1;
                  return (
                    <button
                      key={page}
                      onClick={() => handlePageChange(page)}
                      className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                        page === pagination.current_page
                          ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                          : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                      }`}
                    >
                      {page}
                    </button>
                  );
                })}
                <button
                  onClick={() => handlePageChange(pagination.current_page + 1)}
                  disabled={!pagination.next}
                  className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </nav>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default JobList;