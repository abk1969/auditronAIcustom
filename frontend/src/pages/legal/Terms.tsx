import React from 'react';
import { Container, Typography, Paper, Box } from '@mui/material';

const Terms: React.FC = () => {
  return (
    <Paper sx={{ p: 4 }}>
      <Typography variant="h4" gutterBottom>
        Conditions d'utilisation
      </Typography>
      
      <Box sx={{ mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          1. Acceptation des conditions
        </Typography>
        <Typography paragraph>
          En accédant et en utilisant AuditronAI, vous acceptez d'être lié par ces conditions d'utilisation.
          Ces conditions régissent votre utilisation de notre service d'analyse de code.
        </Typography>

        <Typography variant="h6" gutterBottom>
          2. Description du service
        </Typography>
        <Typography paragraph>
          AuditronAI est un service d'analyse de code qui fournit des outils d'audit et d'analyse automatisée
          pour améliorer la qualité et la sécurité du code source.
        </Typography>

        <Typography variant="h6" gutterBottom>
          3. Propriété intellectuelle
        </Typography>
        <Typography paragraph>
          Tout le contenu présent sur AuditronAI, y compris mais sans s'y limiter, le texte, les graphiques,
          les logos, est la propriété de Globacom3000 et est protégé par les lois sur la propriété intellectuelle.
        </Typography>

        <Typography variant="h6" gutterBottom>
          4. Limitation de responsabilité
        </Typography>
        <Typography paragraph>
          AuditronAI est fourni "tel quel" sans garantie d'aucune sorte. Nous ne garantissons pas que le service
          sera ininterrompu ou sans erreur.
        </Typography>
      </Box>
    </Paper>
  );
};

export default Terms;
