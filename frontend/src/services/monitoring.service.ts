import * as Sentry from '@sentry/react';

interface ApiMetric {
  endpoint: string;
  method: string;
  duration: number;
  status: number;
  timestamp: number;
}

class MonitoringService {
  private metrics: ApiMetric[] = [];
  private isInitialized = false;

  initialize() {
    if (this.isInitialized) return;

    // Initialisation de Sentry
    if (process.env.REACT_APP_SENTRY_DSN) {
      Sentry.init({
        dsn: process.env.REACT_APP_SENTRY_DSN,
        environment: process.env.NODE_ENV,
        tracesSampleRate: 1.0,
      });
    }

    // Initialisation de Google Analytics
    if (process.env.REACT_APP_ANALYTICS_ID) {
      // Code d'initialisation de GA ici
    }

    this.isInitialized = true;
  }

  logApiCall(metric: ApiMetric) {
    this.metrics.push(metric);

    // Envoi à Sentry si c'est une erreur
    if (metric.status >= 400) {
      Sentry.captureMessage(`API Error: ${metric.method} ${metric.endpoint}`, {
        level: metric.status >= 500 ? 'error' : 'warning',
        extra: metric,
      });
    }

    // Envoi à Google Analytics
    if (window.gtag && process.env.REACT_APP_ENABLE_ANALYTICS === 'true') {
      window.gtag('event', 'api_call', {
        event_category: 'API',
        event_label: `${metric.method} ${metric.endpoint}`,
        value: metric.duration,
      });
    }

    // Nettoyage des anciennes métriques (garder seulement les dernières 24h)
    const oneDayAgo = Date.now() - 24 * 60 * 60 * 1000;
    this.metrics = this.metrics.filter((m) => m.timestamp > oneDayAgo);
  }

  getMetrics(timeRange: 'hour' | 'day' | 'week' = 'day') {
    const now = Date.now();
    const ranges = {
      hour: now - 60 * 60 * 1000,
      day: now - 24 * 60 * 60 * 1000,
      week: now - 7 * 24 * 60 * 60 * 1000,
    };

    const filteredMetrics = this.metrics.filter(
      (m) => m.timestamp > ranges[timeRange]
    );

    return {
      totalCalls: filteredMetrics.length,
      averageDuration: this.calculateAverageDuration(filteredMetrics),
      errorRate: this.calculateErrorRate(filteredMetrics),
      statusDistribution: this.calculateStatusDistribution(filteredMetrics),
      endpointPerformance: this.calculateEndpointPerformance(filteredMetrics),
    };
  }

  private calculateAverageDuration(metrics: ApiMetric[]) {
    if (metrics.length === 0) return 0;
    const total = metrics.reduce((sum, m) => sum + m.duration, 0);
    return total / metrics.length;
  }

  private calculateErrorRate(metrics: ApiMetric[]) {
    if (metrics.length === 0) return 0;
    const errors = metrics.filter((m) => m.status >= 400).length;
    return (errors / metrics.length) * 100;
  }

  private calculateStatusDistribution(metrics: ApiMetric[]) {
    return metrics.reduce((acc, m) => {
      const statusGroup = Math.floor(m.status / 100) * 100;
      acc[statusGroup] = (acc[statusGroup] || 0) + 1;
      return acc;
    }, {} as Record<number, number>);
  }

  private calculateEndpointPerformance(metrics: ApiMetric[]) {
    const endpointStats = new Map<string, { total: number; count: number }>();

    metrics.forEach((m) => {
      const key = `${m.method} ${m.endpoint}`;
      const current = endpointStats.get(key) || { total: 0, count: 0 };
      endpointStats.set(key, {
        total: current.total + m.duration,
        count: current.count + 1,
      });
    });

    const result: Record<string, number> = {};
    endpointStats.forEach((stats, endpoint) => {
      result[endpoint] = stats.total / stats.count;
    });

    return result;
  }

  captureError(error: Error, context?: Record<string, any>) {
    Sentry.captureException(error, {
      extra: context,
    });
  }

  setUser(user: { id: string; email: string }) {
    Sentry.setUser(user);
  }

  clearUser() {
    Sentry.setUser(null);
  }
}

export const monitoringService = new MonitoringService(); 