"""Composant d'authentification avec support multi-méthodes."""
import React from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Divider,
  IconButton,
  InputAdornment,
  Alert,
  CircularProgress,
  Stack,
  Tabs,
  Tab,
  Link
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Google as GoogleIcon,
  GitHub as GitHubIcon,
  Email as EmailIcon,
  Key as KeyIcon
} from '@mui/icons-material';
import { useAuth } from '../../hooks/useAuth';
import { useNotification } from '../../hooks/useNotification';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, index, value }) => (
  <div role="tabpanel" hidden={value !== index}>
    {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
  </div>
);

export const Auth: React.FC = () => {
  const [tabValue, setTabValue] = React.useState(0);
  const [showPassword, setShowPassword] = React.useState(false);
  const [isLoading, setIsLoading] = React.useState(false);
  const [formData, setFormData] = React.useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: ''
  });

  const { login, register, loginWithGoogle, loginWithGithub } = useAuth();
  const { showNotification } = useNotification();

  const handleChange = (prop: keyof typeof formData) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData({ ...formData, [prop]: event.target.value });
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setIsLoading(true);

    try {
      if (tabValue === 0) {
        // Connexion
        await login(formData.email, formData.password);
        showNotification('Connexion réussie', 'success');
      } else {
        // Inscription
        if (formData.password !== formData.confirmPassword) {
          throw new Error('Les mots de passe ne correspondent pas');
        }
        await register(formData.email, formData.password, formData.name);
        showNotification('Inscription réussie', 'success');
      }
    } catch (error) {
      showNotification(
        error instanceof Error ? error.message : 'Une erreur est survenue',
        'error'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleSocialLogin = async (provider: 'google' | 'github') => {
    setIsLoading(true);
    try {
      if (provider === 'google') {
        await loginWithGoogle();
      } else {
        await loginWithGithub();
      }
      showNotification('Connexion réussie', 'success');
    } catch (error) {
      showNotification(
        'Erreur lors de la connexion sociale',
        'error'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default',
        py: 3
      }}
    >
      <Paper
        elevation={4}
        sx={{
          width: '100%',
          maxWidth: 480,
          p: 3,
          position: 'relative'
        }}
      >
        {isLoading && (
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              bgcolor: 'rgba(255, 255, 255, 0.8)',
              zIndex: 1
            }}
          >
            <CircularProgress />
          </Box>
        )}

        <Typography variant="h4" align="center" gutterBottom>
          AuditronAI
        </Typography>
        <Typography variant="subtitle1" align="center" color="text.secondary" sx={{ mb: 4 }}>
          Plateforme d'Analyse de Code IA
        </Typography>

        <Tabs
          value={tabValue}
          onChange={(_, newValue) => setTabValue(newValue)}
          variant="fullWidth"
          sx={{ mb: 3 }}
        >
          <Tab label="Connexion" />
          <Tab label="Inscription" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <form onSubmit={handleSubmit}>
            <Stack spacing={3}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={formData.email}
                onChange={handleChange('email')}
                required
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <EmailIcon />
                    </InputAdornment>
                  ),
                }}
              />

              <TextField
                fullWidth
                label="Mot de passe"
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={handleChange('password')}
                required
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <KeyIcon />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />

              <Button
                fullWidth
                type="submit"
                variant="contained"
                size="large"
                disabled={isLoading}
              >
                Se connecter
              </Button>
            </Stack>
          </form>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <form onSubmit={handleSubmit}>
            <Stack spacing={3}>
              <TextField
                fullWidth
                label="Nom"
                value={formData.name}
                onChange={handleChange('name')}
                required
              />

              <TextField
                fullWidth
                label="Email"
                type="email"
                value={formData.email}
                onChange={handleChange('email')}
                required
              />

              <TextField
                fullWidth
                label="Mot de passe"
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={handleChange('password')}
                required
              />

              <TextField
                fullWidth
                label="Confirmer le mot de passe"
                type={showPassword ? 'text' : 'password'}
                value={formData.confirmPassword}
                onChange={handleChange('confirmPassword')}
                required
              />

              <Button
                fullWidth
                type="submit"
                variant="contained"
                size="large"
                disabled={isLoading}
              >
                S'inscrire
              </Button>
            </Stack>
          </form>
        </TabPanel>

        <Box sx={{ mt: 3 }}>
          <Divider>
            <Typography variant="body2" color="text.secondary">
              Ou continuer avec
            </Typography>
          </Divider>

          <Stack
            direction="row"
            spacing={2}
            sx={{ mt: 2, justifyContent: 'center' }}
          >
            <Button
              variant="outlined"
              startIcon={<GoogleIcon />}
              onClick={() => handleSocialLogin('google')}
              disabled={isLoading}
            >
              Google
            </Button>
            <Button
              variant="outlined"
              startIcon={<GitHubIcon />}
              onClick={() => handleSocialLogin('github')}
              disabled={isLoading}
            >
              GitHub
            </Button>
          </Stack>
        </Box>

        <Typography
          variant="body2"
          align="center"
          sx={{ mt: 3 }}
        >
          {tabValue === 0 ? (
            <>
              Pas encore de compte ?{' '}
              <Link
                component="button"
                variant="body2"
                onClick={() => setTabValue(1)}
              >
                S'inscrire
              </Link>
            </>
          ) : (
            <>
              Déjà un compte ?{' '}
              <Link
                component="button"
                variant="body2"
                onClick={() => setTabValue(0)}
              >
                Se connecter
              </Link>
            </>
          )}
        </Typography>
      </Paper>
    </Box>
  );
}; 