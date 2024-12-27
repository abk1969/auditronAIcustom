import React from 'react';
import { render, screen } from '@testing-library/react';
import { AuditTimeline } from '../../../components/dashboard/AuditTimeline';
import { useDashboard } from '../../../hooks/useDashboard';

// Mock du hook useDashboard
jest.mock('../../../hooks/useDashboard');
const mockUseDashboard = useDashboard as jest.MockedFunction<typeof useDashboard>;

describe('AuditTimeline', () => {
  beforeEach(() => {
    mockUseDashboard.mockReset();
  });

  it('affiche un loader pendant le chargement', () => {
    mockUseDashboard.mockReturnValue({
      audits: [],
      loading: true,
      error: null,
      metrics: {
        activeRisks: 0,
        resolvedRisks: 0,
        globalScore: 0,
        trends: { weekly: '', monthly: '' },
      },
      riskMatrix: [],
      analytics: [],
      refresh: jest.fn(),
    });

    render(<AuditTimeline />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('affiche un message d\'erreur en cas d\'échec', () => {
    const errorMessage = 'Erreur de chargement';
    mockUseDashboard.mockReturnValue({
      audits: [],
      loading: false,
      error: errorMessage,
      metrics: {
        activeRisks: 0,
        resolvedRisks: 0,
        globalScore: 0,
        trends: { weekly: '', monthly: '' },
      },
      riskMatrix: [],
      analytics: [],
      refresh: jest.fn(),
    });

    render(<AuditTimeline />);
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it('affiche la chronologie des audits', () => {
    const mockData = {
      audits: [
        {
          id: 1,
          date: new Date('2023-12-20'),
          title: 'Audit de Sécurité',
          status: 'completed' as const,
          description: 'Analyse complète des vulnérabilités',
        },
        {
          id: 2,
          date: new Date('2023-12-18'),
          title: 'Audit de Conformité',
          status: 'warning' as const,
          description: 'Revue des processus internes',
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
      analytics: [],
      refresh: jest.fn(),
    };

    mockUseDashboard.mockReturnValue(mockData);

    render(<AuditTimeline />);
    expect(screen.getByText('Chronologie des Audits')).toBeInTheDocument();
    expect(screen.getByText('Audit de Sécurité')).toBeInTheDocument();
    expect(screen.getByText('Audit de Conformité')).toBeInTheDocument();
    expect(screen.getByText('Analyse complète des vulnérabilités')).toBeInTheDocument();
    expect(screen.getByText('Revue des processus internes')).toBeInTheDocument();
  });

  it('affiche les dates au format correct', () => {
    const mockData = {
      audits: [
        {
          id: 1,
          date: new Date('2023-12-20'),
          title: 'Audit de Sécurité',
          status: 'completed' as const,
          description: 'Analyse complète des vulnérabilités',
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
      analytics: [],
      refresh: jest.fn(),
    };

    mockUseDashboard.mockReturnValue(mockData);

    render(<AuditTimeline />);
    expect(screen.getByText('20 décembre 2023')).toBeInTheDocument();
  });
}); 