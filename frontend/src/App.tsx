import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/common/Layout';
import Dashboard from './components/Dashboard';
import JobList from './components/jobs/JobList';
import ResumeUpload from './components/ResumeUpload';
import JobUpload from './components/JobUpload';
import MatchingAnalysis from './components/MatchingAnalysis';
import './App.css';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// Main application component
const AppContent: React.FC = () => {
  return (
    <Router>
      <Layout>
        <Routes>
          {/* Main feature pages */}
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/jobs" element={<JobList />} />
          <Route path="/resume-upload" element={<ResumeUpload />} />
          <Route path="/job-upload" element={<JobUpload />} />
          <Route path="/matching" element={<MatchingAnalysis />} />
          <Route path="/" element={<Navigate to="/matching" replace />} />
          <Route path="*" element={
            <div className="text-center py-12">
              <h1 className="text-2xl font-bold text-gray-900">Page Not Found</h1>
              <p className="text-gray-600 mt-2">Please check if the URL is correct</p>
            </div>
          } />
        </Routes>
      </Layout>
    </Router>
  );
};

// Root application component
const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  );
};

export default App;
