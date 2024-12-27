"""Page d'analyse de code."""
import React from 'react';
import { Box, Paper, Typography, Button, CircularProgress } from '@mui/material';
import { useMutation } from 'react-query';

import { CodeEditor } from './components/CodeEditor';
import { AnalysisResults } from './components/AnalysisResults';
import { analyzeCode } from '../../services/api';
import { useNotification } from '../../hooks/useNotification';

export const CodeAnalysis: React.FC = () => {
  const [code, setCode] = React.useState('');
  const { showNotification } = useNotification();

  const { mutate: analyze, isLoading } = useMutation(analyzeCode, {
    onSuccess: (data) => {
      showNotification('Analyse terminée', 'success');
    },
    onError: (error) => {
      showNotification('Erreur lors de l\'analyse', 'error');
    }
  });

  const handleAnalyze = () => {
    if (!code.trim()) {
      showNotification('Veuillez entrer du code à analyser', 'warning');
      return;
    }
    analyze({ code });
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Analyse de Code
      </Typography>

      <Paper sx={{ p: 2, mb: 3 }}>
        <CodeEditor
          value={code}
          onChange={setCode}
          language="python"
          height="400px"
        />
        
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            variant="contained"
            color="primary"
            onClick={handleAnalyze}
            disabled={isLoading}
            startIcon={isLoading ? <CircularProgress size={20} /> : null}
          >
            {isLoading ? 'Analyse en cours...' : 'Analyser'}
          </Button>
        </Box>
      </Paper>

      <AnalysisResults />
    </Box>
  );
}; 