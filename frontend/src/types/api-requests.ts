import type { InternalAxiosRequestConfig } from 'axios';

declare module 'axios' {
  interface InternalAxiosRequestConfig {
    _retry?: boolean;
  }
}

export interface ApiError {
  response?: {
    data?: {
      message?: string;
      errors?: Record<string, string>;
    };
    status?: number;
  };
  message: string;
}

export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
}

export interface UpdateProfileRequest {
  firstName?: string;
  lastName?: string;
  email?: string;
  currentPassword?: string;
  newPassword?: string;
}

export interface AnalysisRequest {
  code: string;
  language: string;
  options?: {
    rules?: string[];
    severity?: string[];
    ignorePatterns?: string[];
  };
}

export interface AnalysisFilters {
  startDate?: string;
  endDate?: string;
  language?: string;
  severity?: string[];
  type?: string[];
  status?: string[];
}

export interface MonitoringFilters {
  timeRange: string;
  metrics?: string[];
  aggregation?: 'sum' | 'avg' | 'max' | 'min';
}

export interface AlertFilters {
  type?: ('error' | 'warning' | 'info')[];
  status?: ('active' | 'acknowledged' | 'resolved')[];
  startDate?: string;
  endDate?: string;
  source?: string[];
}

export interface UpdateSettingsRequest {
  theme?: 'light' | 'dark' | 'system';
  language?: string;
  notifications?: {
    email?: boolean;
    push?: boolean;
    desktop?: boolean;
  };
  dashboard?: {
    refreshInterval?: number;
    defaultTimeRange?: string;
  };
}

export interface UpdateAISettingsRequest {
  model?: string;
  temperature?: number;
  maxTokens?: number;
  apiKey?: string;
  provider?: 'openai' | 'azure' | 'custom';
  endpoint?: string;
  customHeaders?: Record<string, string>;
} 