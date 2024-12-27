"""Composant de surveillance des ressources système."""
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
  Menu,
  MenuItem,
  Alert
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Warning as WarningIcon,
  Memory as MemoryIcon,
  Storage as StorageIcon,
  Speed as CpuIcon,
  NetworkCheck as NetworkIcon
} from '@mui/icons-material';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';

interface ResourceMetric {
  timestamp: number;
  value: number;
}

interface ResourceData {
  cpu: {
    current: number;
    history: ResourceMetric[];
    cores: number;
    temperature: number;
    processes: number;
  };
  memory: {
    current: number;
    history: ResourceMetric[];
    total: number;
    free: number;
    cached: number;
  };
  disk: {
    current: number;
    history: ResourceMetric[];
    total: number;
    free: number;
    readSpeed: number;
    writeSpeed: number;
  };
  network: {
    current: number;
    history: ResourceMetric[];
    bytesIn: number;
    bytesOut: number;
    connections: number;
  };
}

interface ResourceUsageProps {
  data?: ResourceData;
  isLoading?: boolean;
  onRefresh?: () => void;
  timeRange: '1h' | '24h' | '7d' | '30d';
  onTimeRangeChange: (range: '1h' | '24h' | '7d' | '30d') => void;
}

const ResourceGauge: React.FC<{
  value: number;
  title: string;
  icon: React.ReactNode;
  details: string[];
  color: string;
  warning?: boolean;
}> = ({ value, title, icon, details, color, warning }) => (
  <Paper sx={{ p: 2, position: 'relative' }}>
    {warning && (
      <WarningIcon
        color="warning"
        sx={{ position: 'absolute', top: 8, right: 8 }}
      />
    )}
    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
      <Box sx={{ color, mr: 1 }}>{icon}</Box>
      <Typography variant="subtitle1">{title}</Typography>
    </Box>
    <Box sx={{ position: 'relative', display: 'inline-flex', mb: 2 }}>
      <CircularProgress
        variant="determinate"
        value={value}
        size={80}
        sx={{
          color: value > 90 ? 'error.main' :
                 value > 70 ? 'warning.main' : color
        }}
      />
      <Box
        sx={{
          top: 0,
          left: 0,
          bottom: 0,
          right: 0,
          position: 'absolute',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Typography variant="h6" component="div">
          {value}%
        </Typography>
      </Box>
    </Box>
    <Box>
      {details.map((detail, index) => (
        <Typography
          key={index}
          variant="body2"
          color="text.secondary"
          sx={{ mb: 0.5 }}
        >
          {detail}
        </Typography>
      ))}
    </Box>
  </Paper>
);

export const ResourceUsage: React.FC<ResourceUsageProps> = ({
  data,
  isLoading,
  onRefresh,
  timeRange,
  onTimeRangeChange
}) => {
  const [settingsAnchor, setSettingsAnchor] = React.useState<null | HTMLElement>(null);

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!data) {
    return (
      <Alert severity="error">
        Impossible de récupérer les données des ressources
      </Alert>
    );
  }

  const formatBytes = (bytes: number) => {
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    if (bytes === 0) return '0 B';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`;
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h6">
          Utilisation des Ressources
        </Typography>
        <Box>
          <IconButton onClick={onRefresh}>
            <SettingsIcon />
          </IconButton>
        </Box>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <ResourceGauge
            value={data.cpu.current}
            title="CPU"
            icon={<CpuIcon />}
            details={[
              `${data.cpu.cores} Cœurs`,
              `${data.cpu.temperature}°C`,
              `${data.cpu.processes} Processus`
            ]}
            color="#2196f3"
            warning={data.cpu.temperature > 80}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <ResourceGauge
            value={data.memory.current}
            title="Mémoire"
            icon={<MemoryIcon />}
            details={[
              `Total: ${formatBytes(data.memory.total)}`,
              `Libre: ${formatBytes(data.memory.free)}`,
              `Cache: ${formatBytes(data.memory.cached)}`
            ]}
            color="#4caf50"
            warning={data.memory.free < data.memory.total * 0.1}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <ResourceGauge
            value={data.disk.current}
            title="Disque"
            icon={<StorageIcon />}
            details={[
              `Total: ${formatBytes(data.disk.total)}`,
              `Libre: ${formatBytes(data.disk.free)}`,
              `Lecture: ${formatBytes(data.disk.readSpeed)}/s`,
              `Écriture: ${formatBytes(data.disk.writeSpeed)}/s`
            ]}
            color="#ff9800"
            warning={data.disk.free < data.disk.total * 0.1}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <ResourceGauge
            value={data.network.current}
            title="Réseau"
            icon={<NetworkIcon />}
            details={[
              `Entrée: ${formatBytes(data.network.bytesIn)}/s`,
              `Sortie: ${formatBytes(data.network.bytesOut)}/s`,
              `Connexions: ${data.network.connections}`
            ]}
            color="#9c27b0"
          />
        </Grid>
      </Grid>

      <Paper sx={{ mt: 3, p: 2 }}>
        <Typography variant="subtitle1" gutterBottom>
          Historique d'Utilisation
        </Typography>
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="timestamp"
              type="number"
              scale="time"
              domain={['auto', 'auto']}
              tickFormatter={(ts) => new Date(ts).toLocaleTimeString()}
            />
            <YAxis />
            <RechartsTooltip
              labelFormatter={(ts) => new Date(ts).toLocaleString()}
            />
            <Legend />
            <Area
              type="monotone"
              dataKey="value"
              data={data.cpu.history}
              name="CPU"
              stroke="#2196f3"
              fill="#2196f3"
              fillOpacity={0.3}
            />
            <Area
              type="monotone"
              dataKey="value"
              data={data.memory.history}
              name="Mémoire"
              stroke="#4caf50"
              fill="#4caf50"
              fillOpacity={0.3}
            />
            <Area
              type="monotone"
              dataKey="value"
              data={data.disk.history}
              name="Disque"
              stroke="#ff9800"
              fill="#ff9800"
              fillOpacity={0.3}
            />
            <Area
              type="monotone"
              dataKey="value"
              data={data.network.history}
              name="Réseau"
              stroke="#9c27b0"
              fill="#9c27b0"
              fillOpacity={0.3}
            />
          </AreaChart>
        </ResponsiveContainer>
      </Paper>
    </Box>
  );
}; 