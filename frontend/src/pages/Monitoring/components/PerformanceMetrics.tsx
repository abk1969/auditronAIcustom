"""Composant de métriques de performance en temps réel."""
import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  CircularProgress,
  Tooltip,
  IconButton,
  Menu,
  MenuItem,
  Chip
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import {
  Settings as SettingsIcon,
  FileDownload as ExportIcon,
  Refresh as RefreshIcon,
  Timer as LatencyIcon,
  Speed as ThroughputIcon,
  Error as ErrorIcon,
  CheckCircle as SuccessIcon
} from '@mui/icons-material';

interface MetricData {
  timestamp: number;
  value: number;
}

interface PerformanceData {
  latency: MetricData[];
  throughput: MetricData[];
  errorRate: MetricData[];
  successRate: MetricData[];
  currentValues: {
    latency: number;
    throughput: number;
    errorRate: number;
    successRate: number;
  };
}

interface PerformanceMetricsProps {
  data?: PerformanceData;
  isLoading?: boolean;
  onRefresh?: () => void;
  onExport?: () => void;
  timeRange: '1h' | '24h' | '7d' | '30d';
  onTimeRangeChange: (range: '1h' | '24h' | '7d' | '30d') => void;
}

const MetricCard: React.FC<{
  title: string;
  value: number;
  unit: string;
  icon: React.ReactNode;
  color: string;
  trend?: number;
}> = ({ title, value, unit, icon, color, trend }) => (
  <Paper sx={{ p: 2 }}>
    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
      <Box sx={{ color, mr: 1 }}>{icon}</Box>
      <Typography variant="subtitle2" color="text.secondary">
        {title}
      </Typography>
    </Box>
    <Typography variant="h4" component="div" sx={{ mb: 1 }}>
      {value.toFixed(2)}{unit}
    </Typography>
    {trend && (
      <Chip
        size="small"
        label={`${trend > 0 ? '+' : ''}${trend.toFixed(1)}%`}
        color={trend > 0 ? 'success' : 'error'}
        variant="outlined"
      />
    )}
  </Paper>
);

export const PerformanceMetrics: React.FC<PerformanceMetricsProps> = ({
  data,
  isLoading,
  onRefresh,
  onExport,
  timeRange,
  onTimeRangeChange
}) => {
  const [settingsAnchor, setSettingsAnchor] = React.useState<null | HTMLElement>(null);

  const handleSettingsClick = (event: React.MouseEvent<HTMLElement>) => {
    setSettingsAnchor(event.currentTarget);
  };

  const handleSettingsClose = () => {
    setSettingsAnchor(null);
  };

  const timeRangeOptions = {
    '1h': 'Dernière heure',
    '24h': 'Dernières 24h',
    '7d': '7 derniers jours',
    '30d': '30 derniers jours'
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!data) {
    return (
      <Typography color="text.secondary">
        Aucune donnée disponible
      </Typography>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h6">
          Métriques de Performance
        </Typography>
        <Box>
          <Tooltip title="Rafraîchir">
            <IconButton onClick={onRefresh}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Exporter">
            <IconButton onClick={onExport}>
              <ExportIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Paramètres">
            <IconButton onClick={handleSettingsClick}>
              <SettingsIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Latence Moyenne"
            value={data.currentValues.latency}
            unit="ms"
            icon={<LatencyIcon />}
            color="#8884d8"
            trend={-5.2}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Débit"
            value={data.currentValues.throughput}
            unit="/s"
            icon={<ThroughputIcon />}
            color="#82ca9d"
            trend={2.8}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Taux d'Erreur"
            value={data.currentValues.errorRate}
            unit="%"
            icon={<ErrorIcon />}
            color="#ff8042"
            trend={-1.5}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Taux de Succès"
            value={data.currentValues.successRate}
            unit="%"
            icon={<SuccessIcon />}
            color="#00C49F"
            trend={1.5}
          />
        </Grid>
      </Grid>

      <Paper sx={{ p: 2 }}>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="timestamp"
              type="number"
              scale="time"
              domain={['auto', 'auto']}
              tickFormatter={(timestamp) => new Date(timestamp).toLocaleTimeString()}
            />
            <YAxis yAxisId="left" />
            <YAxis yAxisId="right" orientation="right" />
            <RechartsTooltip
              labelFormatter={(value) => new Date(value).toLocaleString()}
            />
            <Legend />
            <Line
              yAxisId="left"
              type="monotone"
              data={data.latency}
              dataKey="value"
              name="Latence (ms)"
              stroke="#8884d8"
              dot={false}
            />
            <Line
              yAxisId="right"
              type="monotone"
              data={data.throughput}
              dataKey="value"
              name="Débit (req/s)"
              stroke="#82ca9d"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </Paper>

      <Menu
        anchorEl={settingsAnchor}
        open={Boolean(settingsAnchor)}
        onClose={handleSettingsClose}
      >
        {Object.entries(timeRangeOptions).map(([value, label]) => (
          <MenuItem
            key={value}
            selected={timeRange === value}
            onClick={() => {
              onTimeRangeChange(value as '1h' | '24h' | '7d' | '30d');
              handleSettingsClose();
            }}
          >
            {label}
          </MenuItem>
        ))}
      </Menu>
    </Box>
  );
}; 