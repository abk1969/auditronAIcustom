import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Link,
  Alert,
  CircularProgress,
} from '@mui/material';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import EmailIcon from '@mui/icons-material/Email';
import { useAuth } from '../../hooks/useAuth';
import api from '../../services/api';

interface Status {
  type: 'success' | 'error' | null;
  message: string;
}

interface ApiError {
  response?: {
    data?: {
      message?: string;
    };
  };
  message: string;
}

export const ForgotPassword: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<Status>({ type: null, message: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validateEmail = (email: string): boolean => {
    return /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(email);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) {
      setStatus({
        type: 'error',
        message: 'Veuillez entrer votre adresse email',
      });
      return;
    }

    if (!validateEmail(email)) {
      setStatus({
        type: 'error',
        message: 'Veuillez entrer une adresse email valide',
      });
      return;
    }

    setIsSubmitting(true);
    setStatus({ type: null, message: '' });

    try {
      await api.post('/auth/reset-password', { email });
      setStatus({
        type: 'success',
        message: 'Un email de réinitialisation a été envoyé à votre adresse',
      });
      setTimeout(() => {
        navigate('/signin');
      }, 3000);
    } catch (err) {
      const apiError = err as ApiError;
      setStatus({
        type: 'error',
        message: apiError.response?.data?.message ||
                apiError.message ||
                'Une erreur est survenue. Veuillez réessayer.',
      });
    } finally {
      setIsSubmitting(false);
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
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              mb: 3,
            }}
          >
            <EmailIcon
              sx={{
                fontSize: 48,
                color: 'primary.main',
                mb: 2,
              }}
            />
            <Typography variant="h4" align="center" sx={{ fontWeight: 'bold', color: '#1a237e' }}>
              Mot de passe oublié ?
            </Typography>
            <Typography variant="body1" align="center" color="textSecondary" sx={{ mt: 2 }}>
              Entrez votre adresse email pour recevoir un lien de réinitialisation
            </Typography>
          </Box>

          {status.type && (
            <Alert severity={status.type} sx={{ mb: 3 }}>
              {status.message}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Email"
              type="email"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                setStatus({ type: null, message: '' });
              }}
              sx={{ mb: 3 }}
              required
              disabled={isSubmitting}
              inputProps={{
                'aria-label': 'email',
              }}
            />

            <Button
              fullWidth
              type="submit"
              variant="contained"
              size="large"
              disabled={isSubmitting}
              sx={{
                mb: 3,
                height: 48,
                background: 'linear-gradient(45deg, #1a237e 30%, #0d47a1 90%)',
                '&:hover': {
                  background: 'linear-gradient(45deg, #0d47a1 30%, #1a237e 90%)',
                },
              }}
            >
              {isSubmitting ? (
                <CircularProgress size={24} sx={{ color: 'white' }} />
              ) : (
                'Envoyer le lien'
              )}
            </Button>
          </form>

          <Typography align="center">
            <Link
              component="button"
              type="button"
              onClick={() => navigate('/signin')}
              sx={{ cursor: 'pointer' }}
              underline="hover"
              disabled={isSubmitting}
            >
              Retour à la connexion
            </Link>
          </Typography>
        </Paper>
      </motion.div>
    </Box>
  );
}; 