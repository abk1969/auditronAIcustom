"""Composant de visualisation des métriques clés."""
import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  IconButton,
  Menu,
  MenuItem,
  Tooltip,
  CircularProgress,
  useTheme
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  Line,
  ComposedChart
} from 'recharts';
import {
  MoreVert as MoreIcon,
  FileDownload as ExportIcon,
  Refresh as RefreshIcon,
  DateRange as DateRangeIcon
} from '@mui/icons-material';

interface MetricsData {
  date: string;
  codeQuality: number;
  bugs: number;
  vulnerabilities: number;
  performance: number;
}

interface MetricsChartProps {
  data: MetricsData[];
  isLoading?: boolean;
  onRefresh?: () => void;
  onExport?: () => void;
  onDateRangeChange?: (range: string) => void;
}

const dateRangeOptions = [
  { value: '7d', label: '7 derniers jours' },
  { value: '30d', label: '30 derniers jours' },
  { value: '90d', label: '90 derniers jours' },
  { value: '1y', label: 'Cette année' }
];

export const MetricsChart: React.FC<MetricsChartProps> = ({
  data,
  isLoading,
  onRefresh,
  onExport,
  onDateRangeChange
}) => {
  const theme = useTheme();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const [dateRange, setDateRange] = React.useState('30d');

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleDateRangeChange = (range: string) => {
    setDateRange(range);
    onDateRangeChange?.(range);
    handleMenuClose();
  };

  const getMetricColor = (value: number) => {
    if (value >= 80) return theme.palette.success.main;
    if (value >= 60) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <Paper sx={{ p: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            {label}
          </Typography>
          {payload.map((entry: any) => (
            <Box key={entry.name} sx={{ color: entry.color }}>
              <Typography variant="body2">
                {entry.name}: {entry.value}
              </Typography>
            </Box>
          ))}
        </Paper>
      );
    }
    return null;
  };

  return (
    <Paper sx={{ p: 3, height: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h6">
          Métriques de Performance
        </Typography>
        <Box>
          <Tooltip title="Rafraîchir">
            <IconButton onClick={onRefresh} disabled={isLoading}>
              {isLoading ? <CircularProgress size={24} /> : <RefreshIcon />}
            </IconButton>
          </Tooltip>
          <Tooltip title="Exporter">
            <IconButton onClick={onExport}>
              <ExportIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Période">
            <IconButton onClick={handleMenuClick}>
              <DateRangeIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        {dateRangeOptions.map(option => (
          <MenuItem
            key={option.value}
            selected={dateRange === option.value}
            onClick={() => handleDateRangeChange(option.value)}
          >
            {option.label}
          </MenuItem>
        ))}
      </Menu>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        {Object.entries(data[data.length - 1] || {}).map(([key, value]) => {
          if (key === 'date') return null;
          return (
            <Grid item xs={12} sm={6} md={3} key={key}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography
                  variant="h4"
                  sx={{ color: getMetricColor(value as number) }}
                >
                  {value}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {key.replace(/([A-Z])/g, ' $1').trim()}
                </Typography>
              </Box>
            </Grid>
          );
        })}
      </Grid>

      <Box sx={{ height: 400 }}>
        <ResponsiveContainer>
          <ComposedChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => new Date(value).toLocaleDateString()}
            />
            <YAxis yAxisId="left" />
            <YAxis yAxisId="right" orientation="right" />
            <RechartsTooltip content={<CustomTooltip />} />
            <Legend />
            <Bar
              yAxisId="left"
              dataKey="codeQuality"
              name="Qualité du Code"
              fill={theme.palette.primary.main}
              radius={[4, 4, 0, 0]}
            />
            <Bar
              yAxisId="left"
              dataKey="bugs"
              name="Bugs"
              fill={theme.palette.error.main}
              radius={[4, 4, 0, 0]}
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="performance"
              name="Performance"
              stroke={theme.palette.success.main}
              strokeWidth={2}
              dot={false}
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="vulnerabilities"
              name="Vulnérabilités"
              stroke={theme.palette.warning.main}
              strokeWidth={2}
              dot={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
}; 