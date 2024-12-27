import api from './api';

export interface AuditConfig {
  projectName: string;
  scope: string[];
  rules: string[];
  priority: 'low' | 'medium' | 'high';
  customRules?: Record<string, any>;
}

export interface AuditResult {
  id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  findings: Array<{
    id: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    category: string;
    description: string;
    location: string;
    recommendation: string;
    risk: string;
  }>;
  summary: {
    totalIssues: number;
    criticalIssues: number;
    highIssues: number;
    mediumIssues: number;
    lowIssues: number;
    score: number;
  };
  startedAt: string;
  completedAt?: string;
  error?: string;
}

class AuditService {
  async startAudit(config: AuditConfig): Promise<{ auditId: string }> {
    const response = await api.post<{ auditId: string }>('/audits/start', config);
    return response.data;
  }

  async getAuditStatus(auditId: string): Promise<AuditResult> {
    const response = await api.get<AuditResult>(`/audits/${auditId}/status`);
    return response.data;
  }

  async getAuditResults(auditId: string): Promise<AuditResult> {
    const response = await api.get<AuditResult>(`/audits/${auditId}/results`);
    return response.data;
  }

  async getAllAudits(filters?: {
    status?: string[];
    dateFrom?: string;
    dateTo?: string;
    priority?: string[];
  }): Promise<AuditResult[]> {
    const response = await api.get<AuditResult[]>('/audits', { params: filters });
    return response.data;
  }

  async cancelAudit(auditId: string): Promise<void> {
    await api.post(`/audits/${auditId}/cancel`);
  }

  async deleteAudit(auditId: string): Promise<void> {
    await api.delete(`/audits/${auditId}`);
  }

  async updateAuditNotes(auditId: string, notes: string): Promise<void> {
    await api.patch(`/audits/${auditId}/notes`, { notes });
  }

  async exportAuditReport(auditId: string, format: 'pdf' | 'csv' | 'json'): Promise<Blob> {
    const response = await api.get(`/audits/${auditId}/export`, {
      responseType: 'blob',
      params: { format },
    });
    return response.data;
  }

  async getAuditMetrics(timeRange: 'day' | 'week' | 'month' | 'year'): Promise<{
    totalAudits: number;
    completedAudits: number;
    averageScore: number;
    issuesByPriority: Record<string, number>;
    trendsOverTime: Array<{
      date: string;
      audits: number;
      issues: number;
    }>;
  }> {
    const response = await api.get('/audits/metrics', { params: { timeRange } });
    return response.data;
  }
}

export const auditService = new AuditService(); 