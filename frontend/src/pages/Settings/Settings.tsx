"""Page des paramètres."""
import React from 'react';
import { Box, Grid, Paper, Typography } from '@mui/material';
import { useQuery } from 'react-query';

import { GeneralSettings } from './components/GeneralSettings';
import { AISettings } from './components/AISettings';
import { BackupSettings } from './components/BackupSettings';
import { SecuritySettings } from './components/SecuritySettings';
import { fetchSettings } from '../../services/api';

export const Settings: React.FC = () => {
  const { data, isLoading } = useQuery('settings', fetchSettings);

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Paramètres
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Paramètres Généraux
            </Typography>
            <GeneralSettings
              settings={data?.general}
              isLoading={isLoading}
            />
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Configuration IA
            </Typography>
            <AISettings
              settings={data?.ai}
              isLoading={isLoading}
            />
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Sauvegardes
            </Typography>
            <BackupSettings
              settings={data?.backup}
              isLoading={isLoading}
            />
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Sécurité
            </Typography>
            <SecuritySettings
              settings={data?.security}
              isLoading={isLoading}
            />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}; 