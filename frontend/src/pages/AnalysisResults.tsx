import React from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
} from '@mui/material';
import {
  Security as SecurityIcon,
  BugReport as BugReportIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';

const AnalysisResults: React.FC = () => {
  // Ces données devraient venir de l'API
  const analysisData = {
    score: 85,
    issues: [
      {
        severity: 'high',
        title: 'Injection SQL potentielle',
        description: 'Une vulnérabilité d\'injection SQL a été détectée dans la requête.',
        file: 'src/database/queries.js',
        line: 42,
      },
      {
        severity: 'medium',
        title: 'Mot de passe en clair',
        description: 'Un mot de passe est stocké en clair dans le code.',
        file: 'src/config/database.js',
        line: 15,
      },
      {
        severity: 'low',
        title: 'Console.log présent',
        description: 'Des instructions console.log sont présentes en production.',
        file: 'src/utils/logger.js',
        line: 23,
      },
    ],
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Résultats de l'Analyse
        </Typography>

        <Grid container spacing={3}>
          {/* Score global */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, textAlign: 'center' }}>
              <SecurityIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h4" gutterBottom>
                {analysisData.score}%
              </Typography>
              <Typography variant="subtitle1" color="textSecondary">
                Score de Sécurité
              </Typography>
              <LinearProgress
                variant="determinate"
                value={analysisData.score}
                sx={{ mt: 2, height: 8, borderRadius: 4 }}
              />
            </Paper>
          </Grid>

          {/* Statistiques */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Résumé des Problèmes
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <Box sx={{ textAlign: 'center' }}>
                    <BugReportIcon color="error" sx={{ fontSize: 32 }} />
                    <Typography variant="h6">2</Typography>
                    <Typography variant="body2" color="textSecondary">
                      Critiques
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={4}>
                  <Box sx={{ textAlign: 'center' }}>
                    <WarningIcon color="warning" sx={{ fontSize: 32 }} />
                    <Typography variant="h6">3</Typography>
                    <Typography variant="body2" color="textSecondary">
                      Moyens
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={4}>
                  <Box sx={{ textAlign: 'center' }}>
                    <CheckCircleIcon color="success" sx={{ fontSize: 32 }} />
                    <Typography variant="h6">5</Typography>
                    <Typography variant="body2" color="textSecondary">
                      Résolus
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* Liste des problèmes */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Problèmes Détectés
              </Typography>
              <List>
                {analysisData.issues.map((issue, index) => (
                  <ListItem
                    key={index}
                    sx={{
                      mb: 2,
                      border: 1,
                      borderColor: 'divider',
                      borderRadius: 1,
                    }}
                  >
                    <ListItemIcon>
                      {issue.severity === 'high' && <BugReportIcon color="error" />}
                      {issue.severity === 'medium' && <WarningIcon color="warning" />}
                      {issue.severity === 'low' && <CheckCircleIcon color="info" />}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {issue.title}
                          <Chip
                            label={issue.severity}
                            size="small"
                            color={getSeverityColor(issue.severity) as any}
                          />
                        </Box>
                      }
                      secondary={
                        <>
                          <Typography variant="body2" component="span" display="block">
                            {issue.description}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            {issue.file}:{issue.line}
                          </Typography>
                        </>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default AnalysisResults; 