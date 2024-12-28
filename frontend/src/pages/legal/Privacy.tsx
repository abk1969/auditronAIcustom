import React from 'react';
import { Typography, Paper, Box } from '@mui/material';

const Privacy: React.FC = () => {
  return (
    <Paper sx={{ p: 4 }}>
      <Typography variant="h4" gutterBottom>
        Politique de confidentialité et RGPD
      </Typography>
      
      <Box sx={{ mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          1. Collecte des données
        </Typography>
        <Typography paragraph>
          Dans le cadre de notre service d'analyse de code, nous collectons uniquement les données
          nécessaires au bon fonctionnement du service. Cela inclut :
          - Le code source soumis pour analyse
          - Les informations de compte utilisateur
          - Les logs d'utilisation du service
        </Typography>

        <Typography variant="h6" gutterBottom>
          2. Conformité RGPD
        </Typography>
        <Typography paragraph>
          Conformément au Règlement Général sur la Protection des Données (RGPD), nous nous engageons à :
          - Traiter vos données de manière licite, loyale et transparente
          - Collecter vos données pour des finalités déterminées et légitimes
          - Minimiser la collecte des données
          - Garantir l'exactitude des données
          - Limiter la conservation des données
          - Assurer la sécurité des données
        </Typography>

        <Typography variant="h6" gutterBottom>
          3. Vos droits
        </Typography>
        <Typography paragraph>
          En tant qu'utilisateur, vous disposez des droits suivants :
          - Droit d'accès à vos données
          - Droit de rectification
          - Droit à l'effacement
          - Droit à la limitation du traitement
          - Droit à la portabilité
          - Droit d'opposition
        </Typography>

        <Typography variant="h6" gutterBottom>
          4. Sécurité des données
        </Typography>
        <Typography paragraph>
          Nous mettons en œuvre des mesures techniques et organisationnelles appropriées pour garantir
          un niveau de sécurité adapté au risque, notamment :
          - Le chiffrement des données
          - La pseudonymisation des données
          - Des procédures de test et d'évaluation régulières
        </Typography>

        <Typography variant="h6" gutterBottom>
          5. Contact
        </Typography>
        <Typography paragraph>
          Pour toute question concernant le traitement de vos données ou pour exercer vos droits,
          vous pouvez nous contacter à : privacy@auditronai.com
        </Typography>
      </Box>
    </Paper>
  );
};

export default Privacy;
