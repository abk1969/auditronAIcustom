import React from 'react';
import { Box, Typography } from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { useDashboard } from '../../hooks/useDashboard';

const mockData = [
  { date: '2024-01', issues: 65, resolved: 45 },
  { date: '2024-02', issues: 78, resolved: 60 },
  { date: '2024-03', issues: 82, resolved: 75 },
  { date: '2024-04', issues: 70, resolved: 65 },
];

export const AnalyticsChart: React.FC = () => {
  return (
    <Box height="100%">
      <Typography variant="h6" gutterBottom>
        Évolution des Problèmes de Sécurité
      </Typography>
      <ResponsiveContainer width="100%" height="90%">
        <LineChart
          data={mockData}
          margin={{
            top: 5,
            right: 30,
            left: 20,
            bottom: 5,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="issues"
            name="Problèmes Détectés"
            stroke="#ff9800"
            activeDot={{ r: 8 }}
          />
          <Line
            type="monotone"
            dataKey="resolved"
            name="Problèmes Résolus"
            stroke="#4caf50"
            activeDot={{ r: 8 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
}; 