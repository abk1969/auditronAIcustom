import React from 'react';
import { Box, Container, Typography, Link, Divider, Grid } from '@mui/material';
import FacebookIcon from '@mui/icons-material/Facebook';
import TwitterIcon from '@mui/icons-material/Twitter';
import LinkedInIcon from '@mui/icons-material/LinkedIn';

const Footer: React.FC = () => {
  return (
    <Box
      component="footer"
      sx={{
        py: 3,
        px: 2,
        mt: 'auto',
        backgroundColor: (theme) => theme.palette.grey[100]
      }}
    >
      <Container maxWidth="lg">
        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Typography variant="h6" color="text.primary" gutterBottom>
              AuditronAI
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Powered by Globacom3000
            </Typography>
            <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
              <Link href="https://facebook.com" target="_blank" color="inherit">
                <FacebookIcon />
              </Link>
              <Link href="https://twitter.com" target="_blank" color="inherit">
                <TwitterIcon />
              </Link>
              <Link href="https://linkedin.com" target="_blank" color="inherit">
                <LinkedInIcon />
              </Link>
            </Box>
          </Grid>

          <Grid item xs={12} md={4}>
            <Typography variant="h6" color="text.primary" gutterBottom>
              Mentions légales
            </Typography>
            <Link href="/legal/terms" color="inherit" display="block" sx={{ mb: 1 }}>
              Conditions d'utilisation
            </Link>
            <Link href="/legal/privacy" color="inherit" display="block" sx={{ mb: 1 }}>
              Politique de confidentialité
            </Link>
            <Link href="/legal/cookies" color="inherit" display="block">
              Gestion des cookies
            </Link>
          </Grid>

          <Grid item xs={12} md={4}>
            <Typography variant="h6" color="text.primary" gutterBottom>
              RGPD
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Conformément au Règlement Général sur la Protection des Données (RGPD), 
              nous nous engageons à protéger la confidentialité de vos données personnelles.
            </Typography>
            <Link href="/legal/gdpr" color="inherit">
              En savoir plus
            </Link>
          </Grid>
        </Grid>

        <Divider sx={{ my: 3 }} />
        
        <Typography variant="body2" color="text.secondary" align="center">
          © {new Date().getFullYear()} AuditronAI. Tous droits réservés.
        </Typography>
      </Container>
    </Box>
  );
};

export default Footer;
