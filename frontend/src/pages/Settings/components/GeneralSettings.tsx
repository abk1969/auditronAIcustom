"""Composant des paramètres généraux."""
import React from 'react';
import {
  Box,
  CircularProgress,
  FormControl,
  FormControlLabel,
  Switch,
  TextField,
  Button,
  Stack
} from '@mui/material';
import { useMutation } from 'react-query';
import { useNotification } from '../../../hooks/useNotification';
import { updateGeneralSettings } from '../../../services/api';

interface GeneralSettingsData {
  language: string;
  theme: 'light' | 'dark';
  notifications: boolean;
  autoUpdate: boolean;
  maxThreads: number;
}

interface GeneralSettingsProps {
  settings?: GeneralSettingsData;
  isLoading: boolean;
}

export const GeneralSettings: React.FC<GeneralSettingsProps> = ({
  settings,
  isLoading
}) => {
  const [formData, setFormData] = React.useState<GeneralSettingsData>({
    language: 'fr',
    theme: 'dark',
    notifications: true,
    autoUpdate: true,
    maxThreads: 4
  });

  const { showNotification } = useNotification();

  React.useEffect(() => {
    if (settings) {
      setFormData(settings);
    }
  }, [settings]);

  const { mutate: updateSettings, isLoading: isSaving } = useMutation(
    updateGeneralSettings,
    {
      onSuccess: () => {
        showNotification('Paramètres mis à jour', 'success');
      },
      onError: () => {
        showNotification('Erreur lors de la mise à jour', 'error');
      }
    }
  );

  const handleChange = (field: keyof GeneralSettingsData) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = event.target.type === 'checkbox'
      ? event.target.checked
      : event.target.value;

    setFormData((prev) => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    updateSettings(formData);
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <form onSubmit={handleSubmit}>
      <Stack spacing={3}>
        <FormControl fullWidth>
          <TextField
            label="Langue"
            value={formData.language}
            onChange={handleChange('language')}
            select
            SelectProps={{ native: true }}
          >
            <option value="fr">Français</option>
            <option value="en">English</option>
          </TextField>
        </FormControl>

        <FormControl fullWidth>
          <TextField
            label="Thème"
            value={formData.theme}
            onChange={handleChange('theme')}
            select
            SelectProps={{ native: true }}
          >
            <option value="light">Clair</option>
            <option value="dark">Sombre</option>
          </TextField>
        </FormControl>

        <FormControlLabel
          control={
            <Switch
              checked={formData.notifications}
              onChange={handleChange('notifications')}
            />
          }
          label="Activer les notifications"
        />

        <FormControlLabel
          control={
            <Switch
              checked={formData.autoUpdate}
              onChange={handleChange('autoUpdate')}
            />
          }
          label="Mise à jour automatique"
        />

        <FormControl fullWidth>
          <TextField
            label="Nombre maximum de threads"
            type="number"
            value={formData.maxThreads}
            onChange={handleChange('maxThreads')}
            inputProps={{ min: 1, max: 16 }}
          />
        </FormControl>

        <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            type="submit"
            variant="contained"
            disabled={isSaving}
          >
            {isSaving ? 'Enregistrement...' : 'Enregistrer'}
          </Button>
        </Box>
      </Stack>
    </form>
  );
}; 