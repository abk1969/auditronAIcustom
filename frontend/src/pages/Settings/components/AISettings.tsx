"""Composant des paramètres IA."""
import React from 'react';
import {
  Box,
  CircularProgress,
  FormControl,
  TextField,
  Button,
  Stack,
  Slider,
  Typography,
  FormControlLabel,
  Switch,
  Card,
  CardContent,
  CardActionArea,
  Grid,
  Chip,
  Tooltip,
  IconButton,
  Collapse,
  Alert,
  Divider,
  TableContainer,
  Paper,
  Table,
  TableHead,
  TableRow,
  TableBody,
  TableCell
} from '@mui/material';
import { useMutation } from 'react-query';
import { useNotification } from '../../../hooks/useNotification';
import { updateAISettings } from '../../../services/api';
import {
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  Psychology as PsychologyIcon,
  Info as InfoIcon,
  Check as CheckIcon,
  VisibilityOff as VisibilityOffIcon,
  CompareArrows as CompareArrowsIcon
} from '@mui/icons-material';

interface AIModelFeatures {
  speed: 'ultra' | 'fast' | 'standard';
  specialization: string[];
  costPerToken: number;
  supportedLanguages: string[];
}

interface AIModel {
  id: string;
  name: string;
  provider: string;
  description: string;
  maxTokens: number;
  features: AIModelFeatures;
}

const AI_MODELS: AIModel[] = [
  {
    id: 'gemini-2.0-flash-thinking-exp-1219',
    name: 'Gemini 2.0 Flash Thinking',
    provider: 'Google',
    description: 'Modèle expérimental optimisé pour la rapidité et la précision',
    maxTokens: 16384,
    features: {
      speed: 'ultra',
      specialization: ['Analyse de code', 'Optimisation', 'Debugging'],
      costPerToken: 0.0001,
      supportedLanguages: ['Python', 'JavaScript', 'Java', 'C++', 'Go']
    }
  },
  {
    id: 'mistral-large-latest',
    name: 'Mistral Large',
    provider: 'Mistral AI',
    description: 'Dernière version du modèle large de Mistral',
    maxTokens: 8192
  },
  {
    id: 'gpt-4o-mini',
    name: 'GPT-4 Optimized Mini',
    provider: 'OpenAI',
    description: 'Version optimisée et compacte de GPT-4',
    maxTokens: 4096
  },
  {
    id: 'llama3-latest',
    name: 'Llama 3',
    provider: 'Ollama',
    description: 'Dernière version de Llama 3 via Ollama',
    maxTokens: 4096
  }
];

interface AISettingsData {
  model: string;
  temperature: number;
  maxTokens: number;
  contextWindow: number;
  streamResponse: boolean;
  useCache: boolean;
  apiKey: string;
  customEndpoint?: string; // Pour Ollama
}

interface AISettingsProps {
  settings?: AISettingsData;
  isLoading: boolean;
}

interface ModelCardProps {
  model: AIModel;
  selected: boolean;
  onSelect: () => void;
}

const ModelCard: React.FC<ModelCardProps> = ({ model, selected, onSelect }) => {
  const [showInfo, setShowInfo] = React.useState(false);
  const [showDetails, setShowDetails] = React.useState(false);

  return (
    <Card 
      sx={{ 
        height: '100%',
        border: selected ? 2 : 1,
        borderColor: selected ? 'primary.main' : 'divider',
        position: 'relative'
      }}
    >
      <CardActionArea onClick={onSelect} sx={{ height: '100%' }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <Typography variant="h6" gutterBottom>
              {model.name}
            </Typography>
            {selected && (
              <Chip
                icon={<CheckIcon />}
                label="Actif"
                color="primary"
                size="small"
              />
            )}
          </Box>

          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            {model.provider}
          </Typography>

          <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Tooltip title="Vitesse de traitement">
              <Chip
                icon={<SpeedIcon />}
                label={model.id.includes('flash') ? 'Ultra rapide' : 'Standard'}
                size="small"
                variant="outlined"
              />
            </Tooltip>
            <Tooltip title="Taille du contexte">
              <Chip
                icon={<MemoryIcon />}
                label={`${model.maxTokens} tokens`}
                size="small"
                variant="outlined"
              />
            </Tooltip>
            <Tooltip title="Capacités">
              <Chip
                icon={<PsychologyIcon />}
                label={model.id.includes('large') ? 'Avancées' : 'Standard'}
                size="small"
                variant="outlined"
              />
            </Tooltip>
          </Box>

          <Box sx={{ mt: 2 }}>
            {model.features.specialization.map((spec) => (
              <Chip
                key={spec}
                label={spec}
                size="small"
                sx={{ m: 0.5 }}
              />
            ))}
          </Box>

          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              setShowInfo(!showInfo);
            }}
            sx={{ position: 'absolute', bottom: 8, right: 8 }}
          >
            <InfoIcon />
          </IconButton>
        </CardContent>
      </CardActionArea>

      <Collapse in={showInfo}>
        <Alert severity="info" sx={{ m: 1 }}>
          <Stack spacing={1}>
            <Typography variant="body2">
              {model.description}
            </Typography>
            <Divider />
            <Typography variant="subtitle2">
              Langages supportés :
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
              {model.features.supportedLanguages.map((lang) => (
                <Chip
                  key={lang}
                  label={lang}
                  size="small"
                  variant="outlined"
                />
              ))}
            </Box>
            <Typography variant="caption" color="text.secondary">
              Coût estimé : {model.features.costPerToken} $ / token
            </Typography>
          </Stack>
        </Alert>
      </Collapse>
    </Card>
  );
};

