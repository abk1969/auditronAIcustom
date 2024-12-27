import React from 'react';
import { Box, Typography, Grid, Paper } from '@mui/material';
import { RiskData } from '../../types/api';

const mockRisks: RiskData[] = [
  {
    id: '1',
    probability: 0.8,
    impact: 0.9,
    category: 'Sécurité',
    description: 'Vulnérabilité critique dans l\'authentification',
  },
  {
    id: '2',
    probability: 0.4,
    impact: 0.6,
    category: 'Performance',
    description: 'Temps de réponse élevé',
  },
  {
    id: '3',
    probability: 0.2,
    impact: 0.3,
    category: 'Configuration',
    description: 'Paramètres non sécurisés',
  },
];

const getColor = (probability: number, impact: number): string => {
  const risk = probability * impact;
  if (risk > 0.6) return '#f44336'; // Rouge
  if (risk > 0.3) return '#ff9800'; // Orange
  return '#4caf50'; // Vert
};

export const RiskMatrix: React.FC = () => {
  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Matrice des Risques
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Box
            sx={{
              width: '100%',
              height: 300,
              position: 'relative',
              border: '1px solid #ddd',
              borderRadius: 1,
            }}
          >
            {mockRisks.map((risk) => (
              <Box
                key={risk.id}
                sx={{
                  position: 'absolute',
                  left: `${risk.probability * 100}%`,
                  bottom: `${risk.impact * 100}%`,
                  transform: 'translate(-50%, 50%)',
                  width: 16,
                  height: 16,
                  borderRadius: '50%',
                  backgroundColor: getColor(risk.probability, risk.impact),
                  cursor: 'pointer',
                  '&:hover': {
                    transform: 'translate(-50%, 50%) scale(1.2)',
                  },
                }}
                title={`${risk.category}: ${risk.description}`}
              />
            ))}
            <Box
              sx={{
                position: 'absolute',
                bottom: 0,
                left: 0,
                right: 0,
                textAlign: 'center',
                p: 1,
              }}
            >
              Probabilité
            </Box>
            <Box
              sx={{
                position: 'absolute',
                top: '50%',
                left: -20,
                transform: 'rotate(-90deg)',
                transformOrigin: 'center',
              }}
            >
              Impact
            </Box>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
}; 