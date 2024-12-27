import React from 'react';
import { render, screen } from '@testing-library/react';
import { AnalyticsChart } from '../../../components/dashboard/AnalyticsChart';
import { useDashboard } from '../../../hooks/useDashboard';

// Mock du hook useDashboard
jest.mock('../../../hooks/useDashboard');
const mockUseDashboard = useDashboard as jest.MockedFunction<typeof useDashboard>;

// Mock de la bibliothèque nivo
jest.mock('@nivo/line', () => ({
  ResponsiveLine: () => <div data-testid="line-chart" />,
}));

describe('AnalyticsChart', () => {
  beforeEach(() => {
    mockUseDashboard.mockReset();
  });

  it('affiche un loader pendant le chargement', () => {
    mockUseDashboard.mockReturnValue({
      analytics: [],
      loading: true,
      error: null,
      metrics: {
        activeRisks: 0,
        resolvedRisks: 0,
        globalScore: 0,
        trends: { weekly: '', monthly: '' },
      },
      riskMatrix: [],
      audits: [],
      refresh: jest.fn(),
    });

    render(<AnalyticsChart />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('affiche un message d\'erreur en cas d\'échec', () => {
    const errorMessage = 'Erreur de chargement';
    mockUseDashboard.mockReturnValue({
      analytics: [],
      loading: false,
      error: errorMessage,
      metrics: {
        activeRisks: 0,
        resolvedRisks: 0,
        globalScore: 0,
        trends: { weekly: '', monthly: '' },
      },
      riskMatrix: [],
      audits: [],
      refresh: jest.fn(),
    });

    render(<AnalyticsChart />);
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it('affiche le graphique d\'évolution', () => {
    const mockData = {
      analytics: [
        {
          id: 'risques détectés',
          data: [
            { x: 'Jan', y: 23 },
            { x: 'Fév', y: 28 },
          ],
        },
        {
          id: 'risques résolus',
          data: [
            { x: 'Jan', y: 20 },
            { x: 'Fév', y: 25 },
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
      riskMatrix: [],
      audits: [],
      refresh: jest.fn(),
    };

    mockUseDashboard.mockReturnValue(mockData);

    render(<AnalyticsChart />);
    expect(screen.getByText('Évolution des Risques')).toBeInTheDocument();
    expect(screen.getByTestId('line-chart')).toBeInTheDocument();
  });
}); 