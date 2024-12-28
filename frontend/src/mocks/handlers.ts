import { http, HttpResponse } from 'msw';
import { ApiResponse, AnalysisStats, Analysis, Alert, PerformanceMetrics } from '../types/api';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export const handlers = [
  // Authentification
  http.post(`${API_URL}/auth/login`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        accessToken: 'mock-access-token',
        refreshToken: 'mock-refresh-token',
      },
      message: 'Connexion réussie',
    });
  }),

  // Analyses
  // Upload handlers
  http.post(`${API_URL}/analysis/upload`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        id: 'mock-analysis-id',
      },
      message: 'Code uploadé avec succès',
    });
  }),

  http.post(`${API_URL}/analysis/repository`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        id: 'mock-analysis-id',
      },
      message: 'Dépôt Git ajouté avec succès',
    });
  }),

  http.get(`${API_URL}/analysis/stats`, () => {
    const response: ApiResponse<AnalysisStats> = {
      success: true,
      data: {
        totalScans: 150,
        issuesFound: 42,
        issuesResolved: 128,
        averageResolutionTime: '3.5 days',
      },
    };
    return HttpResponse.json(response);
  }),

  http.get(`${API_URL}/analysis/history`, () => {
    const response: ApiResponse<Analysis[]> = {
      success: true,
      data: Array.from({ length: 10 }, (_, i) => ({
        id: `analysis-${i}`,
        user_id: '1',
        status: i % 2 === 0 ? 'COMPLETED' : 'PENDING',
        language: 'python',
        repositoryName: `analysis-${i}.py`,
        metrics: {
          complexity: 5,
          duplications: 2,
          comment_ratio: 0.15
        },
        quality_score: 0.75,
        global_score: 0.8,
        issues: [],
        suggestions: [],
        summary: '',
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
      success: true,
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

  // Récupérer une analyse spécifique
  http.get(`${API_URL}/analysis/:id`, () => {
    const response: ApiResponse<Analysis> = {
      success: true,
      data: {
        id: 'mock-analysis-id',
        user_id: '1',
        status: 'COMPLETED',
        language: 'python',
        repositoryName: 'sample.py',
        summary: 'Analyse complète du fichier sample.py : 3 vulnérabilités de sécurité détectées (2 high, 1 critical) et 2 problèmes de qualité de code',
        metrics: {
          'Lignes de code': 45,
          'Fonctions': 5,
          'Classes': 1,
          'Complexité cyclomatique moyenne': 4.2,
          complexity: 4.2,
          duplications: 1,
          comment_ratio: 0.2
        },
        quality_score: 0.85,
        global_score: 0.7,
        issues: [
          {
            type: 'security',
            severity: 'high',
            message: 'Utilisation non sécurisée de os.system()',
            line: 5,
            file: 'sample.py',
            code: 'os.system(cmd)',
            suggestion: 'Utilisez subprocess.run() avec shell=False'
          },
          {
            type: 'security',
            severity: 'critical',
            message: 'Désérialisation non sécurisée avec pickle',
            line: 10,
            file: 'sample.py',
            code: 'pickle.loads(data)',
            suggestion: 'Évitez d\'utiliser pickle avec des données non fiables'
          },
          {
            type: 'security',
            severity: 'high',
            message: 'Vulnérabilité d\'injection SQL potentielle',
            line: 15,
            file: 'sample.py',
            code: 'f"SELECT * FROM users WHERE id = {user_input}"',
            suggestion: 'Utilisez des requêtes paramétrées'
          }
        ],
        suggestions: [
          {
            type: 'quality',
            message: 'Complexité cyclomatique élevée dans process_data',
            code: 'class ComplexClass',
            impact: 'Maintenabilité réduite',
            effort: 'Moyen'
          },
          {
            type: 'quality',
            message: 'Code mort détecté',
            code: 'unused_function',
            impact: 'Confusion dans le code',
            effort: 'Faible'
          }
        ],
        lines_of_code: 45,
        complexity_score: 4.2,
        security_score: 3.5,
        performance_score: 7.8,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    };
    return HttpResponse.json(response);
  }),

  http.get(`${API_URL}/monitoring/alerts`, () => {
    const response: ApiResponse<Alert[]> = {
      success: true,
      data: Array.from({ length: 5 }, (_, i) => ({
        id: `alert-${i}`,
        severity: i % 2 === 0 ? 'high' : 'medium',
        title: `Alert ${i}`,
        description: `Alert message ${i}`,
        timestamp: new Date(Date.now() - i * 60 * 60 * 1000).toISOString(),
        status: 'open',
      })),
    };
    return HttpResponse.json(response);
  }),
];
