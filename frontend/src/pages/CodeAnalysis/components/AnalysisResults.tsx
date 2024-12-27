"""Composant d'affichage des résultats d'analyse."""
import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  CircularProgress,
  Chip,
  IconButton,
  Tooltip,
  Alert
} from '@mui/material';
import {
  BugReport as BugIcon,
  Security as SecurityIcon,
  Speed as SpeedIcon,
  Download as DownloadIcon,
  Share as ShareIcon
} from '@mui/icons-material';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div role="tabpanel" hidden={value !== index}>
    {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
  </div>
);

interface AnalysisResult {
  issues: Array<{
    type: 'error' | 'warning' | 'info';
    message: string;
    line: number;
    file: string;
    code: string;
  }>;
  metrics: {
    complexity: number;
    maintainability: number;
    testCoverage: number;
    performance: number;
  };
  suggestions: Array<{
    type: 'optimization' | 'security' | 'quality';
    description: string;
    impact: 'high' | 'medium' | 'low';
  }>;
}

interface AnalysisResultsProps {
  results?: AnalysisResult;
  isLoading?: boolean;
  onExport?: () => void;
  onShare?: () => void;
}

export const AnalysisResults: React.FC<AnalysisResultsProps> = ({
  results,
  isLoading,
  onExport,
  onShare
}) => {
  const [tabValue, setTabValue] = React.useState(0);

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!results) {
    return (
      <Alert severity="info">
        Lancez une analyse pour voir les résultats
      </Alert>
    );
  }

  const getSeverityColor = (type: string) => {
    switch (type) {
      case 'error': return 'error';
      case 'warning': return 'warning';
      case 'info': return 'info';
      default: return 'default';
    }
  };

  return (
    <Paper sx={{ mt: 3 }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider', p: 2, display: 'flex', justifyContent: 'space-between' }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab 
            icon={<BugIcon />} 
            label={`Problèmes (${results.issues.length})`}
            iconPosition="start"
          />
          <Tab 
            icon={<SpeedIcon />}
            label="Métriques"
            iconPosition="start"
          />
          <Tab 
            icon={<SecurityIcon />}
            label={`Suggestions (${results.suggestions.length})`}
            iconPosition="start"
          />
        </Tabs>
        <Box>
          <Tooltip title="Exporter les résultats">
            <IconButton onClick={onExport}>
              <DownloadIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Partager l'analyse">
            <IconButton onClick={onShare}>
              <ShareIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {results.issues.map((issue, index) => (
            <Paper key={index} variant="outlined" sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                <Typography variant="subtitle1">
                  {issue.file}:{issue.line}
                </Typography>
                <Chip
                  size="small"
                  label={issue.type}
                  color={getSeverityColor(issue.type)}
                />
              </Box>
              <Typography>{issue.message}</Typography>
              <Box
                component="pre"
                sx={{
                  mt: 1,
                  p: 1,
                  bgcolor: 'grey.900',
                  borderRadius: 1,
                  overflow: 'auto'
                }}
              >
                <code>{issue.code}</code>
              </Box>
            </Paper>
          ))}
        </Box>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 3 }}>
          <Paper variant="outlined" sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Complexité Cyclomatique
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <CircularProgress
                variant="determinate"
                value={Math.min(results.metrics.complexity / 10 * 100, 100)}
                size={60}
                color={results.metrics.complexity > 7 ? 'error' : 'success'}
              />
              <Box>
                <Typography variant="h4">
                  {results.metrics.complexity}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {results.metrics.complexity <= 5 ? 'Excellent' : 
                   results.metrics.complexity <= 7 ? 'Bon' : 'À améliorer'}
                </Typography>
              </Box>
            </Box>
          </Paper>

          <Paper variant="outlined" sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Maintenabilité
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <CircularProgress
                variant="determinate"
                value={results.metrics.maintainability}
                size={60}
                color={results.metrics.maintainability < 70 ? 'warning' : 'success'}
              />
              <Box>
                <Typography variant="h4">
                  {results.metrics.maintainability}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {results.metrics.maintainability >= 80 ? 'Très bon' : 
                   results.metrics.maintainability >= 70 ? 'Acceptable' : 'À améliorer'}
                </Typography>
              </Box>
            </Box>
          </Paper>

          <Paper variant="outlined" sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Couverture de Tests
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <CircularProgress
                variant="determinate"
                value={results.metrics.testCoverage}
                size={60}
                color={results.metrics.testCoverage < 80 ? 'warning' : 'success'}
              />
              <Box>
                <Typography variant="h4">
                  {results.metrics.testCoverage}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {results.metrics.testCoverage >= 90 ? 'Excellent' : 
                   results.metrics.testCoverage >= 80 ? 'Bon' : 'Insuffisant'}
                </Typography>
              </Box>
            </Box>
          </Paper>

          <Paper variant="outlined" sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Performance
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <CircularProgress
                variant="determinate"
                value={results.metrics.performance}
                size={60}
                color={results.metrics.performance < 75 ? 'warning' : 'success'}
              />
              <Box>
                <Typography variant="h4">
                  {results.metrics.performance}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {results.metrics.performance >= 90 ? 'Optimal' : 
                   results.metrics.performance >= 75 ? 'Bon' : 'À optimiser'}
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Box>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {results.suggestions.map((suggestion, index) => (
            <Paper key={index} variant="outlined" sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {suggestion.type === 'security' ? (
                    <SecurityIcon color="error" />
                  ) : suggestion.type === 'optimization' ? (
                    <SpeedIcon color="warning" />
                  ) : (
                    <BugIcon color="info" />
                  )}
                  <Typography variant="subtitle1">
                    {suggestion.type.charAt(0).toUpperCase() + suggestion.type.slice(1)}
                  </Typography>
                </Box>
                <Chip
                  size="small"
                  label={suggestion.impact}
                  color={
                    suggestion.impact === 'high' ? 'error' :
                    suggestion.impact === 'medium' ? 'warning' : 'info'
                  }
                />
              </Box>
              <Typography>{suggestion.description}</Typography>
            </Paper>
          ))}
        </Box>
      </TabPanel>
    </Paper>
  );
}; 