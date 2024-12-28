import React, { useState, useCallback } from 'react';
import { Box, Button, Card, Typography, CircularProgress, List, ListItem, ListItemIcon, ListItemText, IconButton } from '@mui/material';
import { UploadFile, CheckCircle, Error as ErrorIcon, Close as CloseIcon } from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';

interface UploadedFile {
  file: File;
  status: 'pending' | 'uploading' | 'success' | 'error';
  error?: string;
}

const CodeUpload: React.FC = () => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      status: 'pending' as const,
    }));
    setFiles(prev => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/*': ['.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.cpp', '.c', '.h', '.cs', '.php', '.rb'],
    },
    multiple: true,
  });

  const handleUpload = async () => {
    setIsUploading(true);
    
    try {
      const formData = new FormData();
      files.forEach(({ file }) => {
        formData.append('files', file);
      });

      const response = await fetch('/api/analysis/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Erreur lors de l\'upload des fichiers');
      }

      setFiles(prev => prev.map(file => ({ ...file, status: 'success' })));
      
      // Redirection vers la page d'analyse après un upload réussi
      // window.location.href = '/analysis/results';
    } catch (error) {
      setFiles(prev => prev.map(file => ({
        ...file,
        status: 'error',
        error: 'Échec de l\'upload',
      })));
    } finally {
      setIsUploading(false);
    }
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <Card sx={{ p: 4, m: 2 }}>
      <Box
        {...getRootProps()}
        sx={{
          width: '100%',
          minHeight: 200,
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.300',
          borderRadius: 2,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          p: 3,
          cursor: 'pointer',
          transition: 'all 0.2s ease',
          '&:hover': {
            borderColor: 'primary.main',
            backgroundColor: 'action.hover',
          },
        }}
      >
        <input {...getInputProps()} />
        <UploadFile sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          {isDragActive
            ? 'Déposez les fichiers ici'
            : 'Glissez-déposez vos fichiers de code ici'}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          ou cliquez pour sélectionner des fichiers
        </Typography>
        <Typography variant="caption" color="textSecondary" sx={{ mt: 1 }}>
          Formats supportés: .js, .jsx, .ts, .tsx, .py, .java, .cpp, .c, .h, .cs, .php, .rb
        </Typography>
      </Box>

      {files.length > 0 && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Fichiers sélectionnés
          </Typography>
          <List>
            {files.map((file, index) => (
              <ListItem
                key={file.file.name}
                secondaryAction={
                  <IconButton edge="end" onClick={() => removeFile(index)}>
                    <CloseIcon />
                  </IconButton>
                }
              >
                <ListItemIcon>
                  {file.status === 'success' && <CheckCircle color="success" />}
                  {file.status === 'error' && <ErrorIcon color="error" />}
                  {(file.status === 'pending' || file.status === 'uploading') && <UploadFile color="primary" />}
                </ListItemIcon>
                <ListItemText
                  primary={file.file.name}
                  secondary={file.error || `${(file.file.size / 1024).toFixed(1)} KB`}
                />
              </ListItem>
            ))}
          </List>

          <Button
            variant="contained"
            color="primary"
            onClick={handleUpload}
            disabled={isUploading || files.length === 0}
            sx={{ mt: 2 }}
          >
            {isUploading ? (
              <>
                <CircularProgress size={24} sx={{ mr: 1 }} color="inherit" />
                Upload en cours...
              </>
            ) : (
              'Lancer l\'analyse'
            )}
          </Button>
        </Box>
      )}
    </Card>
  );
};

export default CodeUpload; 