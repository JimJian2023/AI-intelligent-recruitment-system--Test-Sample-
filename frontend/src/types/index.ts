// 用户相关类型
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  user_type: 'student' | 'employer';
  is_active: boolean;
  date_joined: string;
  last_login?: string;
}

export interface Skill {
  id: number;
  name: string;
  category: string;
  description?: string;
}

export interface StudentSkill {
  id: number;
  skill: Skill;
  proficiency_level: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  years_of_experience: number;
  is_primary: boolean;
}

export interface Project {
  id: number;
  title: string;
  description: string;
  technologies_used: string[];
  start_date: string;
  end_date?: string;
  project_url?: string;
  github_url?: string;
  is_featured: boolean;
}

export interface StudentProfile {
  id: number;
  user: User;
  bio?: string;
  location?: string;
  phone?: string;
  linkedin_url?: string;
  github_url?: string;
  portfolio_url?: string;
  resume?: string;
  education_level: 'high_school' | 'associate' | 'bachelor' | 'master' | 'phd';
  major?: string;
  graduation_year?: number;
  gpa?: number;
  expected_salary_min?: number;
  expected_salary_max?: number;
  preferred_job_type: 'full_time' | 'part_time' | 'internship' | 'contract';
  preferred_work_location: 'remote' | 'onsite' | 'hybrid';
  availability_date?: string;
  is_open_to_work: boolean;
  profile_completion_percentage: number;
  skills: StudentSkill[];
  projects: Project[];
}

export interface EmployerProfile {
  id: number;
  user: User;
  company_name: string;
  company_description?: string;
  company_website?: string;
  company_size: 'startup' | 'small' | 'medium' | 'large' | 'enterprise';
  industry: string;
  location?: string;
  phone?: string;
  linkedin_url?: string;
  logo?: string;
  is_verified: boolean;
}

// 职位相关类型
export interface JobCategory {
  id: number;
  name: string;
  description?: string;
  icon?: string;
}

export interface JobSkillRequirement {
  id: number;
  skill: Skill;
  required_level: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  is_required: boolean;
  weight: number;
}

export interface Job {
  id: number;
  title: string;
  description: string;
  requirements: string;
  responsibilities: string;
  benefits?: string;
  salary_min?: number;
  salary_max?: number;
  job_type: 'full_time' | 'part_time' | 'internship' | 'contract';
  work_location: 'remote' | 'onsite' | 'hybrid';
  location?: string;
  experience_level: 'entry' | 'junior' | 'mid' | 'senior' | 'lead';
  education_requirement: 'high_school' | 'associate' | 'bachelor' | 'master' | 'phd';
  application_deadline?: string;
  is_active: boolean;
  is_featured: boolean;
  views_count: number;
  applications_count: number;
  created_at: string;
  updated_at: string;
  employer: EmployerProfile;
  category: JobCategory;
  skill_requirements: JobSkillRequirement[];
}

// 申请相关类型
export interface Application {
  id: number;
  student: number;
  job: number;
  status: 'pending' | 'reviewing' | 'interview' | 'accepted' | 'rejected' | 'withdrawn';
  applied_at: string;
  updated_at: string;
  cover_letter?: string;
  resume_url?: string;
  notes?: string;
}

export interface Interview {
  id: number;
  application: Application;
  interview_type: 'phone' | 'video' | 'onsite' | 'technical';
  scheduled_at: string;
  duration_minutes: number;
  location?: string;
  meeting_link?: string;
  notes?: string;
  status: 'scheduled' | 'completed' | 'cancelled' | 'rescheduled';
  feedback?: string;
}

export interface SavedJob {
  id: number;
  student: StudentProfile;
  job: Job;
  saved_at: string;
  notes?: string;
}

// 匹配相关类型
export interface SkillMatchDetail {
  id: number;
  skill: Skill;
  student_level: string;
  required_level: string;
  match_score: number;
  weight: number;
}

export interface MatchResult {
  id: number;
  student: StudentProfile;
  job: Job;
  overall_score: number;
  skill_score: number;
  experience_score: number;
  education_score: number;
  location_score: number;
  match_details: Record<string, any>;
  recommendation_reasons: string[];
  improvement_suggestions: string[];
  created_at: string;
  skill_matches: SkillMatchDetail[];
}

export interface RecommendationItem {
  id: number;
  item_type: 'job' | 'skill' | 'course' | 'certification';
  item_id: number;
  title: string;
  description: string;
  relevance_score: number;
  reasons: string[];
  metadata: Record<string, any>;
}

export interface StudentRecommendation {
  id: number;
  student: StudentProfile;
  recommendation_type: 'job' | 'skill' | 'career' | 'comprehensive';
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  is_active: boolean;
  expires_at: string;
  created_at: string;
  items: RecommendationItem[];
}

// API响应类型
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// 表单类型
export interface LoginForm {
  email: string;
  password: string;
}

export interface RegisterForm {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  password_confirm: string;
  user_type: 'student' | 'employer';
}

export interface JobSearchForm {
  search?: string;
  category?: number;
  job_type?: string;
  work_location?: string;
  experience_level?: string;
  salary_min?: number;
  salary_max?: number;
  location?: string;
}

export interface MatchRequest {
  student_id?: number;
  job_id?: number;
  limit?: number;
  min_score?: number;
  algorithm_config_id?: number;
}

// 统计类型
export interface MatchStatistics {
  total_matches: number;
  high_quality_matches: number;
  medium_quality_matches: number;
  low_quality_matches: number;
  average_score: number;
  matches_this_week: number;
  matches_this_month: number;
  top_skills: Array<{
    skill: string;
    match_count: number;
    average_score: number;
  }>;
  match_trends: Array<{
    date: string;
    count: number;
  }>;
}

export interface DashboardStats {
  total_applications?: number;
  pending_applications?: number;
  interview_invitations?: number;
  job_offers?: number;
  total_jobs?: number;
  active_jobs?: number;
  total_views?: number;
  total_applications_received?: number;
  profile_completion?: number;
  match_score?: number;
  saved_jobs?: number;
  total_students?: number;
  total_employers?: number;
  jobs_count?: number;
  applications_count?: number;
  views_count?: number;
  matches_count?: number;
  interviews_count?: number;
  profile_completeness?: number;
  recent_activities?: Array<{
    id: number;
    type: string;
    message: string;
    timestamp: string;
  }>;
}