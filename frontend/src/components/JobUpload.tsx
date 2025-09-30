import React, { useState } from 'react';
import { BriefcaseIcon, CheckCircleIcon, ExclamationCircleIcon, SparklesIcon, DocumentArrowUpIcon } from '@heroicons/react/24/outline';

interface JobData {
  title: string;
  description: string;
  requirements: string;
  job_type: string;
  experience_level: string;
  location_city: string;
  remote_option: string;
  salary_min: string;
  salary_max: string;
  benefits: string;
  application_deadline: string;
  file?: File;
}

const JobUpload: React.FC = () => {
  const [jobData, setJobData] = useState<JobData>({
    title: '',
    description: '',
    requirements: '',
    job_type: 'full_time',
    experience_level: 'entry',
    location_city: '',
    remote_option: 'on_site',
    salary_min: '',
    salary_max: '',
    benefits: '',
    application_deadline: '',
  });
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'parsing' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [aiParseResult, setAiParseResult] = useState<any>(null);
  const [showParseResult, setShowParseResult] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setJobData(prev => ({
        ...prev,
        file
      }));
    }
  };

  const parseJobWithAI = async (file: File) => {
    setUploadStatus('parsing');
    setMessage('Parsing job description with AI...');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/api/jobs/parse/', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const parsedData = await response.json();
        setAiParseResult(parsedData); // Save original parse result
        setShowParseResult(true); // Show parse result
        setJobData(prev => ({
          ...prev,
          title: parsedData.title || '',
          description: parsedData.description || '',
          requirements: parsedData.requirements || '',
          job_type: parsedData.job_type || 'full_time',
          experience_level: parsedData.experience_level || 'entry',
          location_city: parsedData.location_city || '',
          remote_option: parsedData.remote_option || 'on_site',
          salary_min: parsedData.salary_min || '',
          salary_max: parsedData.salary_max || '',
          benefits: parsedData.benefits || '',
          application_deadline: typeof parsedData.application_deadline === 'string' 
            ? parsedData.application_deadline 
            : parsedData.application_deadline instanceof Date
              ? parsedData.application_deadline.toISOString().split('T')[0]
              : '',
        }));
        setUploadStatus('idle');
        setMessage('AI parsing completed! Please review and confirm the information');
      } else {
        setUploadStatus('error');
        setMessage('AI parsing failed, please fill in information manually');
      }
    } catch (error) {
      setUploadStatus('error');
      setMessage('AI parsing service temporarily unavailable, please fill in information manually');
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setJobData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setUploadStatus('uploading');
    setMessage('');

    try {
      // Prepare submission data, convert numeric fields
      const submitData = {
        ...jobData,
        salary_min: jobData.salary_min ? parseFloat(jobData.salary_min) : null,
        salary_max: jobData.salary_max ? parseFloat(jobData.salary_max) : null,
      };

      const response = await fetch('http://localhost:8000/api/jobs/demo-create/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(submitData),
      });

      if (response.ok) {
        const responseData = await response.json();
        setUploadStatus('success');
        setMessage(`Job description uploaded successfully! Job ID: ${responseData.id}`);
        // Reset form
        setJobData({
          title: '',
          description: '',
          requirements: '',
          job_type: 'full_time',
          experience_level: 'entry',
          location_city: '',
          remote_option: 'on_site',
          salary_min: '',
          salary_max: '',
          benefits: '',
          application_deadline: '',
        });
        setShowParseResult(false);
        setAiParseResult(null);
      } else {
        const errorData = await response.json();
        setUploadStatus('error');
        setMessage(errorData.error || 'Upload failed, please try again');
      }
    } catch (error) {
      setUploadStatus('error');
      setMessage('Network error, please check connection');
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        <div className="px-6 py-4 bg-gradient-to-r from-green-500 to-blue-600">
          <h1 className="text-2xl font-bold text-white flex items-center">
            <BriefcaseIcon className="h-8 w-8 mr-3" />
            Job Description Upload
          </h1>
          <p className="text-green-100 mt-2">Please fill in job information and requirements</p>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* File upload and AI parsing */}
          <div className="bg-gray-50 p-6 rounded-lg border-2 border-dashed border-gray-300">
            <div className="text-center">
              <DocumentArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
              <div className="mt-4">
                <label htmlFor="file-upload" className="cursor-pointer">
                  <span className="mt-2 block text-sm font-medium text-gray-900">
                    Upload Job Description Document
                  </span>
                  <span className="mt-1 block text-sm text-gray-500">
                    Supports PDF, DOC, DOCX formats
                  </span>
                </label>
                <input
                  id="file-upload"
                  name="file-upload"
                  type="file"
                  className="sr-only"
                  accept=".pdf,.doc,.docx"
                  onChange={handleFileChange}
                />
              </div>
              {selectedFile && (
                <div className="mt-4">
                  <p className="text-sm text-gray-600">Selected file: {selectedFile.name}</p>
                  <button
                    type="button"
                    onClick={() => parseJobWithAI(selectedFile)}
                    disabled={uploadStatus === 'parsing'}
                    className="mt-2 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50"
                  >
                    <SparklesIcon className="h-4 w-4 mr-2" />
                    {uploadStatus === 'parsing' ? 'AI Parsing...' : 'Parse with AI'}
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* AI Parse Results Display */}
          {showParseResult && aiParseResult && (
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-6 rounded-lg border border-purple-200">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-purple-800 flex items-center">
                  <SparklesIcon className="h-5 w-5 mr-2" />
                  AI Parse Results
                </h3>
                <button
                  type="button"
                  onClick={() => setShowParseResult(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                {aiParseResult.title && (
                  <div className="bg-white p-3 rounded border">
                    <span className="font-medium text-gray-700">Job Title:</span>
                    <p className="text-gray-900 mt-1">{aiParseResult.title}</p>
                  </div>
                )}
                
                {aiParseResult.location_city && (
                  <div className="bg-white p-3 rounded border">
                    <span className="font-medium text-gray-700">Location:</span>
                    <p className="text-gray-900 mt-1">{aiParseResult.location_city}</p>
                  </div>
                )}
                
                {(aiParseResult.salary_min || aiParseResult.salary_max) && (
                  <div className="bg-white p-3 rounded border">
                    <span className="font-medium text-gray-700">Salary Range:</span>
                    <p className="text-gray-900 mt-1">
                      {aiParseResult.salary_min && `${aiParseResult.salary_min}K`}
                      {aiParseResult.salary_min && aiParseResult.salary_max && ' - '}
                      {aiParseResult.salary_max && `${aiParseResult.salary_max}K`}
                    </p>
                  </div>
                )}
                
                {aiParseResult.job_type && (
                  <div className="bg-white p-3 rounded border">
                    <span className="font-medium text-gray-700">Job Type:</span>
                    <p className="text-gray-900 mt-1">
                      {aiParseResult.job_type === 'full_time' ? 'Full-time' : 
                       aiParseResult.job_type === 'part_time' ? 'Part-time' : 
                       aiParseResult.job_type === 'contract' ? 'Contract' : 
                       aiParseResult.job_type === 'internship' ? 'Internship' : aiParseResult.job_type}
                    </p>
                  </div>
                )}
                
                {aiParseResult.experience_level && (
                  <div className="bg-white p-3 rounded border">
                    <span className="font-medium text-gray-700">Experience Level:</span>
                    <p className="text-gray-900 mt-1">
                      {aiParseResult.experience_level === 'entry' ? 'Entry Level' : 
                       aiParseResult.experience_level === 'mid' ? 'Mid Level' : 
                       aiParseResult.experience_level === 'senior' ? 'Senior Level' : 
                       aiParseResult.experience_level === 'lead' ? 'Lead Level' : aiParseResult.experience_level}
                    </p>
                  </div>
                )}
                
                {aiParseResult.remote_option && (
                  <div className="bg-white p-3 rounded border">
                    <span className="font-medium text-gray-700">Remote Option:</span>
                    <p className="text-gray-900 mt-1">
                      {aiParseResult.remote_option === 'on_site' ? 'On-site' : 
                       aiParseResult.remote_option === 'remote' ? 'Remote' : 
                       aiParseResult.remote_option === 'hybrid' ? 'Hybrid' : aiParseResult.remote_option}
                    </p>
                  </div>
                )}
              </div>
              
              {aiParseResult.description && (
                <div className="mt-4 bg-white p-3 rounded border">
                  <span className="font-medium text-gray-700">Job Description:</span>
                  <p className="text-gray-900 mt-1 text-sm leading-relaxed">{aiParseResult.description}</p>
                </div>
              )}
              
              {aiParseResult.requirements && (
                <div className="mt-4 bg-white p-3 rounded border">
                  <span className="font-medium text-gray-700">Requirements:</span>
                  <p className="text-gray-900 mt-1 text-sm leading-relaxed">{aiParseResult.requirements}</p>
                </div>
              )}
              
              {aiParseResult.benefits && (
                <div className="mt-4 bg-white p-3 rounded border">
                  <span className="font-medium text-gray-700">Benefits:</span>
                  <p className="text-gray-900 mt-1 text-sm leading-relaxed">{aiParseResult.benefits}</p>
                </div>
              )}
              
              {aiParseResult.application_deadline && (
                <div className="mt-4 bg-white p-3 rounded border">
                  <span className="font-medium text-gray-700">Application Deadline:</span>
                  <p className="text-gray-900 mt-1 text-sm leading-relaxed">
                    {typeof aiParseResult.application_deadline === 'string' 
                      ? aiParseResult.application_deadline 
                      : aiParseResult.application_deadline instanceof Date
                        ? aiParseResult.application_deadline.toISOString().split('T')[0]
                        : aiParseResult.application_deadline?.toString() || 'Not specified'}
                  </p>
                </div>
              )}
              
              <div className="mt-4 text-xs text-purple-600 bg-purple-100 p-2 rounded">
                💡 Tip: AI has automatically filled the form fields, you can adjust as needed
              </div>
            </div>
          )}

          {/* Status Messages */}
          {message && (
            <div className={`p-4 rounded-md ${
              uploadStatus === 'success' ? 'bg-green-50 text-green-800' : 
              uploadStatus === 'error' ? 'bg-red-50 text-red-800' : 
              'bg-blue-50 text-blue-800'
            }`}>
              <div className="flex">
                <div className="flex-shrink-0">
                  {uploadStatus === 'success' ? (
                    <CheckCircleIcon className="h-5 w-5 text-green-400" />
                  ) : uploadStatus === 'error' ? (
                    <ExclamationCircleIcon className="h-5 w-5 text-red-400" />
                  ) : (
                    <SparklesIcon className="h-5 w-5 text-blue-400" />
                  )}
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium">{message}</p>
                </div>
              </div>
            </div>
          )}

          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
                Job Title *
              </label>
              <input
                type="text"
                id="title"
                name="title"
                value={jobData.title}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Frontend Developer"
              />
            </div>

            <div>
              <label htmlFor="location_city" className="block text-sm font-medium text-gray-700 mb-2">
                Location *
              </label>
              <input
                type="text"
                id="location_city"
                name="location_city"
                value={jobData.location_city}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., New York"
              />
            </div>

            <div>
              <label htmlFor="job_type" className="block text-sm font-medium text-gray-700 mb-2">
                Job Type *
              </label>
              <select
                id="job_type"
                name="job_type"
                value={jobData.job_type}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="full_time">Full-time</option>
                <option value="part_time">Part-time</option>
                <option value="internship">Internship</option>
                <option value="contract">Contract</option>
                <option value="freelance">Freelance</option>
              </select>
            </div>

            <div>
              <label htmlFor="experience_level" className="block text-sm font-medium text-gray-700 mb-2">
                Experience Level *
              </label>
              <select
                id="experience_level"
                name="experience_level"
                value={jobData.experience_level}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="entry">Entry Level</option>
                <option value="junior">Junior</option>
                <option value="mid">Mid Level</option>
                <option value="senior">Senior</option>
                <option value="lead">Lead</option>
                <option value="executive">Executive</option>
              </select>
            </div>

            <div>
              <label htmlFor="remote_option" className="block text-sm font-medium text-gray-700 mb-2">
                Work Arrangement
              </label>
              <select
                id="remote_option"
                name="remote_option"
                value={jobData.remote_option}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="on_site">On-site</option>
                <option value="remote">Remote</option>
                <option value="hybrid">Hybrid</option>
              </select>
            </div>

            <div>
              <label htmlFor="application_deadline" className="block text-sm font-medium text-gray-700 mb-2">
                Application Deadline
              </label>
              <input
                type="date"
                id="application_deadline"
                name="application_deadline"
                value={jobData.application_deadline}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Salary Range */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="salary_min" className="block text-sm font-medium text-gray-700 mb-2">
                Minimum Salary ($/month)
              </label>
              <input
                type="number"
                id="salary_min"
                name="salary_min"
                value={jobData.salary_min}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., 5000"
              />
            </div>

            <div>
              <label htmlFor="salary_max" className="block text-sm font-medium text-gray-700 mb-2">
                Maximum Salary ($/month)
              </label>
              <input
                type="number"
                id="salary_max"
                name="salary_max"
                value={jobData.salary_max}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., 8000"
              />
            </div>
          </div>

          {/* Detailed Description */}
          <div className="space-y-6">
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                Job Description *
              </label>
              <textarea
                id="description"
                name="description"
                value={jobData.description}
                onChange={handleInputChange}
                required
                rows={6}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Please describe the job content, responsibilities and requirements in detail..."
              />
            </div>

            <div>
              <label htmlFor="requirements" className="block text-sm font-medium text-gray-700 mb-2">
                Job Requirements *
              </label>
              <textarea
                id="requirements"
                name="requirements"
                value={jobData.requirements}
                onChange={handleInputChange}
                required
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Please list specific skill requirements, education requirements, experience requirements, etc..."
              />
            </div>

            <div>
              <label htmlFor="benefits" className="block text-sm font-medium text-gray-700 mb-2">
                Benefits
              </label>
              <textarea
                id="benefits"
                name="benefits"
                value={jobData.benefits}
                onChange={handleInputChange}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Health insurance, annual bonus, paid vacation, flexible working hours, etc..."
              />
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={uploadStatus === 'uploading' || uploadStatus === 'parsing'}
              className={`px-6 py-3 rounded-md font-medium text-white ${
                uploadStatus === 'uploading' || uploadStatus === 'parsing'
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-green-500 to-blue-600 hover:from-green-600 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2'
              }`}
            >
              {uploadStatus === 'uploading' ? 'Uploading...' : 
               uploadStatus === 'parsing' ? 'AI Parsing...' : 'Save to Database'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default JobUpload;