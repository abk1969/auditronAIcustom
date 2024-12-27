"""Composant d'affichage des analyses récentes."""
import React from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Tooltip,
  CircularProgress,
  Button,
  Menu,
  MenuItem,
  Divider,
  useTheme
} from '@mui/material';
import {
  Code as CodeIcon,
  BugReport as BugIcon,
  Security as SecurityIcon,
  Speed as PerformanceIcon,
  MoreVert as MoreIcon,
  OpenInNew as OpenIcon,
  GetApp as DownloadIcon,
  Delete as DeleteIcon,
  FilterList as FilterIcon
} from '@mui/icons-material';

interface Analysis {
  id: string;
  name: string;
  timestamp: number;
  language: string;
  status: 'success' | 'warning' | 'error';
  metrics: {
    bugs: number;
    vulnerabilities: number;
    codeSmells: number;
    performance: number;
  };
  duration: number;
}

interface RecentAnalysesProps {
  analyses: Analysis[];
  isLoading?: boolean;
  onViewDetails: (id: string) => void;
  onDownload: (id: string) => void;
  onDelete: (id: string) => void;
  onFilter: (filters: string[]) => void;
}

const formatDuration = (ms: number) => {
  if (ms < 1000) return `${ms}ms`;
  const seconds = Math.floor(ms / 1000);
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  return `${minutes}m ${seconds % 60}s`;
};

export const RecentAnalyses: React.FC<RecentAnalysesProps> = ({
  analyses,
  isLoading,
  onViewDetails,
  onDownload,
  onDelete,
  onFilter
}) => {
  const theme = useTheme();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const [filterAnchor, setFilterAnchor] = React.useState<null | HTMLElement>(null);
  const [selectedAnalysis, setSelectedAnalysis] = React.useState<string | null>(null);
  const [selectedFilters, setSelectedFilters] = React.useState<string[]>([]);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, id: string) => {
    setAnchorEl(event.currentTarget);
    setSelectedAnalysis(id);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedAnalysis(null);
  };

  const handleFilterClick = (event: React.MouseEvent<HTMLElement>) => {
    setFilterAnchor(event.currentTarget);
  };

  const handleFilterClose = () => {
    setFilterAnchor(null);
  };

  const handleFilterChange = (filter: string) => {
    const newFilters = selectedFilters.includes(filter)
      ? selectedFilters.filter(f => f !== filter)
      : [...selectedFilters, filter];
    setSelectedFilters(newFilters);
    onFilter(newFilters);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return theme.palette.success.main;
      case 'warning':
        return theme.palette.warning.main;
      case 'error':
        return theme.palette.error.main;
      default:
        return theme.palette.grey[500];
    }
  };

  const getLanguageIcon = (language: string) => {
    // Ici, vous pouvez ajouter plus d'icônes spécifiques aux langages
    return <CodeIcon />;
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">
          Analyses Récentes
        </Typography>
        <Box>
          <Tooltip title="Filtrer">
            <IconButton onClick={handleFilterClick}>
              <FilterIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Menu
        anchorEl={filterAnchor}
        open={Boolean(filterAnchor)}
        onClose={handleFilterClose}
      >
        <MenuItem
          onClick={() => handleFilterChange('success')}
          selected={selectedFilters.includes('success')}
        >
          Succès uniquement
        </MenuItem>
        <MenuItem
          onClick={() => handleFilterChange('warning')}
          selected={selectedFilters.includes('warning')}
        >
          Avec avertissements
        </MenuItem>
        <MenuItem
          onClick={() => handleFilterChange('error')}
          selected={selectedFilters.includes('error')}
        >
          Avec erreurs
        </MenuItem>
      </Menu>

      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      ) : (
        <List>
          {analyses.map((analysis, index) => (
            <React.Fragment key={analysis.id}>
              {index > 0 && <Divider />}
              <ListItem
                sx={{
                  '&:hover': {
                    bgcolor: 'action.hover',
                  },
                }}
              >
                <ListItemIcon>
                  {getLanguageIcon(analysis.language)}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {analysis.name}
                      <Chip
                        size="small"
                        label={analysis.language}
                        sx={{ ml: 1 }}
                      />
                    </Box>
                  }
                  secondary={
                    <Box sx={{ mt: 1 }}>
                      <Typography variant="caption" display="block" color="text.secondary">
                        {new Date(analysis.timestamp).toLocaleString()}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                        <Tooltip title="Bugs">
                          <Chip
                            size="small"
                            icon={<BugIcon />}
                            label={analysis.metrics.bugs}
                            color={analysis.metrics.bugs > 0 ? 'error' : 'default'}
                          />
                        </Tooltip>
                        <Tooltip title="Vulnérabilités">
                          <Chip
                            size="small"
                            icon={<SecurityIcon />}
                            label={analysis.metrics.vulnerabilities}
                            color={analysis.metrics.vulnerabilities > 0 ? 'warning' : 'default'}
                          />
                        </Tooltip>
                        <Tooltip title="Performance">
                          <Chip
                            size="small"
                            icon={<PerformanceIcon />}
                            label={`${analysis.metrics.performance}%`}
                          />
                        </Tooltip>
                      </Box>
                    </Box>
                  }
                />
                <ListItemSecondaryAction>
                  <IconButton
                    edge="end"
                    onClick={(e) => handleMenuOpen(e, analysis.id)}
                  >
                    <MoreIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            </React.Fragment>
          ))}
        </List>
      )}

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => {
          onViewDetails(selectedAnalysis!);
          handleMenuClose();
        }}>
          <ListItemIcon>
            <OpenIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Voir les détails" />
        </MenuItem>
        <MenuItem onClick={() => {
          onDownload(selectedAnalysis!);
          handleMenuClose();
        }}>
          <ListItemIcon>
            <DownloadIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Télécharger le rapport" />
        </MenuItem>
        <Divider />
        <MenuItem
          onClick={() => {
            onDelete(selectedAnalysis!);
            handleMenuClose();
          }}
          sx={{ color: 'error.main' }}
        >
          <ListItemIcon>
            <DeleteIcon fontSize="small" color="error" />
          </ListItemIcon>
          <ListItemText primary="Supprimer" />
        </MenuItem>
      </Menu>
    </Paper>
  );
}; 