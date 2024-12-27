import { http, HttpResponse } from 'msw';
import { ApiResponse, AnalysisStats, Analysis, Alert, PerformanceMetrics } from '../types/api';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export const handlers = [
  // Authentification
  http.post(`${API_URL}/auth/login`, () => {
    return HttpResponse.json({
      data: {
        accessToken: 'mock-access-token',
        refreshToken: 'mock-refresh-token',
      },
      message: 'Connexion réussie',
    });
  }),

  // Analyses
  http.get(`${API_URL}/analysis/stats`, () => {
    const response: ApiResponse<AnalysisStats> = {
      data: {
        totalAnalyses: 150,
        issuesByType: {
          security: 42,
          performance: 28,
          quality: 35,
          resolved: 128,
        },
        issuesBySeverity: {
          low: 45,
          medium: 35,
          high: 20,
          critical: 5,
        },
        averageIssuesPerAnalysis: 3.5,
        topIssues: [
          {
            ruleId: 'SEC001',
            count: 15,
            type: 'security',
            severity: 'high',
          },
        ],
      },
    };
    return HttpResponse.json(response);
  }),

  http.get(`${API_URL}/analysis/history`, () => {
    const response: ApiResponse<Analysis[]> = {
      data: Array.from({ length: 10 }, (_, i) => ({
        id: `analysis-${i}`,
        user_id: '1',
        status: i % 2 === 0 ? 'COMPLETED' : 'PENDING',
        language: 'python',
        metrics: {},
        issues: [],
        suggestions: [],
        lines_of_code: 100,
        complexity_score: 5,
        security_score: 8,
        performance_score: 7,
        created_at: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString(),
      })),
    };
    return HttpResponse.json(response);
  }),

  // Monitoring
  http.get(`${API_URL}/monitoring/performance`, () => {
    const response: ApiResponse<PerformanceMetrics> = {
      data: {
        cpu: {
          usage: 45,
          cores: 8,
        },
        memory: {
          total: 16384,
          used: 8192,
          free: 8192,
        },
        requests: {
          total: 1000,
          successful: 950,
          failed: 50,
          averageResponseTime: 250,
        },
        timestamp: new Date().toISOString(),
      },
    };
    return HttpResponse.json(response);
  }),

  http.get(`${API_URL}/monitoring/alerts`, () => {
    const response: ApiResponse<Alert[]> = {
      data: Array.from({ length: 5 }, (_, i) => ({
        id: `alert-${i}`,
        type: i % 2 === 0 ? 'error' : 'warning',
        message: `Alert message ${i}`,
        source: 'system',
        timestamp: new Date(Date.now() - i * 60 * 60 * 1000).toISOString(),
        acknowledged: false,
        resolved: false,
      })),
    };
    return HttpResponse.json(response);
  }),
];
