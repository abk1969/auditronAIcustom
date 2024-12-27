import React from 'react';
import { render, screen } from '@testing-library/react';
import { MetricsOverview } from '../../../components/dashboard/MetricsOverview';
import { useDashboard } from '../../../hooks/useDashboard';

// Mock du hook useDashboard
jest.mock('../../../hooks/useDashboard');
const mockUseDashboard = useDashboard as jest.MockedFunction<typeof useDashboard>;

describe('MetricsOverview', () => {
  beforeEach(() => {
    mockUseDashboard.mockReset();
  });

  it('affiche un loader pendant le chargement', () => {
    mockUseDashboard.mockReturnValue({
      metrics: {
        activeRisks: 0,
        resolvedRisks: 0,
        globalScore: 0,
        trends: { weekly: '', monthly: '' },
      },
      loading: true,
      error: null,
      riskMatrix: [],
      analytics: [],
      audits: [],
      refresh: jest.fn(),
    });

    render(<MetricsOverview />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('affiche un message d\'erreur en cas d\'échec', () => {
    const errorMessage = 'Erreur de chargement';
    mockUseDashboard.mockReturnValue({
      metrics: {
        activeRisks: 0,
        resolvedRisks: 0,
        globalScore: 0,
        trends: { weekly: '', monthly: '' },
      },
      loading: false,
      error: errorMessage,
      riskMatrix: [],
      analytics: [],
      audits: [],
      refresh: jest.fn(),
    });

    render(<MetricsOverview />);
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it('affiche les métriques correctement', () => {
    const mockData = {
      metrics: {
        activeRisks: 42,
        resolvedRisks: 128,
        globalScore: 8.5,
        trends: {
          weekly: '+5% cette semaine',
          monthly: '+12% ce mois',
        },
      },
      loading: false,
      error: null,
      riskMatrix: [],
      analytics: [],
      audits: [],
      refresh: jest.fn(),
    };

    mockUseDashboard.mockReturnValue(mockData);

    render(<MetricsOverview />);

    expect(screen.getByText('42')).toBeInTheDocument();
    expect(screen.getByText('128')).toBeInTheDocument();
    expect(screen.getByText('8.5/10')).toBeInTheDocument();
    expect(screen.getByText('+5% cette semaine')).toBeInTheDocument();
    expect(screen.getByText('+12% ce mois')).toBeInTheDocument();
  });

  it('affiche les titres des métriques', () => {
    mockUseDashboard.mockReturnValue({
      metrics: {
        activeRisks: 0,
        resolvedRisks: 0,
        globalScore: 0,
        trends: { weekly: '', monthly: '' },
      },
      loading: false,
      error: null,
      riskMatrix: [],
      analytics: [],
      audits: [],
      refresh: jest.fn(),
    });

    render(<MetricsOverview />);

    expect(screen.getByText('Risques Actifs')).toBeInTheDocument();
    expect(screen.getByText('Risques Résolus')).toBeInTheDocument();
    expect(screen.getByText('Score Global')).toBeInTheDocument();
  });
}); 