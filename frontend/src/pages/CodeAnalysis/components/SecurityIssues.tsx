"""Composant d'analyse des problèmes de sécurité."""
import React from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Collapse,
  Button,
  Alert,
  LinearProgress,
  Grid,
  Tooltip,
  IconButton
} from '@mui/material';
import {
  Security as SecurityIcon,
  Warning as WarningIcon,
  BugReport as VulnerabilityIcon,
  Shield as ShieldIcon,
  Link as DependencyIcon,
  Visibility as ViewIcon,
  ExpandMore,
  ExpandLess,
  GetApp as DownloadIcon
} from '@mui/icons-material';

interface SecurityVulnerability {
  id: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  type: 'injection' | 'authentication' | 'exposure' | 'configuration' | 'dependency';
  title: string;
  description: string;
  impact: string;
  remediation: string;
  cwe?: string; // Common Weakness Enumeration ID
  cvss?: number; // Common Vulnerability Scoring System
  affectedFiles: Array<{
    path: string;
    lines: number[];
    snippet: string;
  }>;
}

interface SecuritySummary {
  totalIssues: number;
  criticalCount: number;
  highCount: number;
  mediumCount: number;
  lowCount: number;
  score: number;
}

interface SecurityIssuesProps {
  vulnerabilities: SecurityVulnerability[];
  summary: SecuritySummary;
  isLoading?: boolean;
  onExportReport?: () => void;
}

const VulnerabilityTypeIcon: React.FC<{ type: string }> = ({ type }) => {
  switch (type) {
    case 'injection':
      return <VulnerabilityIcon color="error" />;
    case 'authentication':
      return <SecurityIcon color="error" />;
    case 'exposure':
      return <WarningIcon color="warning" />;
    case 'configuration':
      return <ShieldIcon color="info" />;
    case 'dependency':
      return <DependencyIcon color="warning" />;
    default:
      return <SecurityIcon />;
  }
};

const SecurityScoreCard: React.FC<{ score: number }> = ({ score }) => {
  const getScoreColor = (score: number) => {
    if (score >= 90) return 'success';
    if (score >= 70) return 'warning';
    return 'error';
  };

  return (
    <Paper sx={{ p: 2, textAlign: 'center' }}>
      <Typography variant="h6" gutterBottom>
        Score de Sécurité
      </Typography>
      <Box sx={{ position: 'relative', display: 'inline-flex' }}>
        <CircularProgress
          variant="determinate"
          value={score}
          size={80}
          color={getScoreColor(score)}
        />
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            bottom: 0,
            right: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Typography variant="h4" component="div">
            {score}
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
};

export const SecurityIssues: React.FC<SecurityIssuesProps> = ({
  vulnerabilities,
  summary,
  isLoading,
  onExportReport
}) => {
  const [expandedId, setExpandedId] = React.useState<string | null>(null);

  if (isLoading) {
    return (
      <Box sx={{ width: '100%' }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <SecurityScoreCard score={summary.score} />
        </Grid>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Résumé des Vulnérabilités
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Chip
                icon={<SecurityIcon />}
                label={`${summary.criticalCount} Critiques`}
                color="error"
              />
              <Chip
                icon={<WarningIcon />}
                label={`${summary.highCount} Élevées`}
                color="warning"
              />
              <Chip
                icon={<InfoIcon />}
                label={`${summary.mediumCount} Moyennes`}
                color="info"
              />
              <Chip
                icon={<ShieldIcon />}
                label={`${summary.lowCount} Faibles`}
                color="success"
              />
            </Box>
          </Paper>
        </Grid>
      </Grid>

      <Paper>
        <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">
            Vulnérabilités Détectées
          </Typography>
          <Tooltip title="Exporter le rapport de sécurité">
            <IconButton onClick={onExportReport}>
              <DownloadIcon />
            </IconButton>
          </Tooltip>
        </Box>

        <List>
          {vulnerabilities.map((vuln) => (
            <ListItem
              key={vuln.id}
              button
              onClick={() => setExpandedId(expandedId === vuln.id ? null : vuln.id)}
            >
              <ListItemIcon>
                <VulnerabilityTypeIcon type={vuln.type} />
              </ListItemIcon>
              <ListItemText
                primary={vuln.title}
                secondary={
                  <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                    {vuln.cwe && (
                      <Chip
                        size="small"
                        label={`CWE-${vuln.cwe}`}
                        variant="outlined"
                      />
                    )}
                    {vuln.cvss && (
                      <Chip
                        size="small"
                        label={`CVSS: ${vuln.cvss}`}
                        color={
                          vuln.cvss >= 9 ? 'error' :
                          vuln.cvss >= 7 ? 'warning' :
                          vuln.cvss >= 4 ? 'info' : 'success'
                        }
                      />
                    )}
                  </Box>
                }
              />
              <Chip
                size="small"
                label={vuln.severity}
                color={
                  vuln.severity === 'critical' ? 'error' :
                  vuln.severity === 'high' ? 'warning' :
                  vuln.severity === 'medium' ? 'info' : 'success'
                }
                sx={{ mr: 1 }}
              />
              {expandedId === vuln.id ? <ExpandLess /> : <ExpandMore />}
            </ListItem>
            <Collapse in={expandedId === vuln.id} timeout="auto" unmountOnExit>
              <Box sx={{ p: 3, bgcolor: 'background.default' }}>
                <Alert severity="error" sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Impact
                  </Typography>
                  {vuln.impact}
                </Alert>

                <Typography variant="subtitle2" gutterBottom>
                  Description
                </Typography>
                <Typography paragraph>
                  {vuln.description}
                </Typography>

                <Typography variant="subtitle2" gutterBottom>
                  Fichiers Affectés
                </Typography>
                {vuln.affectedFiles.map((file, index) => (
                  <Paper key={index} variant="outlined" sx={{ p: 2, mb: 2 }}>
                    <Typography variant="subtitle2">
                      {file.path}
                    </Typography>
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
                      <code>{file.snippet}</code>
                    </Box>
                  </Paper>
                ))}

                <Typography variant="subtitle2" gutterBottom>
                  Recommandations
                </Typography>
                <Typography>
                  {vuln.remediation}
                </Typography>
              </Box>
            </Collapse>
          ))}
        </List>
      </Paper>
    </Box>
  );
}; 