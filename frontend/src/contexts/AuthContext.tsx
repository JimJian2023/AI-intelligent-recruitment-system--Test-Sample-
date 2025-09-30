import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { User } from '../types';
import { authAPI } from '../services/api';

// 认证状态类型
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// 认证动作类型
type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: User }
  | { type: 'AUTH_FAILURE'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'CLEAR_ERROR' }
  | { type: 'UPDATE_USER'; payload: User };

// 初始状态
const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

// Reducer
const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'AUTH_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      };
    case 'AUTH_SUCCESS':
      return {
        ...state,
        user: action.payload,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };
    case 'AUTH_FAILURE':
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload,
      };
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      };
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };
    case 'UPDATE_USER':
      return {
        ...state,
        user: action.payload,
      };
    default:
      return state;
  }
};

// 认证上下文类型
interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (userData: {
    first_name: string;
    last_name: string;
    email: string;
    password: string;
    password_confirm: string;
    user_type: 'student' | 'employer';
  }) => Promise<void>;
  logout: () => void;
  updateUser: (userData: Partial<User>) => Promise<void>;
  clearError: () => void;
}

// 创建上下文
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// 认证提供者组件
interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // 检查用户是否已登录
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          dispatch({ type: 'AUTH_START' });
          const response = await authAPI.getCurrentUser();
          dispatch({ type: 'AUTH_SUCCESS', payload: response.data });
        } catch (error) {
          // Token无效，清除本地存储
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          dispatch({ type: 'AUTH_FAILURE', payload: '认证已过期，请重新登录' });
        }
      } else {
        dispatch({ type: 'AUTH_FAILURE', payload: '' });
      }
    };

    checkAuth();
  }, []);

  // 登录函数
  const login = async (email: string, password: string) => {
    try {
      dispatch({ type: 'AUTH_START' });
      const response = await authAPI.login({ email, password });
      const { user, tokens } = response.data;
      
      // 保存token到本地存储
      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);
      
      dispatch({ type: 'AUTH_SUCCESS', payload: user });
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || error.response?.data?.detail || '登录失败，请检查邮箱和密码';
      dispatch({ type: 'AUTH_FAILURE', payload: errorMessage });
      throw error;
    }
  };

  // 注册函数
  const register = async (userData: {
    first_name: string;
    last_name: string;
    email: string;
    password: string;
    password_confirm: string;
    user_type: 'student' | 'employer';
  }) => {
    try {
      dispatch({ type: 'AUTH_START' });
      const response = await authAPI.register(userData);
      const { user, tokens } = response.data;
      
      // 保存token到本地存储
      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);
      
      dispatch({ type: 'AUTH_SUCCESS', payload: user });
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || error.response?.data?.detail || '注册失败，请检查输入信息';
      dispatch({ type: 'AUTH_FAILURE', payload: errorMessage });
      throw error;
    }
  };

  // 登出函数
  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      // 即使登出API失败，也要清除本地状态
      console.error('Logout API failed:', error);
    } finally {
      // 清除本地存储
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      dispatch({ type: 'LOGOUT' });
    }
  };

  // 更新用户信息
  const updateUser = async (userData: Partial<User>) => {
    try {
      const response = await authAPI.updateProfile(userData);
      dispatch({ type: 'UPDATE_USER', payload: response.data });
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || error.response?.data?.detail || '更新用户信息失败';
      dispatch({ type: 'AUTH_FAILURE', payload: errorMessage });
      throw error;
    }
  };

  // 清除错误
  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  const value: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    updateUser,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// 使用认证上下文的Hook
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;