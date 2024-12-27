import React from 'react';
import { Grid, Paper, Typography, Box } from '@mui/material';
import { SecurityOutlined, BugReport, CheckCircleOutline, AccessTimeOutlined } from '@mui/icons-material';
import { useDashboard } from '../../hooks/useDashboard';

export const MetricsOverview: React.FC = () => {
  const { analysisStats, globalScore, isLoading } = useDashboard();

  const metrics = [
    {
      title: 'Score Global',
      value: `${globalScore}%`,
      icon: <SecurityOutlined sx={{ fontSize: 40, color: 'primary.main' }} />,
    },
    {
      title: 'Analyses Totales',
      value: analysisStats.totalScans,
      icon: <SecurityOutlined sx={{ fontSize: 40, color: 'info.main' }} />,
    },
    {
      title: 'Problèmes Détectés',
      value: analysisStats.issuesFound,
      icon: <BugReport sx={{ fontSize: 40, color: 'warning.main' }} />,
    },
    {
      title: 'Problèmes Résolus',
      value: analysisStats.issuesResolved,
      icon: <CheckCircleOutline sx={{ fontSize: 40, color: 'success.main' }} />,
    },
  ];

  if (isLoading) {
    return <div>Chargement...</div>;
  }

  return (
    <Grid container spacing={3}>
      {metrics.map((metric, index) => (
        <Grid item xs={12} sm={6} md={3} key={index}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              height: 140,
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            <Box
              sx={{
                position: 'absolute',
                top: -10,
                right: -10,
                opacity: 0.1,
                transform: 'rotate(15deg)',
              }}
            >
              {metric.icon}
            </Box>
            <Typography variant="h6" color="textSecondary" gutterBottom>
              {metric.title}
            </Typography>
            <Typography variant="h4" component="div">
              {metric.value}
            </Typography>
          </Paper>
        </Grid>
      ))}
    </Grid>
  );
}; 