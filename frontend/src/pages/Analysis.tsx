import React from 'react';
import { Container, Typography, Box } from '@mui/material';
import CodeUpload from '../components/analysis/CodeUpload';

const Analysis: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Analyse de Code
        </Typography>
        <Typography variant="body1" color="text.secondary" align="center" sx={{ mb: 4 }}>
          Téléchargez vos fichiers de code pour une analyse de sécurité approfondie
        </Typography>
        <CodeUpload />
      </Box>
    </Container>
  );
};

export default Analysis; 