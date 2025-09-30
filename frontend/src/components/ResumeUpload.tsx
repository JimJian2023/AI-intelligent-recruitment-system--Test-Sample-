import React, { useState } from 'react';
import { DocumentArrowUpIcon, CheckCircleIcon, ExclamationCircleIcon, SparklesIcon } from '@heroicons/react/24/outline';

interface ResumeData {
  name: string;
  email: string;
  phone: string;
  education: string;
  experience: string;
  skills: string;
  file?: File;
}

const ResumeUpload: React.FC = () => {
  const [resumeData, setResumeData] = useState<ResumeData>({
    name: '',
    email: '',
    phone: '',
    education: '',
    experience: '',
    skills: '',
  });
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'parsing' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setResumeData(prev => ({
        ...prev,
        file
      }));
    }
  };

  const parseResumeWithAI = async (file: File) => {
    setUploadStatus('parsing');
    setMessage('Parsing resume content with AI...');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/api/resumes/parse/', {
        method: 'POST',
        body: formData,
        // Don't manually set Content-Type, let browser set multipart/form-data boundary automatically
      });

      if (response.ok) {
        const result = await response.json();
        const parsedData = result.data; // Backend returns data in data field
        setResumeData(prev => ({
          ...prev,
          name: parsedData.name || '',
          email: parsedData.email || '',
          phone: parsedData.phone || '',
          education: parsedData.education || '',
          experience: parsedData.work_experience || '',
          skills: parsedData.skills || '',
        }));
        
        // Display AI parsing detailed information
        if (result.ai_response) {
          setUploadStatus('success');
          setMessage(`AI parsing successful!\n\n=== AI Original Response ===\n${result.ai_response}\n\n=== Extracted Text Content ===\n${result.extracted_text || 'None'}\n\n=== Prompt Used ===\n${result.prompt_used || 'None'}\n\nAI Service Status: ${result.ai_enabled ? 'Enabled' : 'Disabled'}`);
        } else {
          setUploadStatus('idle');
          setMessage('AI parsing completed! Please review and confirm the information');
        }
      } else {
        const errorResult = await response.json();
        setUploadStatus('error');
        setMessage(errorResult.message || 'AI parsing failed, please fill in information manually');
      }
    } catch (error) {
      setUploadStatus('error');
      setMessage('AI parsing service temporarily unavailable, please fill in information manually');
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setResumeData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setUploadStatus('uploading');
    setMessage('');

    try {
      const formData = new FormData();
      formData.append('name', resumeData.name);
      formData.append('email', resumeData.email);
      formData.append('phone', resumeData.phone);
      formData.append('education', resumeData.education);
      formData.append('experience', resumeData.experience);
      formData.append('skills', resumeData.skills);
      
      if (resumeData.file) {
        formData.append('resume_file', resumeData.file);
      }

      const response = await fetch('http://localhost:8000/api/resumes/', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        setUploadStatus('success');
        setMessage('Resume uploaded successfully!');
        // Reset form
        setResumeData({
          name: '',
          email: '',
          phone: '',
          education: '',
          experience: '',
          skills: '',
        });
        // Clear file input
        const fileInput = document.getElementById('resume-file') as HTMLInputElement;
        if (fileInput) fileInput.value = '';
      } else {
        const errorData = await response.json();
        setUploadStatus('error');
        setMessage(errorData.message || 'Upload failed, please try again');
      }
    } catch (error) {
      setUploadStatus('error');
      setMessage('Network error, please check connection');
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        <div className="px-6 py-4 bg-gradient-to-r from-blue-500 to-purple-600">
          <h1 className="text-2xl font-bold text-white flex items-center">
            <DocumentArrowUpIcon className="h-8 w-8 mr-3" />
            Resume Upload
          </h1>
          <p className="text-blue-100 mt-2">Please fill in your resume information and upload resume file</p>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* File Upload Area - Moved to front */}
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors">
            <div className="space-y-4">
              <div className="flex justify-center">
                <DocumentArrowUpIcon className="h-12 w-12 text-gray-400" />
              </div>
              <div>
                <label htmlFor="resume-file" className="cursor-pointer">
                  <span className="text-lg font-medium text-gray-900">Upload Resume File</span>
                  <p className="text-sm text-gray-500 mt-1">
                    Supports PDF, DOC, DOCX formats, file size not exceeding 10MB
                  </p>
                  <input
                    type="file"
                    id="resume-file"
                    onChange={handleFileChange}
                    accept=".pdf,.doc,.docx"
                    className="hidden"
                  />
                  <div className="mt-4">
                    <span className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                      Choose File
                    </span>
                  </div>
                </label>
              </div>
              
              {selectedFile && (
                <div className="mt-4 p-4 bg-blue-50 rounded-md">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2" />
                      <span className="text-sm text-gray-700">{selectedFile.name}</span>
                    </div>
                    <button
                      type="button"
                      onClick={() => parseResumeWithAI(selectedFile)}
                      disabled={uploadStatus === 'parsing'}
                      className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <SparklesIcon className="h-4 w-4 mr-1" />
                      {uploadStatus === 'parsing' ? 'Parsing...' : 'AI Parse'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* AI Feedback Messages */}
          {message && (
            <div className={`rounded-md ${
              uploadStatus === 'success' ? 'bg-green-50 border border-green-200' :
              uploadStatus === 'error' ? 'bg-red-50 border border-red-200' :
              uploadStatus === 'parsing' ? 'bg-blue-50 border border-blue-200' :
              'bg-gray-50 border border-gray-200'
            }`}>
              <div className={`p-3 flex items-center ${
                uploadStatus === 'success' ? 'text-green-800' :
                uploadStatus === 'error' ? 'text-red-800' :
                uploadStatus === 'parsing' ? 'text-blue-800' :
                'text-gray-800'
              }`}>
                {uploadStatus === 'success' && <CheckCircleIcon className="h-5 w-5 mr-2 flex-shrink-0" />}
                {uploadStatus === 'error' && <ExclamationCircleIcon className="h-5 w-5 mr-2 flex-shrink-0" />}
                {uploadStatus === 'parsing' && <SparklesIcon className="h-5 w-5 mr-2 flex-shrink-0 animate-spin" />}
                <span className="text-sm font-medium">
                  {uploadStatus === 'success' ? 'AI Parsing Successful' :
                   uploadStatus === 'error' ? 'Parsing Failed' :
                   uploadStatus === 'parsing' ? 'AI is parsing...' :
                   'Status Information'}
                </span>
              </div>
              <div className="px-3 pb-3">
                <textarea
                  readOnly
                  value={message}
                  className={`w-full h-32 p-3 text-sm border rounded-md resize-none overflow-y-auto ${
                    uploadStatus === 'success' ? 'bg-white border-green-300 text-green-900' :
                    uploadStatus === 'error' ? 'bg-white border-red-300 text-red-900' :
                    uploadStatus === 'parsing' ? 'bg-white border-blue-300 text-blue-900' :
                    'bg-white border-gray-300 text-gray-900'
                  }`}
                  style={{ fontFamily: 'monospace' }}
                />
              </div>
            </div>
          )}

          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                Name *
              </label>
              <input
                type="text"
                id="name"
                name="name"
                value={resumeData.name}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Please enter your name"
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email *
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={resumeData.email}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Please enter your email"
              />
            </div>

            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                Phone
              </label>
              <input
                type="tel"
                id="phone"
                name="phone"
                value={resumeData.phone}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Please enter your phone number"
              />
            </div>
          </div>

          {/* Education Background */}
          <div>
            <label htmlFor="education" className="block text-sm font-medium text-gray-700 mb-2">
              Education Background *
            </label>
            <textarea
              id="education"
              name="education"
              value={resumeData.education}
              onChange={handleInputChange}
              required
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Please describe your education background, such as school, major, degree, etc."
            />
          </div>

          {/* Work Experience */}
          <div>
            <label htmlFor="experience" className="block text-sm font-medium text-gray-700 mb-2">
              Work Experience *
            </label>
            <textarea
              id="experience"
              name="experience"
              value={resumeData.experience}
              onChange={handleInputChange}
              required
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Please describe your work experience, including company, position, job content, etc."
            />
          </div>

          {/* Skills */}
          <div>
            <label htmlFor="skills" className="block text-sm font-medium text-gray-700 mb-2">
              Skills & Expertise *
            </label>
            <textarea
              id="skills"
              name="skills"
              value={resumeData.skills}
              onChange={handleInputChange}
              required
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Please list your skills and expertise, such as programming languages, tools, certificates, etc."
            />
          </div>

          {/* Submit Button */}
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={uploadStatus === 'uploading' || uploadStatus === 'parsing'}
              className={`px-6 py-3 rounded-md font-medium text-white ${
                uploadStatus === 'uploading' || uploadStatus === 'parsing'
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
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

export default ResumeUpload;