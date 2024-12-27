import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Link,
  Slide,
  Stack,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import CookieIcon from '@mui/icons-material/Cookie';

const COOKIE_CONSENT_KEY = 'cookie-consent-status';

export const CookieBanner: React.FC = () => {
  const [isVisible, setIsVisible] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  useEffect(() => {
    const consentStatus = localStorage.getItem(COOKIE_CONSENT_KEY);
    if (!consentStatus) {
      const timer = setTimeout(() => {
        setIsVisible(true);
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, []);

  const handleAccept = () => {
    localStorage.setItem(COOKIE_CONSENT_KEY, 'accepted');
    setIsVisible(false);
  };

  const handleDecline = () => {
    localStorage.setItem(COOKIE_CONSENT_KEY, 'declined');
    setIsVisible(false);
  };

  if (!isVisible) return null;

  return (
    <Slide direction="up" in={isVisible} mountOnEnter unmountOnExit>
      <Box
        sx={{
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          zIndex: 9999,
          p: 2,
          background: 'rgba(0, 0, 0, 0.5)',
          backdropFilter: 'blur(10px)',
        }}
      >
        <Paper
          elevation={6}
          sx={{
            maxWidth: 1200,
            mx: 'auto',
            p: 3,
            borderRadius: 2,
            background: 'rgba(255, 255, 255, 0.95)',
          }}
        >
          <Stack
            direction={isMobile ? 'column' : 'row'}
            spacing={3}
            alignItems={isMobile ? 'stretch' : 'center'}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1 }}>
              <CookieIcon
                sx={{
                  fontSize: 40,
                  color: 'primary.main',
                }}
              />
              <Box>
                <Typography variant="h6" gutterBottom>
                  Nous utilisons des cookies 🍪
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Nous utilisons des cookies et des technologies similaires pour améliorer votre
                  expérience sur notre site. Consultez notre{' '}
                  <Link href="/privacy" underline="hover">
                    politique de confidentialité
                  </Link>{' '}
                  pour en savoir plus.
                </Typography>
              </Box>
            </Box>

            <Stack
              direction={isMobile ? 'column' : 'row'}
              spacing={2}
              sx={{ minWidth: isMobile ? 'auto' : 300 }}
            >
              <Button
                variant="outlined"
                onClick={handleDecline}
                sx={{
                  height: 42,
                  flex: 1,
                }}
              >
                Refuser
              </Button>
              <Button
                variant="contained"
                onClick={handleAccept}
                sx={{
                  height: 42,
                  flex: 1,
                  background: 'linear-gradient(45deg, #1a237e 30%, #0d47a1 90%)',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #0d47a1 30%, #1a237e 90%)',
                  },
                }}
              >
                Accepter
              </Button>
            </Stack>
          </Stack>
        </Paper>
      </Box>
    </Slide>
  );
}; 