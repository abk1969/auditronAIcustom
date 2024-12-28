import React from 'react';
import { Box, Grid, Paper, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { AnalyticsChart } from '../components/dashboard/AnalyticsChart';
import { MetricsOverview } from '../components/dashboard/MetricsOverview';
import { AuditTimeline } from '../components/dashboard/AuditTimeline';
import { RiskMatrix } from '../components/dashboard/RiskMatrix';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight="bold">
          Tableau de Bord AuditronAI
        </Typography>
        <Button
          variant="contained"
          color="primary"
          size="large"
          onClick={() => navigate('/analyze')}
        >
          Nouvelle Analyse
        </Button>
      </Box>

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