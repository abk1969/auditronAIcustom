"""Composant de chronologie des alertes et incidents."""
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
  IconButton,
  Tooltip,
  Button,
  Menu,
  MenuItem,
  Divider,
  Badge,
  Alert
} from '@mui/material';
import {
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  CheckCircle as ResolvedIcon,
  FilterList as FilterIcon,
  Timeline as TimelineIcon,
  Notifications as NotificationsIcon,
  MoreVert as MoreIcon
} from '@mui/icons-material';
import Timeline from '@mui/lab/Timeline';
import TimelineItem from '@mui/lab/TimelineItem';
import TimelineSeparator from '@mui/lab/TimelineSeparator';
import TimelineConnector from '@mui/lab/TimelineConnector';
import TimelineContent from '@mui/lab/TimelineContent';
import TimelineDot from '@mui/lab/TimelineDot';
import TimelineOppositeContent from '@mui/lab/TimelineOppositeContent';

interface Alert {
  id: string;
  type: 'error' | 'warning' | 'info' | 'success';
  title: string;
  message: string;
  timestamp: number;
  source: string;
  status: 'active' | 'resolved' | 'acknowledged';
  resolution?: {
    timestamp: number;
    by: string;
    comment: string;
  };
  metrics?: {
    [key: string]: number;
  };
  relatedAlerts?: string[];
}

interface AlertsTimelineProps {
  alerts: Alert[];
  isLoading?: boolean;
  onAcknowledge: (alertId: string) => void;
  onResolve: (alertId: string, comment: string) => void;
  onFilter: (filters: string[]) => void;
}

const AlertIcon: React.FC<{ type: string }> = ({ type }) => {
  switch (type) {
    case 'error':
      return <ErrorIcon color="error" />;
    case 'warning':
      return <WarningIcon color="warning" />;
    case 'info':
      return <InfoIcon color="info" />;
    case 'success':
      return <ResolvedIcon color="success" />;
    default:
      return <InfoIcon />;
  }
};

export const AlertsTimeline: React.FC<AlertsTimelineProps> = ({
  alerts,
  isLoading,
  onAcknowledge,
  onResolve,
  onFilter
}) => {
  const [filterAnchor, setFilterAnchor] = React.useState<null | HTMLElement>(null);
  const [selectedFilters, setSelectedFilters] = React.useState<string[]>([]);
  const [selectedAlert, setSelectedAlert] = React.useState<Alert | null>(null);

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
      case 'active':
        return 'error';
      case 'acknowledged':
        return 'warning';
      case 'resolved':
        return 'success';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h6">
          Chronologie des Alertes
        </Typography>
        <Box>
          <Tooltip title="Filtrer">
            <IconButton onClick={handleFilterClick}>
              <Badge
                badgeContent={selectedFilters.length}
                color="primary"
                sx={{ '& .MuiBadge-badge': { right: -3, top: 3 } }}
              >
                <FilterIcon />
              </Badge>
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
          onClick={() => handleFilterChange('error')}
          selected={selectedFilters.includes('error')}
        >
          <ListItemIcon>
            <ErrorIcon color="error" />
          </ListItemIcon>
          <ListItemText primary="Erreurs" />
        </MenuItem>
        <MenuItem
          onClick={() => handleFilterChange('warning')}
          selected={selectedFilters.includes('warning')}
        >
          <ListItemIcon>
            <WarningIcon color="warning" />
          </ListItemIcon>
          <ListItemText primary="Avertissements" />
        </MenuItem>
        <MenuItem
          onClick={() => handleFilterChange('info')}
          selected={selectedFilters.includes('info')}
        >
          <ListItemIcon>
            <InfoIcon color="info" />
          </ListItemIcon>
          <ListItemText primary="Informations" />
        </MenuItem>
        <Divider />
        <MenuItem
          onClick={() => handleFilterChange('active')}
          selected={selectedFilters.includes('active')}
        >
          <ListItemText primary="Actives uniquement" />
        </MenuItem>
      </Menu>

      <Timeline position="alternate">
        {alerts.map((alert) => (
          <TimelineItem key={alert.id}>
            <TimelineOppositeContent color="text.secondary">
              {new Date(alert.timestamp).toLocaleString()}
            </TimelineOppositeContent>
            <TimelineSeparator>
              <TimelineDot color={alert.type as any}>
                <AlertIcon type={alert.type} />
              </TimelineDot>
              <TimelineConnector />
            </TimelineSeparator>
            <TimelineContent>
              <Paper
                elevation={3}
                sx={{
                  p: 2,
                  bgcolor: alert.status === 'active' ? 'action.hover' : 'background.paper'
                }}
              >
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Typography variant="subtitle1">
                    {alert.title}
                  </Typography>
                  <Chip
                    size="small"
                    label={alert.status}
                    color={getStatusColor(alert.status) as any}
                  />
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  {alert.message}
                </Typography>
                {alert.metrics && (
                  <Box sx={{ mt: 1 }}>
                    {Object.entries(alert.metrics).map(([key, value]) => (
                      <Chip
                        key={key}
                        size="small"
                        label={`${key}: ${value}`}
                        sx={{ mr: 1, mt: 1 }}
                      />
                    ))}
                  </Box>
                )}
                {alert.status === 'active' && (
                  <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
                    <Button
                      size="small"
                      onClick={() => onAcknowledge(alert.id)}
                    >
                      Acquitter
                    </Button>
                    <Button
                      size="small"
                      variant="contained"
                      onClick={() => onResolve(alert.id, '')}
                    >
                      Résoudre
                    </Button>
                  </Box>
                )}
                {alert.resolution && (
                  <Alert
                    severity="success"
                    sx={{ mt: 2 }}
                    icon={<ResolvedIcon />}
                  >
                    <Typography variant="caption">
                      Résolu par {alert.resolution.by} le{' '}
                      {new Date(alert.resolution.timestamp).toLocaleString()}
                    </Typography>
                    <Typography variant="body2">
                      {alert.resolution.comment}
                    </Typography>
                  </Alert>
                )}
              </Paper>
            </TimelineContent>
          </TimelineItem>
        ))}
      </Timeline>
    </Box>
  );
}; 