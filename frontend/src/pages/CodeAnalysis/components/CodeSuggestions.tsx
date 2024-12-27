"""Composant de suggestions de code en temps réel."""
import React from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Tooltip,
  Collapse,
  Button,
  Chip,
  Divider
} from '@mui/material';
import {
  Lightbulb as SuggestionIcon,
  Code as CodeIcon,
  Check as ApplyIcon,
  ExpandMore,
  ExpandLess,
  Info as InfoIcon,
  AutoFix as FixIcon
} from '@mui/icons-material';

interface CodeSuggestion {
  id: string;
  type: 'refactor' | 'style' | 'performance' | 'security';
  title: string;
  description: string;
  originalCode: string;
  suggestedCode: string;
  impact: 'high' | 'medium' | 'low';
  confidence: number;
  location: {
    file: string;
    startLine: number;
    endLine: number;
  };
}

interface CodeSuggestionsProps {
  suggestions: CodeSuggestion[];
  onApplySuggestion: (suggestionId: string) => void;
  onApplyAll: () => void;
  isLoading?: boolean;
}

const SuggestionTypeIcon: React.FC<{ type: string }> = ({ type }) => {
  switch (type) {
    case 'refactor':
      return <FixIcon color="primary" />;
    case 'style':
      return <CodeIcon color="info" />;
    case 'performance':
      return <SuggestionIcon color="warning" />;
    case 'security':
      return <InfoIcon color="error" />;
    default:
      return <SuggestionIcon />;
  }
};

export const CodeSuggestions: React.FC<CodeSuggestionsProps> = ({
  suggestions,
  onApplySuggestion,
  onApplyAll,
  isLoading
}) => {
  const [expandedId, setExpandedId] = React.useState<string | null>(null);
  const [selectedType, setSelectedType] = React.useState<string | null>(null);

  const suggestionTypes = Array.from(new Set(suggestions.map(s => s.type)));
  const filteredSuggestions = selectedType
    ? suggestions.filter(s => s.type === selectedType)
    : suggestions;

  const handleToggle = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Suggestions d'Amélioration ({suggestions.length})
        </Typography>
        <Button
          variant="contained"
          color="primary"
          onClick={onApplyAll}
          startIcon={<ApplyIcon />}
          disabled={suggestions.length === 0}
        >
          Appliquer Toutes
        </Button>
      </Box>

      <Box sx={{ mb: 2, display: 'flex', gap: 1 }}>
        {suggestionTypes.map(type => (
          <Chip
            key={type}
            label={type.charAt(0).toUpperCase() + type.slice(1)}
            icon={<SuggestionTypeIcon type={type} />}
            onClick={() => setSelectedType(selectedType === type ? null : type)}
            variant={selectedType === type ? 'filled' : 'outlined'}
            color={selectedType === type ? 'primary' : 'default'}
          />
        ))}
      </Box>

      <List>
        {filteredSuggestions.map((suggestion, index) => (
          <React.Fragment key={suggestion.id}>
            {index > 0 && <Divider />}
            <ListItem
              button
              onClick={() => handleToggle(suggestion.id)}
              sx={{ flexDirection: 'column', alignItems: 'stretch' }}
            >
              <Box sx={{ display: 'flex', width: '100%', alignItems: 'center' }}>
                <ListItemIcon>
                  <SuggestionTypeIcon type={suggestion.type} />
                </ListItemIcon>
                <ListItemText
                  primary={suggestion.title}
                  secondary={`${suggestion.location.file}:${suggestion.location.startLine}`}
                />
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Chip
                    size="small"
                    label={`${suggestion.confidence}% confiance`}
                    color={suggestion.confidence > 80 ? 'success' : 'warning'}
                  />
                  <Chip
                    size="small"
                    label={suggestion.impact}
                    color={
                      suggestion.impact === 'high' ? 'error' :
                      suggestion.impact === 'medium' ? 'warning' : 'info'
                    }
                  />
                  {expandedId === suggestion.id ? <ExpandLess /> : <ExpandMore />}
                </Box>
              </Box>

              <Collapse in={expandedId === suggestion.id} timeout="auto" unmountOnExit>
                <Box sx={{ pl: 7, pr: 2, py: 2 }}>
                  <Typography variant="body2" gutterBottom>
                    {suggestion.description}
                  </Typography>
                  
                  <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
                    <Box flex={1}>
                      <Typography variant="subtitle2" gutterBottom>
                        Code Original
                      </Typography>
                      <Paper
                        variant="outlined"
                        sx={{
                          p: 1,
                          bgcolor: 'grey.900',
                          maxHeight: 200,
                          overflow: 'auto'
                        }}
                      >
                        <pre style={{ margin: 0 }}>
                          <code>{suggestion.originalCode}</code>
                        </pre>
                      </Paper>
                    </Box>
                    
                    <Box flex={1}>
                      <Typography variant="subtitle2" gutterBottom>
                        Code Suggéré
                      </Typography>
                      <Paper
                        variant="outlined"
                        sx={{
                          p: 1,
                          bgcolor: 'grey.900',
                          maxHeight: 200,
                          overflow: 'auto'
                        }}
                      >
                        <pre style={{ margin: 0 }}>
                          <code>{suggestion.suggestedCode}</code>
                        </pre>
                      </Paper>
                    </Box>
                  </Box>

                  <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                    <Button
                      variant="contained"
                      size="small"
                      onClick={() => onApplySuggestion(suggestion.id)}
                      startIcon={<ApplyIcon />}
                    >
                      Appliquer
                    </Button>
                  </Box>
                </Box>
              </Collapse>
            </ListItem>
          </React.Fragment>
        ))}
      </List>
    </Paper>
  );
}; 