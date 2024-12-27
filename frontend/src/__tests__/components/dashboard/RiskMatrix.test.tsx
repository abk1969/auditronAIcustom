import React from 'react';
import { render, screen } from '@testing-library/react';
import { RiskMatrix } from '../../../components/dashboard/RiskMatrix';
import { useDashboard } from '../../../hooks/useDashboard';

// Mock du hook useDashboard
jest.mock('../../../hooks/useDashboard');
const mockUseDashboard = useDashboard as jest.MockedFunction<typeof useDashboard>;

// Mock de la bibliothèque nivo
jest.mock('@nivo/heatmap', () => ({
  ResponsiveHeatMap: () => <div data-testid="heatmap" />,
}));

describe('RiskMatrix', () => {
  beforeEach(() => {
    mockUseDashboard.mockReset();
  });

  it('affiche un loader pendant le chargement', () => {
    mockUseDashboard.mockReturnValue({
      riskMatrix: [],
      loading: true,
      error: null,
      metrics: {
        activeRisks: 0,
        resolvedRisks: 0,
        globalScore: 0,
        trends: { weekly: '', monthly: '' },
      },
      analytics: [],
      audits: [],
      refresh: jest.fn(),
    });

    render(<RiskMatrix />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('affiche un message d\'erreur en cas d\'échec', () => {
    const errorMessage = 'Erreur de chargement';
    mockUseDashboard.mockReturnValue({
      riskMatrix: [],
      loading: false,
      error: errorMessage,
      metrics: {
        activeRisks: 0,
        resolvedRisks: 0,
        globalScore: 0,
        trends: { weekly: '', monthly: '' },
      },
      analytics: [],
      audits: [],
      refresh: jest.fn(),
    });

    render(<RiskMatrix />);
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it('affiche la matrice des risques', () => {
    const mockData = {
      riskMatrix: [
        {
          id: 'Catastrophique',
          data: [
            { x: 'Rare', y: 3 },
            { x: 'Peu probable', y: 4 },
          ],
        },
      ],
      loading: false,
      error: null,
      metrics: {
        activeRisks: 0,
        resolvedRisks: 0,
        globalScore: 0,
        trends: { weekly: '', monthly: '' },
      },
      analytics: [],
      audits: [],
      refresh: jest.fn(),
    };

    mockUseDashboard.mockReturnValue(mockData);

    render(<RiskMatrix />);
    expect(screen.getByText('Matrice des Risques')).toBeInTheDocument();
    expect(screen.getByTestId('heatmap')).toBeInTheDocument();
  });
}); 