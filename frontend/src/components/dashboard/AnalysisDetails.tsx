import React from 'react';
import { Box, Paper, Typography, Chip, Grid, List, ListItem, ListItemText, ListItemIcon } from '@mui/material';
import { Security, BugReport, Speed, Code } from '@mui/icons-material';
import { Analysis } from '../../types/api';

interface AnalysisDetailsProps {
  analysis: Analysis;
}

export const AnalysisDetails: React.FC<AnalysisDetailsProps> = ({ analysis }) => {
  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'error';
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
    <Box>
      <Typography variant="h5" gutterBottom>
        Résultats de l'Analyse
      </Typography>

      <Grid container spacing={3}>
        {/* Métriques */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Métriques
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={3}>
                <Typography variant="subtitle2">Lignes de code</Typography>
                <Typography variant="h6">{analysis.lines_of_code}</Typography>
              </Grid>
              <Grid item xs={3}>
                <Typography variant="subtitle2">Score de Sécurité</Typography>
                <Typography variant="h6">{analysis.security_score}/10</Typography>
              </Grid>
              <Grid item xs={3}>
                <Typography variant="subtitle2">Score de Complexité</Typography>
                <Typography variant="h6">{analysis.complexity_score}/10</Typography>
              </Grid>
              <Grid item xs={3}>
                <Typography variant="subtitle2">Score de Performance</Typography>
                <Typography variant="h6">{analysis.performance_score}/10</Typography>
              </Grid>
              <Grid item xs={3}>
                <Typography variant="subtitle2">Score de Qualité</Typography>
                <Typography variant="h6">{(analysis.quality_score * 10).toFixed(1)}/10</Typography>
              </Grid>
              <Grid item xs={3}>
                <Typography variant="subtitle2">Score Global</Typography>
                <Typography variant="h6">{(analysis.global_score * 10).toFixed(1)}/10</Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Métriques de Qualité */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Métriques de Qualité
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={4}>
                <Typography variant="subtitle2">Complexité Cyclomatique</Typography>
                <Typography variant="h6">{analysis.metrics.complexity || 0}</Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography variant="subtitle2">Duplications</Typography>
                <Typography variant="h6">{analysis.metrics.duplications || 0}</Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography variant="subtitle2">Ratio de Commentaires</Typography>
                <Typography variant="h6">{((analysis.metrics.comment_ratio || 0) * 100).toFixed(1)}%</Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Vulnérabilités */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Vulnérabilités Détectées
            </Typography>
            <List>
              {analysis.issues.map((issue, index) => (
                <ListItem key={index} sx={{ mb: 2 }}>
                  <ListItemIcon>
                    {issue.type === 'security' ? <Security /> : <BugReport />}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {issue.message}
                        <Chip
                          label={issue.severity}
                          color={getSeverityColor(issue.severity)}
                          size="small"
                        />
                      </Box>
                    }
                    secondary={
                      <div>
                        <div>
                          <span style={{ color: 'rgba(0, 0, 0, 0.6)' }}>
                            Fichier: {issue.file}, Ligne: {issue.line}
                          </span>
                        </div>
                        <div style={{ 
                          marginTop: '8px',
                          padding: '8px',
                          backgroundColor: 'rgba(0, 0, 0, 0.05)',
                          borderRadius: '4px'
                        }}>
                          <code>{issue.code}</code>
                        </div>
                        {issue.suggestion && (
                          <div style={{ marginTop: '8px', color: '#1976d2' }}>
                            Suggestion: {issue.suggestion}
                          </div>
                        )}
                      </div>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        {/* Suggestions d'amélioration */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Suggestions d'Amélioration
            </Typography>
            <List>
              {analysis.suggestions.map((suggestion, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <Code />
                  </ListItemIcon>
                  <ListItemText
                    primary={suggestion.message}
                    secondary={
                      <div style={{ marginTop: '8px' }}>
                        {suggestion.code && (
                          <div style={{ 
                            marginTop: '8px',
                            padding: '8px',
                            backgroundColor: 'rgba(0, 0, 0, 0.05)',
                            borderRadius: '4px'
                          }}>
                            <code>{suggestion.code}</code>
                          </div>
                        )}
                        <div style={{ 
                          marginTop: '8px',
                          display: 'flex',
                          gap: '16px'
                        }}>
                          {suggestion.impact && (
                            <div style={{ color: 'rgba(0, 0, 0, 0.6)' }}>
                              Impact: {suggestion.impact}
                            </div>
                          )}
                          {suggestion.effort && (
                            <div style={{ color: 'rgba(0, 0, 0, 0.6)' }}>
                              Effort: {suggestion.effort}
                            </div>
                          )}
                        </div>
                      </div>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};
