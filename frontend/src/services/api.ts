import axios, { AxiosInstance, AxiosResponse } from 'axios';
import {
  User,
  StudentProfile,
  EmployerProfile,
  Job,
  Application,
  MatchResult,
  StudentRecommendation,
  PaginatedResponse,
  LoginForm,
  RegisterForm,
  JobSearchForm,
  MatchRequest,
  MatchStatistics,
  DashboardStats,
} from '../types';

// 创建axios实例
const api: AxiosInstance = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加认证token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理token过期
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post('/users/token/refresh/', {
            refresh: refreshToken,
          });
          
          const { access } = response.data;
          localStorage.setItem('access_token', access);
          
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh token也过期了，清除token并跳转到登录页
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      } else {
        // 没有refresh token，跳转到登录页
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// 用户认证API
export const authAPI = {
  // 用户注册
  register: (data: RegisterForm): Promise<AxiosResponse<{ user: User; tokens: { access: string; refresh: string } }>> =>
    api.post('/users/register/', data),
  
  // 用户登录
  login: (data: LoginForm): Promise<AxiosResponse<{ user: User; tokens: { access: string; refresh: string } }>> =>
    api.post('/users/login/', data),
  
  // 用户登出
  logout: (): Promise<AxiosResponse<void>> =>
    api.post('/users/logout/'),
  
  // 获取当前用户信息
  getCurrentUser: (): Promise<AxiosResponse<User>> =>
    api.get('/users/profile/'),
  
  // 更新用户信息
  updateProfile: (data: Partial<User>): Promise<AxiosResponse<User>> =>
    api.patch('/users/profile/', data),
  
  // 修改密码
  changePassword: (data: { old_password: string; new_password: string }): Promise<AxiosResponse<void>> =>
    api.post('/users/change-password/', data),
  
  // 获取用户仪表板数据
  getDashboard: (): Promise<AxiosResponse<DashboardStats>> =>
    api.get('/users/dashboard/'),
};

// 学生档案API
export const studentAPI = {
  // 获取学生档案
  getProfile: (): Promise<AxiosResponse<StudentProfile>> =>
    api.get('/users/student-profile/'),
  
  // 更新学生档案
  updateProfile: (data: Partial<StudentProfile>): Promise<AxiosResponse<StudentProfile>> =>
    api.patch('/users/student-profile/', data),
  
  // 获取学生技能
  getSkills: (): Promise<AxiosResponse<StudentProfile['skills']>> =>
    api.get('/users/student-skills/'),
  
  // 添加技能
  addSkill: (data: { skill_id: number; proficiency_level: string; years_of_experience: number; is_primary: boolean }): Promise<AxiosResponse<StudentProfile['skills'][0]>> =>
    api.post('/users/student-skills/', data),
  
  // 更新技能
  updateSkill: (id: number, data: Partial<StudentProfile['skills'][0]>): Promise<AxiosResponse<StudentProfile['skills'][0]>> =>
    api.patch(`/users/student-skills/${id}/`, data),
  
  // 删除技能
  deleteSkill: (id: number): Promise<AxiosResponse<void>> =>
    api.delete(`/users/student-skills/${id}/`),
  
  // 获取项目经历
  getProjects: (): Promise<AxiosResponse<StudentProfile['projects']>> =>
    api.get('/users/student-projects/'),
  
  // 添加项目
  addProject: (data: Omit<StudentProfile['projects'][0], 'id'>): Promise<AxiosResponse<StudentProfile['projects'][0]>> =>
    api.post('/users/student-projects/', data),
  
  // 更新项目
  updateProject: (id: number, data: Partial<StudentProfile['projects'][0]>): Promise<AxiosResponse<StudentProfile['projects'][0]>> =>
    api.patch(`/users/student-projects/${id}/`, data),
  
  // 删除项目
  deleteProject: (id: number): Promise<AxiosResponse<void>> =>
    api.delete(`/users/student-projects/${id}/`),
};

// 雇主档案API
export const employerAPI = {
  // 获取雇主档案
  getProfile: (): Promise<AxiosResponse<EmployerProfile>> =>
    api.get('/users/employer-profile/'),
  
  // 更新雇主档案
  updateProfile: (data: Partial<EmployerProfile>): Promise<AxiosResponse<EmployerProfile>> =>
    api.patch('/users/employer-profile/', data),
};

// 职位API
export const jobAPI = {
  // 获取职位列表
  getJobs: (params?: JobSearchForm & { page?: number; page_size?: number }): Promise<AxiosResponse<PaginatedResponse<Job>>> =>
    api.get('/jobs/', { params }),
  
  // 获取职位详情
  getJob: (id: number): Promise<AxiosResponse<Job>> =>
    api.get(`/jobs/${id}/`),
  
  // 创建职位
  createJob: (data: Omit<Job, 'id' | 'employer' | 'created_at' | 'updated_at' | 'views_count' | 'applications_count'>): Promise<AxiosResponse<Job>> =>
    api.post('/jobs/', data),
  
  // 更新职位
  updateJob: (id: number, data: Partial<Job>): Promise<AxiosResponse<Job>> =>
    api.patch(`/jobs/${id}/`, data),
  
  // 删除职位
  deleteJob: (id: number): Promise<AxiosResponse<void>> =>
    api.delete(`/jobs/${id}/`),
  
  // 获取我发布的职位
  getMyJobs: (params?: { page?: number; page_size?: number }): Promise<AxiosResponse<PaginatedResponse<Job>>> =>
    api.get('/jobs/my-jobs/', { params }),
  
  // 申请职位
  applyJob: (id: number, data: { cover_letter?: string; resume?: File }): Promise<AxiosResponse<Application>> =>
    api.post(`/jobs/${id}/apply/`, data, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }),
  
  // 获取推荐职位
  getFeaturedJobs: (): Promise<AxiosResponse<Job[]>> =>
    api.get('/jobs/featured/'),
  
  // 获取最新职位
  getRecentJobs: (): Promise<AxiosResponse<Job[]>> =>
    api.get('/jobs/recent/'),
  
  // 获取职位统计
  getJobStatistics: (): Promise<AxiosResponse<any>> =>
    api.get('/jobs/statistics/'),
};

