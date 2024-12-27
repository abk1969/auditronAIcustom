import React, { useState } from 'react';
import { Box, Container, Typography, Paper, Alert } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { CodeUpload } from '../components/common/CodeUpload';

const CodeAnalysis: React.FC = () => {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);

  const handleUploadSuccess = (analysisId: string) => {
    // Rediriger vers la page de résultats d'analyse
    navigate(`/analysis/${analysisId}`);
  };

  const handleUploadError = (errorMessage: string) => {
    setError(errorMessage);
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Analyse de Code
        </Typography>
        
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="body1" paragraph>
            Soumettez votre code pour une analyse approfondie de la sécurité, 
            de la qualité et des performances. Vous pouvez soit uploader directement 
            vos fichiers, soit fournir l'URL d'un dépôt Git public.
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <CodeUpload
            onUploadSuccess={handleUploadSuccess}
            onUploadError={handleUploadError}
          />
        </Paper>
      </Box>
    </Container>
  );
};

export default CodeAnalysis; 