import React from 'react';
import { Box, Container, Toolbar } from '@mui/material';
import Header from './Header';
import Footer from './Footer';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header />
      
      {/* Toolbar vide pour compenser la hauteur du Header fixe */}
      <Toolbar />
      
      {/* Contenu principal */}
      <Box
        component="main"
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          bgcolor: 'background.default',
          py: 4
        }}
      >
        <Container maxWidth="lg" sx={{ flex: 1 }}>
          {children}
        </Container>
      </Box>

      <Footer />
    </Box>
  );
};

export default Layout;
