"""Page de monitoring."""
import React from 'react';
import { Grid, Paper, Typography, Box } from '@mui/material';
import { useQuery } from 'react-query';

import { PerformanceMetrics } from './components/PerformanceMetrics';
import { ResourceUsage } from './components/ResourceUsage';
import { AlertsTimeline } from './components/AlertsTimeline';
import { fetchMonitoringData } from '../../services/api';

export const Monitoring: React.FC = () => {
  const { data, isLoading } = useQuery(
    'monitoringData',
    fetchMonitoringData,
    { refetchInterval: 30000 } // Rafraîchir toutes les 30 secondes
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Monitoring
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Performance Globale
            </Typography>
            <PerformanceMetrics
              data={data?.performance}
              isLoading={isLoading}
            />
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Utilisation des Ressources
            </Typography>
            <ResourceUsage
              data={data?.resources}
              isLoading={isLoading}
            />
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Alertes Récentes
            </Typography>
            <AlertsTimeline
              alerts={data?.alerts}
              isLoading={isLoading}
            />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}; 