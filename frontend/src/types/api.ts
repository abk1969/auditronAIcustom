export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}

export interface User {
  id: string;
  email: string;
  username: string;
  role: 'ADMIN' | 'USER' | 'ANALYST';
  is_active: boolean;
  is_verified: boolean;
  preferences: Record<string, any>;
  profile: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Analysis {
  id: string;
  user_id: string;
  repository_url?: string;
  repositoryName: string;
  code_snippet?: string;
  language: string;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  metrics: {
    [key: string]: any;
  };
  issues: Array<{
    type: string;
    severity: string;
    message: string;
    line?: number;
    column?: number;
    file?: string;
    code?: string;
    suggestion?: string;
  }>;
  suggestions: Array<{
    type: string;
    message: string;
    code?: string;
    impact?: string;
    effort?: string;
  }>;
  summary: string;
  lines_of_code: number;
  complexity_score: number;
  security_score: number;
  performance_score: number;
  created_at: string;
  updated_at: string;
}

export interface AnalysisStats {
  totalScans: number;
  issuesFound: number;
  issuesResolved: number;
  averageResolutionTime: string;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}

export interface Alert {
  id: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  timestamp: string;
  status: 'open' | 'in_progress' | 'resolved';
}

export interface PerformanceMetrics {
  cpu: {
    usage: number;
    cores: number;
  };
  memory: {
    total: number;
    used: number;
    free: number;
  };
  requests: {
    total: number;
    successful: number;
    failed: number;
    averageResponseTime: number;
  };
  timestamp: string;
}

export interface ApiError {
  response?: {
    data?: {
      message?: string;
      errors?: Record<string, string>;
    };
  };
  message: string;
}

export interface RiskData {
  id: string;
  probability: number;
  impact: number;
  category: string;
  description: string;
}
