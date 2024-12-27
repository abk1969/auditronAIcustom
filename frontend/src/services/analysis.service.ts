import api from './api';
import { ApiResponse, ApiArrayResponse, AnalysisStats, CodeAnalysis } from '../types/api';

export const analysisService = {
  getAnalysisStats: () => 
    api.get<ApiResponse<AnalysisStats>, AnalysisStats>('/analysis/stats'),

  getAnalysisHistory: (params: { startDate: string; endDate: string }) =>
    api.get<ApiArrayResponse<CodeAnalysis>, CodeAnalysis[]>('/analysis/history', { params }),
}; 