export const config = {
  api: {
    baseUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
    timeout: 30000,
  },
  auth: {
    tokenKey: 'auth_token',
    refreshTokenKey: 'refresh_token',
    googleClientId: process.env.REACT_APP_GOOGLE_CLIENT_ID,
    githubClientId: process.env.REACT_APP_GITHUB_CLIENT_ID,
  },
  app: {
    name: 'AuditronAI',
    version: '1.0.0',
    description: 'Plateforme d\'audit et d\'analyse de code intelligente',
    defaultLanguage: 'fr',
    supportedLanguages: ['fr', 'en'],
    defaultTheme: 'light' as const,
    routes: {
      home: '/',
      signin: '/signin',
      signup: '/signup',
      forgotPassword: '/forgot-password',
      resetPassword: '/reset-password',
      verifyEmail: '/verify-email',
      dashboard: '/dashboard',
      analysis: '/analysis',
      monitoring: '/monitoring',
      settings: '/settings',
    },
  },
  features: {
    socialLogin: true,
    emailVerification: true,
    twoFactorAuth: false,
    darkMode: true,
    notifications: true,
  },
  validation: {
    password: {
      minLength: 8,
      requireUppercase: true,
      requireLowercase: true,
      requireNumbers: true,
      requireSpecialChars: true,
    },
    session: {
      tokenExpiration: 3600, // 1 hour
      refreshTokenExpiration: 604800, // 1 week
    },
  },
  monitoring: {
    errorReporting: true,
    analytics: true,
    performanceMonitoring: true,
  },
} as const;

export type Config = typeof config;
export type AppRoutes = typeof config.app.routes;

export default config; 