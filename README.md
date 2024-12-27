# AuditronAI

AuditronAI est un outil d'analyse de sécurité et d'audit de code Python, développé avec l'assistance d'IA pour offrir une analyse approfondie et automatisée.

## ✅ Fonctionnalités Actuelles

### Analyse de Sécurité
- Détection des vulnérabilités avec Bandit
- Analyse statique du code source
- Identification des problèmes de sécurité courants
- Configuration flexible des seuils de sévérité

### Analyse de Qualité
- Mesure de la complexité cyclomatique avec Radon
- Détection du code mort avec Vulture
- Vérification du style avec Flake8
- Analyse de qualité avec Prospector

### Interface Utilisateur
- Interface Streamlit intuitive
- Visualisation des résultats d'analyse
- Suivi de la progression des analyses
- Affichage des métriques de base

### Configuration
- Paramétrage des seuils de sévérité
- Configuration du niveau de scan
- Ajustement des timeouts
- Personnalisation des règles d'analyse

## 🚧 Limitations Actuelles

- Analyse limitée au code Python uniquement
- Pas d'intégration CI/CD pour le moment
- Pas d'analyse de dépendances
- Pas de support multi-langages
- Interface utilisateur basique
- Pas de stockage persistant des résultats
- Pas d'authentification utilisateur
- Pas d'API REST

## 🤖 Développement Assisté par IA

AuditronAI est développé avec l'assistance d'outils d'IA pour le code, notamment :
- Génération de code assistée par IA
- Revue de code automatisée
- Suggestions d'optimisation
- Documentation générée

## 🔜 Fonctionnalités Prévues

- Support pour d'autres langages de programmation
- Intégration CI/CD
- Analyse des dépendances
- Base de données pour l'historique des analyses
- API REST
- Interface utilisateur avancée
- Authentification et gestion des utilisateurs
- Rapports PDF exportables
- Intégration avec les outils de gestion de projet

## Installation

### Option 1: Installation Locale

1. Cloner le repository
```bash
git clone https://github.com/votre-username/AuditronAI.git
cd AuditronAI
```

2. Créer un environnement virtuel Python
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Installer les dépendances
```bash
pip install -r requirements.txt
```

4. Configuration
- Copier `.env.example` vers `.env`
- Configurer les variables d'environnement requises

5. Lancer l'application
```bash
streamlit run app/streamlit_app.py
```

### Option 2: Installation avec Docker

1. Cloner le repository
```bash
git clone https://github.com/votre-username/AuditronAI.git
cd AuditronAI
```

2. Configuration
- Copier `.env.example` vers `.env`
- Configurer les variables d'environnement requises

3. Construire et lancer avec Docker Compose
```bash
docker-compose up --build
```

L'application sera accessible à l'adresse `http://localhost:8501`

## Structure du Projet

```
AuditronAI/
├── app/                    # Interface Streamlit
├── core/                   # Logique d'analyse
├── templates/              # Templates
└── tests/                  # Tests
```

## Licence

Copyright (c) 2024. Tous droits réservés.

## Note Importante

Cette version d'AuditronAI est en développement actif. Les fonctionnalités listées comme "Prévues" sont en cours de développement et seront ajoutées progressivement. Les retours d'expérience sont les bienvenus pour améliorer l'outil.
