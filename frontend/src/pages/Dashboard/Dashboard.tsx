"""Page du tableau de bord."""
import React from 'react';
import { Grid, Paper, Typography, Box } from '@mui/material';
import { useQuery } from 'react-query';

import { MetricsChart } from './components/MetricsChart';
import { RecentAnalyses } from './components/RecentAnalyses';
import { SystemStatus } from './components/SystemStatus';
import { fetchDashboardData } from '../../services/api';

export const Dashboard: React.FC = () => {
  const { data, isLoading } = useQuery('dashboardData', fetchDashboardData);

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Tableau de Bord
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Métriques de Performance
            </Typography>
            <MetricsChart
              data={data?.metrics}
              isLoading={isLoading}
            />
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              État du Système
            </Typography>
            <SystemStatus
              status={data?.systemStatus}
              isLoading={isLoading}
            />
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Analyses Récentes
            </Typography>
            <RecentAnalyses
              analyses={data?.recentAnalyses}
              isLoading={isLoading}
            />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}; 