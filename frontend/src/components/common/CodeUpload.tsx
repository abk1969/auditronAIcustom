import React, { useState, useCallback } from 'react';
import {
  Box,
  Button,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  TextField,
} from '@mui/material';
import { CloudUpload, Code } from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import api from '../../services/api';

interface CodeUploadProps {
  onUploadSuccess?: (analysisId: string) => void;
  onUploadError?: (error: string) => void;
}

export const CodeUpload: React.FC<CodeUploadProps> = ({
  onUploadSuccess,
  onUploadError,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [repoUrl, setRepoUrl] = useState('');

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', acceptedFiles[0]);

    try {
      const response = await api.post<{ data: { id: string } }>('/analysis/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      onUploadSuccess?.(response.data.data.id);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Une erreur est survenue lors de l\'upload';
      setError(errorMessage);
      onUploadError?.(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [onUploadSuccess, onUploadError]);

  const handleRepoSubmit = async () => {
    if (!repoUrl) return;

    setLoading(true);
    setError(null);

    try {
      const response = await api.post<{ data: { id: string } }>('/analysis/repository', {
        url: repoUrl,
      });

      onUploadSuccess?.(response.data.data.id);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Une erreur est survenue avec l\'URL du dépôt';
      setError(errorMessage);
      onUploadError?.(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/*': ['.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.cpp', '.c', '.h', '.cs', '.php', '.rb'],
      'application/x-zip-compressed': ['.zip'],
      'application/zip': ['.zip'],
    },
    maxSize: 50 * 1024 * 1024, // 50MB max
  });

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Analyser votre Code
      </Typography>

      <Paper
        sx={{
          p: 3,
          mb: 3,
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.300',
          bgcolor: isDragActive ? 'action.hover' : 'background.paper',
          cursor: 'pointer',
        }}
        {...getRootProps()}
      >
        <input {...getInputProps()} />
        <Box
          display="flex"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          minHeight={200}
        >
          {loading ? (
            <CircularProgress />
          ) : (
            <>
              <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Glissez-déposez vos fichiers ici
              </Typography>
              <Typography color="textSecondary">
                ou cliquez pour sélectionner des fichiers
              </Typography>
              <Typography variant="caption" color="textSecondary" sx={{ mt: 1 }}>
                Formats supportés: JS, TS, Python, Java, C++, C#, PHP, Ruby (Max: 50MB)
              </Typography>
            </>
          )}
        </Box>
      </Paper>

      <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
        Ou analysez un dépôt Git
      </Typography>

      <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
        <TextField
          fullWidth
          label="URL du dépôt Git"
          variant="outlined"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          placeholder="https://github.com/username/repository"
          disabled={loading}
        />
        <Button
          variant="contained"
          startIcon={<Code />}
          onClick={handleRepoSubmit}
          disabled={loading || !repoUrl}
        >
          Analyser
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Box>
  );
}; 