const ModelComparison: React.FC<{
  models: AIModel[];
  selectedModel: string;
}> = ({ models, selectedModel }) => {
  return (
    <Box sx={{ mt: 2 }}>
      <Typography variant="subtitle2" gutterBottom>
        Comparaison des Performances
      </Typography>
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Caractéristique</TableCell>
              {models.map(model => (
                <TableCell key={model.id} align="center">
                  {model.name}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            <TableRow>
              <TableCell>Vitesse</TableCell>
              {models.map(model => (
                <TableCell key={model.id} align="center">
                  <Chip
                    size="small"
                    label={model.features.speed}
                    color={model.features.speed === 'ultra' ? 'success' : 'default'}
                  />
                </TableCell>
              ))}
            </TableRow>
            {/* Autres caractéristiques... */}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export const AISettings: React.FC<AISettingsProps> = ({
  settings,
  isLoading
}) => {
  const [formData, setFormData] = React.useState<AISettingsData>({
    model: 'gemini-2.0-flash-thinking-exp-1219',
    temperature: 0.7,
    maxTokens: 2048,
    contextWindow: 4096,
    streamResponse: true,
    useCache: true,
    apiKey: '',
    customEndpoint: ''
  });

  const { showNotification } = useNotification();

  React.useEffect(() => {
    if (settings) {
      setFormData(settings);
    }
  }, [settings]);

  const { mutate: updateSettings, isLoading: isSaving } = useMutation(
    updateAISettings,
    {
      onSuccess: () => {
        showNotification('Configuration IA mise à jour', 'success');
      },
      onError: () => {
        showNotification('Erreur lors de la mise à jour', 'error');
      }
    }
  );

  const handleChange = (field: keyof AISettingsData) => (
    event: React.ChangeEvent<HTMLInputElement> | any
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

  const [showComparison, setShowComparison] = React.useState(false);

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
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">
            Sélection du Modèle IA
          </Typography>
          <Button
            size="small"
            onClick={() => setShowComparison(!showComparison)}
            startIcon={showComparison ? <VisibilityOffIcon /> : <CompareArrowsIcon />}
          >
            {showComparison ? 'Masquer' : 'Comparer'} les modèles
          </Button>
        </Box>

        <Collapse in={showComparison}>
          <ModelComparison
            models={AI_MODELS}
            selectedModel={formData.model}
          />
        </Collapse>

        <Grid container spacing={2}>
          {AI_MODELS.map((model) => (
            <Grid item xs={12} sm={6} key={model.id}>
              <ModelCard
                model={model}
                selected={formData.model === model.id}
                onSelect={() => handleChange('model')({ target: { value: model.id } })}
              />
            </Grid>
          ))}
        </Grid>

        {formData.model === 'llama3-latest' && (
          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Configuration Ollama requise
            </Typography>
            <FormControl fullWidth sx={{ mt: 1 }}>
              <TextField
                label="Point d'accès Ollama"
                value={formData.customEndpoint}
                onChange={handleChange('customEndpoint')}
                placeholder="http://localhost:11434"
                helperText="URL du serveur Ollama local ou distant"
                size="small"
              />
            </FormControl>
          </Alert>
        )}

        <Divider sx={{ my: 3 }} />

        <Typography variant="h6" gutterBottom>
          Paramètres Avancés
        </Typography>

        <Box>
          <Typography gutterBottom>
            Température (Créativité): {formData.temperature}
          </Typography>
          <Slider
            value={formData.temperature}
            onChange={(_, value) => handleChange('temperature')({ target: { value } })}
            min={0}
            max={1}
            step={0.1}
            marks
            valueLabelDisplay="auto"
          />
        </Box>

        <FormControl fullWidth>
          <TextField
            label="Tokens maximum"
            type="number"
            value={formData.maxTokens}
            onChange={handleChange('maxTokens')}
            inputProps={{
              min: 256,
              max: AI_MODELS.find(m => m.id === formData.model)?.maxTokens || 8192
            }}
            helperText={`Maximum pour ${AI_MODELS.find(m => m.id === formData.model)?.name}: ${AI_MODELS.find(m => m.id === formData.model)?.maxTokens}`}
          />
        </FormControl>

        <FormControl fullWidth>
          <TextField
            label="Fenêtre de contexte"
            type="number"
            value={formData.contextWindow}
            onChange={handleChange('contextWindow')}
            inputProps={{ min: 1024, max: 8192 }}
          />
        </FormControl>

        <FormControlLabel
          control={
            <Switch
              checked={formData.streamResponse}
              onChange={handleChange('streamResponse')}
            />
          }
          label="Réponse en streaming"
        />

        <FormControlLabel
          control={
            <Switch
              checked={formData.useCache}
              onChange={handleChange('useCache')}
            />
          }
          label="Utiliser le cache"
        />

        <FormControl fullWidth>
          <TextField
            label="Clé API"
            type="password"
            value={formData.apiKey}
            onChange={handleChange('apiKey')}
            autoComplete="off"
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