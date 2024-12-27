import { useState, useEffect } from 'react';
import { AnalysisStats, Alert } from '../types/api';
import api from '../services/api';

interface DashboardData {
  analysisStats: AnalysisStats;
  alerts: Alert[];
  globalScore: number;
  isLoading: boolean;
  error: Error | null;
}

export const useDashboard = () => {
  const [data, setData] = useState<DashboardData>({
    analysisStats: {
      totalScans: 0,
      issuesFound: 0,
      issuesResolved: 0,
      averageResolutionTime: '0 days'
    },
    alerts: [],
    globalScore: 0,
    isLoading: true,
    error: null
  });

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [analysisStatsResponse, alertsResponse] = await Promise.all([
          api.get('/analysis/stats').then(res => res.data.data),
          api.get('/alerts').then(res => res.data.data)
        ]);

        const calculateGlobalScore = (stats: AnalysisStats): number => {
          if (stats.issuesFound === 0) return 100;
          const resolutionRate = (stats.issuesResolved / stats.issuesFound) * 100;
          return Math.round(resolutionRate);
        };

        setData({
          analysisStats: analysisStatsResponse,
          alerts: alertsResponse,
          globalScore: calculateGlobalScore(analysisStatsResponse),
          isLoading: false,
          error: null
        });
      } catch (error) {
        setData(prev => ({
          ...prev,
          isLoading: false,
          error: error as Error
        }));
      }
    };

    fetchDashboardData();
  }, []);

  return data;
}; 