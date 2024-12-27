"""Composant d'édition de code avec analyse en temps réel."""
import React from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Tooltip,
  CircularProgress,
  Chip,
  Stack,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import {
  PlayArrow as RunIcon,
  Save as SaveIcon,
  Upload as UploadIcon,
  Download as DownloadIcon,
  Settings as SettingsIcon,
  Refresh as ResetIcon
} from '@mui/icons-material';
import Editor from '@monaco-editor/react';

interface CodeEditorProps {
  code: string;
  language: string;
  onChange: (value: string) => void;
  onAnalyze: () => void;
  onSave?: () => void;
  isAnalyzing?: boolean;
  diagnostics?: Array<{
    line: number;
    column: number;
    severity: 'error' | 'warning' | 'info';
    message: string;
  }>;
}

const SUPPORTED_LANGUAGES = [
  { id: 'typescript', label: 'TypeScript' },
  { id: 'javascript', label: 'JavaScript' },
  { id: 'python', label: 'Python' },
  { id: 'java', label: 'Java' },
  { id: 'go', label: 'Go' },
  { id: 'rust', label: 'Rust' }
];

const EDITOR_THEMES = [
  { id: 'vs-dark', label: 'Sombre' },
  { id: 'light', label: 'Clair' },
  { id: 'hc-black', label: 'Contraste Élevé' }
];

export const CodeEditor: React.FC<CodeEditorProps> = ({
  code,
  language,
  onChange,
  onAnalyze,
  onSave,
  isAnalyzing,
  diagnostics
}) => {
  const [theme, setTheme] = React.useState('vs-dark');
  const [fontSize, setFontSize] = React.useState(14);
  const [showSettings, setShowSettings] = React.useState(false);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        onChange(content);
      };
      reader.readAsText(file);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `code.${language}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const editorOptions = {
    fontSize,
    minimap: { enabled: true },
    lineNumbers: 'on',
    roundedSelection: false,
    scrollBeyondLastLine: false,
    automaticLayout: true
  };

  return (
    <Box>
      <Paper sx={{ mb: 2, p: 2 }}>
        <Stack direction="row" spacing={2} alignItems="center">
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Langage</InputLabel>
            <Select
              value={language}
              label="Langage"
              onChange={(e) => onChange(e.target.value)}
            >
              {SUPPORTED_LANGUAGES.map(lang => (
                <MenuItem key={lang.id} value={lang.id}>
                  {lang.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Box sx={{ flexGrow: 1 }} />

          <input
            type="file"
            id="file-upload"
            style={{ display: 'none' }}
            onChange={handleFileUpload}
            accept=".ts,.js,.py,.java,.go,.rs"
          />
          
          <Tooltip title="Charger un fichier">
            <IconButton
              onClick={() => document.getElementById('file-upload')?.click()}
            >
              <UploadIcon />
            </IconButton>
          </Tooltip>

          <Tooltip title="Télécharger">
            <IconButton onClick={handleDownload}>
              <DownloadIcon />
            </IconButton>
          </Tooltip>

          <Tooltip title="Sauvegarder">
            <IconButton onClick={onSave} disabled={!onSave}>
              <SaveIcon />
            </IconButton>
          </Tooltip>

          <Tooltip title="Paramètres">
            <IconButton onClick={() => setShowSettings(!showSettings)}>
              <SettingsIcon />
            </IconButton>
          </Tooltip>

          <Tooltip title="Analyser">
            <IconButton
              onClick={onAnalyze}
              color="primary"
              disabled={isAnalyzing}
            >
              {isAnalyzing ? <CircularProgress size={24} /> : <RunIcon />}
            </IconButton>
          </Tooltip>
        </Stack>

        {showSettings && (
          <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
            <Stack direction="row" spacing={2}>
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Thème</InputLabel>
                <Select
                  value={theme}
                  label="Thème"
                  onChange={(e) => setTheme(e.target.value)}
                >
                  {EDITOR_THEMES.map(theme => (
                    <MenuItem key={theme.id} value={theme.id}>
                      {theme.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Taille Police</InputLabel>
                <Select
                  value={fontSize}
                  label="Taille Police"
                  onChange={(e) => setFontSize(Number(e.target.value))}
                >
                  {[12, 14, 16, 18, 20].map(size => (
                    <MenuItem key={size} value={size}>
                      {size}px
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Stack>
          </Box>
        )}
      </Paper>

      <Paper sx={{ height: 600 }}>
        <Editor
          height="100%"
          language={language}
          value={code}
          theme={theme}
          onChange={(value) => onChange(value || '')}
          options={editorOptions}
          onMount={(editor) => {
            // Configuration des marqueurs pour les diagnostics
            if (diagnostics) {
              const markers = diagnostics.map(d => ({
                startLineNumber: d.line,
                startColumn: d.column,
                endLineNumber: d.line,
                endColumn: d.column + 1,
                message: d.message,
                severity: d.severity === 'error' ? 8 : d.severity === 'warning' ? 4 : 1
              }));
              editor.setModel(editor.getModel());
              editor.deltaDecorations([], markers);
            }
          }}
        />
      </Paper>
    </Box>
  );
}; 