// 申请API
export const applicationAPI = {
  // 获取申请列表
  getApplications: (params?: { page?: number; page_size?: number; status?: string }): Promise<AxiosResponse<PaginatedResponse<Application>>> =>
    api.get('/applications/', { params }),
  
  // 获取申请详情
  getApplication: (id: number): Promise<AxiosResponse<Application>> =>
    api.get(`/applications/${id}/`),
  
  // 更新申请状态
  updateApplicationStatus: (id: number, data: { status: Application['status']; notes?: string }): Promise<AxiosResponse<Application>> =>
    api.patch(`/applications/${id}/`, data),
  
  // 批量更新申请状态
  bulkUpdateApplications: (data: { application_ids: number[]; status: Application['status']; notes?: string }): Promise<AxiosResponse<void>> =>
    api.post('/applications/bulk-update/', data),
  
  // 获取申请统计
  getApplicationStatistics: (): Promise<AxiosResponse<any>> =>
    api.get('/applications/statistics/'),
  
  // 获取即将到来的面试
  getUpcomingInterviews: (): Promise<AxiosResponse<any[]>> =>
    api.get('/applications/interviews/upcoming/'),
  
  // 获取收藏的职位
  getSavedJobs: (params?: { page?: number; page_size?: number }): Promise<AxiosResponse<PaginatedResponse<any>>> =>
    api.get('/applications/saved-jobs/', { params }),
  
  // 收藏职位
  saveJob: (data: { job_id: number; notes?: string }): Promise<AxiosResponse<any>> =>
    api.post('/applications/saved-jobs/', data),
  
  // 取消收藏职位
  unsaveJob: (id: number): Promise<AxiosResponse<void>> =>
    api.delete(`/applications/saved-jobs/${id}/`),
};

// 匹配API
export const matchingAPI = {
  // 获取匹配结果
  getMatchResults: (params?: { page?: number; page_size?: number; min_score?: number; job_id?: number; student_id?: number; ordering?: string }): Promise<AxiosResponse<PaginatedResponse<MatchResult>>> =>
    api.get('/matching/results/', { params }),
  
  // 获取匹配结果详情
  getMatchResult: (id: number): Promise<AxiosResponse<MatchResult>> =>
    api.get(`/matching/results/${id}/`),
  
  // 计算匹配度
  calculateMatch: (data: MatchRequest): Promise<AxiosResponse<{ results: MatchResult[]; count: number }>> =>
    api.post('/matching/calculate/', data),
  
  // 批量计算匹配度
  batchCalculateMatch: (data: { student_ids?: number[]; job_ids?: number[]; limit_per_item?: number; min_score?: number; priority?: string; algorithm_config_id?: number }): Promise<AxiosResponse<any>> =>
    api.post('/matching/batch-calculate/', data),
  
  // 获取学生推荐
  getRecommendations: (): Promise<AxiosResponse<StudentRecommendation[]>> =>
    api.get('/matching/recommendations/'),
  
  // 生成推荐
  generateRecommendations: (data: { type?: string }): Promise<AxiosResponse<{ recommendations: StudentRecommendation[]; count: number }>> =>
    api.post('/matching/recommendations/generate/', data),
  
  // 获取匹配统计
  getMatchStatistics: (): Promise<AxiosResponse<MatchStatistics>> =>
    api.get('/matching/statistics/'),
  
  // 获取推荐统计
  getRecommendationStatistics: (): Promise<AxiosResponse<any>> =>
    api.get('/matching/recommendations/statistics/'),
  
  // 获取匹配任务状态
  getMatchingJobStatus: (jobId: number): Promise<AxiosResponse<any>> =>
    api.get(`/matching/jobs/${jobId}/status/`),
};

// 通用API
export const commonAPI = {
  // 获取技能列表
  getSkills: (params?: { search?: string; category?: string }): Promise<AxiosResponse<any[]>> =>
    api.get('/users/skills/', { params }),
  
  // 获取职位分类
  getJobCategories: (): Promise<AxiosResponse<any[]>> =>
    api.get('/jobs/categories/'),
  
  // 文件上传
  uploadFile: (file: File, type: 'resume' | 'logo' | 'avatar'): Promise<AxiosResponse<{ url: string }>> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);
    
    return api.post('/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

export default api;