import React from 'react';
import { Typography, Paper, Box, List, ListItem, ListItemText } from '@mui/material';

const Cookies: React.FC = () => {
  return (
    <Paper sx={{ p: 4 }}>
      <Typography variant="h4" gutterBottom>
        Gestion des Cookies
      </Typography>
      
      <Box sx={{ mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          1. Qu'est-ce qu'un cookie ?
        </Typography>
        <Typography paragraph>
          Un cookie est un petit fichier texte stocké sur votre ordinateur lors de la visite d'un site web.
          Les cookies nous aident à améliorer votre expérience utilisateur et à comprendre comment notre
          service est utilisé.
        </Typography>

        <Typography variant="h6" gutterBottom>
          2. Types de cookies utilisés
        </Typography>
        <List>
          <ListItem>
            <ListItemText
              primary="Cookies essentiels"
              secondary="Nécessaires au fonctionnement du site et à la sécurité de votre session"
            />
          </ListItem>
          <ListItem>
            <ListItemText
              primary="Cookies de performance"
              secondary="Nous aident à comprendre comment les visiteurs interagissent avec le site"
            />
          </ListItem>
          <ListItem>
            <ListItemText
              primary="Cookies de fonctionnalité"
              secondary="Permettent de mémoriser vos préférences et paramètres"
            />
          </ListItem>
        </List>

        <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
          3. Durée de conservation
        </Typography>
        <Typography paragraph>
          Les cookies peuvent être temporaires (cookies de session) ou permanents.
          Les cookies de session sont supprimés à la fermeture du navigateur, tandis
          que les cookies permanents restent sur votre appareil pendant une durée définie.
        </Typography>

        <Typography variant="h6" gutterBottom>
          4. Comment gérer vos cookies
        </Typography>
        <Typography paragraph>
          Vous pouvez à tout moment modifier vos préférences en matière de cookies :
          - Via les paramètres de votre navigateur
          - En utilisant notre panneau de gestion des cookies
          - En nous contactant directement
        </Typography>

        <Typography variant="h6" gutterBottom>
          5. Impact du refus des cookies
        </Typography>
        <Typography paragraph>
          Le refus des cookies essentiels peut empêcher l'utilisation de certaines
          fonctionnalités du site. Les autres types de cookies peuvent être refusés
          sans impact majeur sur votre expérience utilisateur.
        </Typography>
      </Box>
    </Paper>
  );
};

export default Cookies;
