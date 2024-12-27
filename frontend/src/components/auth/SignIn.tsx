import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Link,
  Divider,
  IconButton,
  InputAdornment,
  Alert,
  CircularProgress,
} from '@mui/material';
import { motion } from 'framer-motion';
import { Visibility, VisibilityOff, Google, GitHub } from '@mui/icons-material';
import { useNavigate, useLocation, Location } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

interface LocationState {
  from: {
    pathname: string;
  };
}

interface FormData {
  email: string;
  password: string;
}

interface ApiError {
  response?: {
    data?: {
      message?: string;
    };
  };
  message: string;
}

export const SignIn: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation() as Location & { state: LocationState };
  const { login, loginWithGoogle, loginWithGithub } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState<FormData>({
    email: '',
    password: '',
  });
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      await login(formData.email, formData.password);
      const from = location.state?.from?.pathname || '/dashboard';
      navigate(from, { replace: true });
    } catch (err) {
      const apiError = err as ApiError;
      setError(
        apiError.response?.data?.message ||
        apiError.message ||
        'Une erreur est survenue lors de la connexion. Veuillez réessayer.'
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
    } catch (err) {
      const apiError = err as ApiError;
      setError(
        apiError.response?.data?.message ||
        apiError.message ||
        `Erreur lors de la connexion avec ${provider}`
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
        background: 'linear-gradient(135deg, #1a237e 0%, #0d47a1 100%)',
        p: 3,
      }}
    >
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Paper
          elevation={24}
          sx={{
            p: 4,
            width: '100%',
            maxWidth: 400,
            borderRadius: 2,
            backdropFilter: 'blur(10px)',
            background: 'rgba(255, 255, 255, 0.95)',
          }}
        >
          <Typography variant="h4" align="center" sx={{ mb: 3, fontWeight: 'bold', color: '#1a237e' }}>
            AuditronAI
          </Typography>
          <Typography variant="h5" align="center" sx={{ mb: 4 }}>
            Connexion
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Email"
              name="email"
              type="email"
              variant="outlined"
              value={formData.email}
              onChange={handleChange}
              sx={{ mb: 3 }}
              required
              disabled={isLoading}
              inputProps={{
                'aria-label': 'email',
              }}
            />

            <TextField
              fullWidth
              label="Mot de passe"
              name="password"
              type={showPassword ? 'text' : 'password'}
              variant="outlined"
              value={formData.password}
              onChange={handleChange}
              sx={{ mb: 2 }}
              required
              disabled={isLoading}
              inputProps={{
                'aria-label': 'mot de passe',
              }}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                      disabled={isLoading}
                      aria-label={showPassword ? 'cacher le mot de passe' : 'montrer le mot de passe'}
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <Box sx={{ mb: 3, textAlign: 'right' }}>
              <Link
                component="button"
                type="button"
                onClick={() => navigate('/forgot-password')}
                underline="hover"
                sx={{ color: 'primary.main', cursor: 'pointer' }}
                disabled={isLoading}
              >
                Mot de passe oublié ?
              </Link>
            </Box>

            <Button
              fullWidth
              type="submit"
              variant="contained"
              size="large"
              disabled={isLoading}
              sx={{
                mb: 3,
                height: 48,
                background: 'linear-gradient(45deg, #1a237e 30%, #0d47a1 90%)',
                '&:hover': {
                  background: 'linear-gradient(45deg, #0d47a1 30%, #1a237e 90%)',
                },
              }}
            >
              {isLoading ? (
                <CircularProgress size={24} sx={{ color: 'white' }} />
              ) : (
                'Se connecter'
              )}
            </Button>
          </form>

          <Divider sx={{ mb: 3 }}>ou</Divider>

          <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<Google />}
              sx={{ height: 48 }}
              disabled={isLoading}
              onClick={() => handleSocialLogin('google')}
            >
              Google
            </Button>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<GitHub />}
              sx={{ height: 48 }}
              disabled={isLoading}
              onClick={() => handleSocialLogin('github')}
            >
              GitHub
            </Button>
          </Box>

          <Typography align="center" color="textSecondary">
            Pas encore de compte ?{' '}
            <Link
              component="button"
              type="button"
              onClick={() => navigate('/signup')}
              sx={{ cursor: 'pointer' }}
              underline="hover"
              disabled={isLoading}
            >
              S'inscrire
            </Link>
          </Typography>
        </Paper>
      </motion.div>
    </Box>
  );
}; 