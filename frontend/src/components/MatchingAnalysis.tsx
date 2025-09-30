import React, { useState, useEffect } from 'react';
import { ChartBarIcon, CheckCircleIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline';

interface Resume {
  id: number;
  name: string;
  email: string;
  education: string;
  experience: string;
  skills: string;
}

interface Job {
  id: number;
  title: string;
  description: string;
  requirements: string;
  job_type: string;
  experience_level: string;
  location_city: string;
}

interface MatchingResult {
  overall_score: number;
  detailed_analysis: string;
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
}

const MatchingAnalysis: React.FC = () => {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState<number | null>(null);
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null);
  const [matchingResult, setMatchingResult] = useState<MatchingResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Load resume list
  useEffect(() => {
    const fetchResumes = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/resumes/');
        if (response.ok) {
          const data = await response.json();
          setResumes(data.results || data);
        }
      } catch (error) {
        console.error('Failed to fetch resume list:', error);
        setResumes([]); // Ensure resumes is always an array
      }
    };

    fetchResumes();
  }, []);

  // Load job list
  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/jobs/');
        if (response.ok) {
          const data = await response.json();
          setJobs(data.results || data);
        }
      } catch (error) {
        console.error('Failed to fetch job list:', error);
        setJobs([]); // Ensure jobs is always an array
      }
    };

    fetchJobs();
  }, []);

  const handleAnalyze = async () => {
    if (!selectedResumeId || !selectedJobId) {
      setError('Please select both resume and job position');
      return;
    }

    setLoading(true);
    setError('');
    setMatchingResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/matching/analyze/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          resume_id: selectedResumeId,
          job_id: selectedJobId,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setMatchingResult(data);
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'Matching analysis failed');
      }
    } catch (error) {
      setError('Network error, please check your connection');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  return (
    <div className="space-y-6">
      {/* Matching results - at the very top */}
      {matchingResult && (
        <div className="bg-white shadow-lg rounded-lg overflow-hidden">
          <div className="px-6 py-4 bg-gradient-to-r from-indigo-500 to-purple-600">
            <h2 className="text-xl font-bold text-white flex items-center">
              <CheckCircleIcon className="h-6 w-6 mr-2" />
              Matching Analysis Results
            </h2>
          </div>

          <div className="p-6 space-y-6">
            {/* Matching score */}
            <div className="text-center">
              <div className={`inline-flex items-center justify-center w-24 h-24 rounded-full ${getScoreBgColor(matchingResult.overall_score)}`}>
                <span className={`text-3xl font-bold ${getScoreColor(matchingResult.overall_score)}`}>
                  {matchingResult.overall_score}%
                </span>
              </div>
              <p className="mt-2 text-lg font-medium text-gray-900">Match Score</p>
            </div>

            {/* Analysis results */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Comprehensive Analysis</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-gray-700 leading-relaxed">{matchingResult.detailed_analysis}</p>
              </div>
            </div>

            {/* Strengths and weaknesses */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Strengths */}
              <div>
                <h3 className="text-lg font-semibold text-green-700 mb-3">Matching Strengths</h3>
                <ul className="space-y-2">
                  {matchingResult.strengths.map((strength, index) => (
                    <li key={index} className="flex items-start">
                      <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700">{strength}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Areas for improvement */}
              <div>
                <h3 className="text-lg font-semibold text-red-700 mb-3">Areas for Improvement</h3>
                <ul className="space-y-2">
                  {matchingResult.weaknesses.map((weakness, index) => (
                    <li key={index} className="flex items-start">
                      <ExclamationCircleIcon className="h-5 w-5 text-red-500 mr-2 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700">{weakness}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Recommendations */}
            <div>
              <h3 className="text-lg font-semibold text-blue-700 mb-3">Improvement Recommendations</h3>
              <ul className="space-y-2">
                {matchingResult.recommendations.map((recommendation, index) => (
                  <li key={index} className="flex items-start">
                    <ChartBarIcon className="h-5 w-5 text-blue-500 mr-2 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{recommendation}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Page title */}
      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        <div className="px-6 py-4 bg-gradient-to-r from-purple-500 to-pink-600">
          <h1 className="text-2xl font-bold text-white flex items-center">
            <ChartBarIcon className="h-8 w-8 mr-3" />
            AI Intelligent Matching Analysis
          </h1>
          <p className="text-purple-100 mt-2">Select resume and job position to get intelligent matching analysis results</p>
        </div>
      </div>

      {/* Selection area */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
          {/* Resume selection */}
          <div className="bg-white shadow-lg rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Select Resume</h2>
            <div className="space-y-3 max-h-80 overflow-y-auto">
              {resumes.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No resume data available, please upload a resume first</p>
              ) : (
                resumes.map((resume) => (
                  <div
                    key={resume.id}
                    className={`p-4 border rounded-lg cursor-pointer transition-all duration-200 hover:shadow-md ${
                      selectedResumeId === resume.id
                        ? 'border-blue-500 bg-blue-50 shadow-md'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedResumeId(resume.id)}
                  >
                    <div className="flex items-center">
                      <input
                        type="radio"
                        checked={selectedResumeId === resume.id}
                        onChange={() => setSelectedResumeId(resume.id)}
                        className="mr-3 h-4 w-4 text-blue-600"
                      />
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900">{resume.name}</h3>
                        <p className="text-sm text-gray-600">{resume.email}</p>
                        <p className="text-xs text-gray-500 mt-1 truncate">
                          Skills: {resume.skills.substring(0, 60)}...
                        </p>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Job selection */}
          <div className="bg-white shadow-lg rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Select Job Position</h2>
            <div className="space-y-3 max-h-80 overflow-y-auto">
              {jobs.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No job data available, please upload job descriptions first</p>
              ) : (
                jobs.map((job) => (
                  <div
                    key={job.id}
                    className={`p-4 border rounded-lg cursor-pointer transition-all duration-200 hover:shadow-md ${
                      selectedJobId === job.id
                        ? 'border-green-500 bg-green-50 shadow-md'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedJobId(job.id)}
                  >
                    <div className="flex items-center">
                      <input
                        type="radio"
                        checked={selectedJobId === job.id}
                        onChange={() => setSelectedJobId(job.id)}
                        className="mr-3 h-4 w-4 text-green-600"
                      />
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900">{job.title}</h3>
                        <p className="text-sm text-gray-600">{job.location_city}</p>
                        <p className="text-xs text-gray-500">{job.job_type} · {job.experience_level}</p>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Matching button */}
        <div className="text-center">
          <button
            onClick={handleAnalyze}
            disabled={loading || !selectedResumeId || !selectedJobId}
            className={`px-8 py-3 rounded-lg font-medium text-white ${
              loading || !selectedResumeId || !selectedJobId
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2'
            }`}
          >
            <ChartBarIcon className="h-5 w-5 inline mr-2" />
            {loading ? 'Analyzing...' : 'Start Matching Analysis'}
          </button>
        </div>

        {/* Error message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center">
            <ExclamationCircleIcon className="h-5 w-5 text-red-500 mr-2" />
            <span className="text-red-800">{error}</span>
          </div>
        )}
      </div>
  );
};

export default MatchingAnalysis;