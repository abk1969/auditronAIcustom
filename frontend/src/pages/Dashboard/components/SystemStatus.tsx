"""Composant d'affichage de l'état du système."""
import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  CircularProgress,
  LinearProgress,
  Tooltip,
  IconButton,
  Chip,
  Stack,
  useTheme
} from '@mui/material';
import {
  CheckCircle as HealthyIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  Memory as CpuIcon,
  Storage as DiskIcon,
  Memory as RamIcon,
  NetworkCheck as NetworkIcon
} from '@mui/icons-material';

interface SystemMetrics {
  cpu: {
    usage: number;
    temperature: number;
    cores: number;
  };
  memory: {
    total: number;
    used: number;
    free: number;
  };
  disk: {
    total: number;
    used: number;
    free: number;
    readSpeed: number;
    writeSpeed: number;
  };
  network: {
    bytesIn: number;
    bytesOut: number;
    latency: number;
    status: 'healthy' | 'degraded' | 'error';
  };
  services: {
    name: string;
    status: 'healthy' | 'degraded' | 'error';
    uptime: number;
    lastCheck: string;
  }[];
}

interface SystemStatusProps {
  metrics: SystemMetrics;
  isLoading?: boolean;
  onRefresh?: () => void;
}

const formatBytes = (bytes: number) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
};

const formatUptime = (seconds: number) => {
  const days = Math.floor(seconds / (24 * 60 * 60));
  const hours = Math.floor((seconds % (24 * 60 * 60)) / (60 * 60));
  const minutes = Math.floor((seconds % (60 * 60)) / 60);
  
  if (days > 0) return `${days}j ${hours}h`;
  if (hours > 0) return `${hours}h ${minutes}m`;
  return `${minutes}m`;
};

const StatusChip: React.FC<{ status: string }> = ({ status }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'healthy':
        return 'success';
      case 'degraded':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'healthy':
        return <HealthyIcon />;
      case 'degraded':
        return <WarningIcon />;
      case 'error':
        return <ErrorIcon />;
      default:
        return null;
    }
  };

  return (
    <Chip
      icon={getStatusIcon()}
      label={status.charAt(0).toUpperCase() + status.slice(1)}
      color={getStatusColor() as any}
      size="small"
    />
  );
};

export const SystemStatus: React.FC<SystemStatusProps> = ({
  metrics,
  isLoading,
  onRefresh
}) => {
  const theme = useTheme();

  const getUsageColor = (usage: number) => {
    if (usage < 70) return theme.palette.success.main;
    if (usage < 90) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h6">
          État du Système
        </Typography>
        <Tooltip title="Rafraîchir">
          <IconButton onClick={onRefresh} disabled={isLoading}>
            {isLoading ? <CircularProgress size={24} /> : <RefreshIcon />}
          </IconButton>
        </Tooltip>
      </Box>

      <Grid container spacing={3}>
        {/* CPU Status */}
        <Grid item xs={12} md={6}>
          <Paper variant="outlined" sx={{ p: 2 }}>
            <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
              <CpuIcon color="primary" />
              <Typography variant="subtitle1">CPU</Typography>
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ ml: 'auto' }}
              >
                {metrics.cpu.cores} cœurs
              </Typography>
            </Stack>
            <Box sx={{ mb: 1 }}>
              <Typography variant="body2" color="text.secondary">
                Utilisation
              </Typography>
              <LinearProgress
                variant="determinate"
                value={metrics.cpu.usage}
                sx={{
                  height: 8,
                  borderRadius: 1,
                  bgcolor: 'background.default',
                  '& .MuiLinearProgress-bar': {
                    bgcolor: getUsageColor(metrics.cpu.usage)
                  }
                }}
              />
            </Box>
            <Typography variant="body2" color="text.secondary">
              Température: {metrics.cpu.temperature}°C
            </Typography>
          </Paper>
        </Grid>

        {/* Memory Status */}
        <Grid item xs={12} md={6}>
          <Paper variant="outlined" sx={{ p: 2 }}>
            <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
              <RamIcon color="primary" />
              <Typography variant="subtitle1">Mémoire</Typography>
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ ml: 'auto' }}
              >
                {formatBytes(metrics.memory.total)}
              </Typography>
            </Stack>
            <Box sx={{ mb: 1 }}>
              <Typography variant="body2" color="text.secondary">
                Utilisation
              </Typography>
              <LinearProgress
                variant="determinate"
                value={(metrics.memory.used / metrics.memory.total) * 100}
                sx={{
                  height: 8,
                  borderRadius: 1,
                  bgcolor: 'background.default',
                  '& .MuiLinearProgress-bar': {
                    bgcolor: getUsageColor((metrics.memory.used / metrics.memory.total) * 100)
                  }
                }}
              />
            </Box>
            <Typography variant="body2" color="text.secondary">
              Libre: {formatBytes(metrics.memory.free)}
            </Typography>
          </Paper>
        </Grid>

        {/* Services Status */}
        <Grid item xs={12}>
          <Paper variant="outlined" sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Services
            </Typography>
            <Grid container spacing={2}>
              {metrics.services.map((service) => (
                <Grid item xs={12} sm={6} md={4} key={service.name}>
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      p: 1,
                      borderRadius: 1,
                      bgcolor: 'background.default'
                    }}
                  >
                    <Box>
                      <Typography variant="body2">
                        {service.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Uptime: {formatUptime(service.uptime)}
                      </Typography>
                    </Box>
                    <StatusChip status={service.status} />
                  </Box>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Paper>
  );
}; 