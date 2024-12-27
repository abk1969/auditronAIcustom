import { http } from 'msw';
import { ApiResponse, AnalysisStats, CodeAnalysis, Alert, PerformanceMetrics, AuthTokens, User } from '../types/api';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export const handlers = [
  // Auth endpoints
  http.post(`${API_URL}/auth/login`, async () => {
    const response: ApiResponse<{ token: string; user: User }> = {
      data: {
        token: 'mock-jwt-token',
        user: {
          id: '1',
          email: 'test@example.com',
          name: 'Test User',
          role: 'user',
          preferences: {
            theme: 'light',
            notifications: true,
            language: 'fr'
          }
        }
      },
      status: 'success'
    };
    return new Response(JSON.stringify(response), { status: 200 });
  }),

  http.post(`${API_URL}/auth/register`, async () => {
    const response: ApiResponse<{ token: string; user: User }> = {
      data: {
        token: 'mock-jwt-token',
        user: {
          id: '1',
          email: 'test@example.com',
          name: 'Test User',
          role: 'user',
          preferences: {
            theme: 'light',
            notifications: true,
            language: 'fr'
          }
        }
      },
      status: 'success'
    };
    return new Response(JSON.stringify(response), { status: 200 });
  }),

  // Analysis endpoints
  http.get(`${API_URL}/analysis/stats`, async () => {
    const mockStats: ApiResponse<AnalysisStats> = {
      data: {
        totalScans: 100,
        issuesFound: 50,
        issuesResolved: 30,
        averageResolutionTime: '2 days'
      },
      status: 'success'
    };
    return new Response(JSON.stringify(mockStats), { status: 200 });
  }),

  http.get(`${API_URL}/analysis/latest`, async () => {
    const mockAnalysis: ApiResponse<CodeAnalysis[]> = {
      data: [
        {
          id: '1',
          repositoryName: 'example-repo',
          branch: 'main',
          status: 'completed',
          issuesCount: 5,
          timestamp: new Date().toISOString(),
          summary: 'Found 5 potential security issues'
        }
      ],
      status: 'success'
    };
    return new Response(JSON.stringify(mockAnalysis), { status: 200 });
  }),

  // Alerts endpoints
  http.get(`${API_URL}/alerts`, async () => {
    const mockAlerts: ApiResponse<Alert[]> = {
      data: [
        {
          id: '1',
          severity: 'high',
          message: 'Critical security vulnerability detected',
          timestamp: new Date().toISOString(),
          status: 'open'
        }
      ],
      status: 'success'
    };
    return new Response(JSON.stringify(mockAlerts), { status: 200 });
  }),

  // Performance endpoints
  http.get(`${API_URL}/performance/metrics`, async () => {
    const mockMetrics: ApiResponse<PerformanceMetrics> = {
      data: {
        scanDuration: {
          average: 120,
          min: 60,
          max: 180
        },
        resourceUsage: {
          cpu: 45,
          memory: 75
        },
        throughput: {
          scansPerHour: 10,
          filesProcessed: 1000
        }
      },
      status: 'success'
    };
    return new Response(JSON.stringify(mockMetrics), { status: 200 });
  })
]; 