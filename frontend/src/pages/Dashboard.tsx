import React from 'react';
import { Box, Grid, Paper, Typography } from '@mui/material';
import { AnalyticsChart } from '../components/dashboard/AnalyticsChart';
import { MetricsOverview } from '../components/dashboard/MetricsOverview';
import { AuditTimeline } from '../components/dashboard/AuditTimeline';
import { RiskMatrix } from '../components/dashboard/RiskMatrix';

const Dashboard: React.FC = () => {
  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom fontWeight="bold">
        Tableau de Bord AuditronAI
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <MetricsOverview />
        </Grid>

        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: '400px' }}>
            <AnalyticsChart />
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '400px' }}>
            <AuditTimeline />
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3, height: '400px' }}>
            <RiskMatrix />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard; 