# AuditronAI

AuditronAI est une application d'analyse de sécurité et d'audit automatisé pour les projets logiciels.

## Fonctionnalités

- Analyse de sécurité automatisée du code source
- Génération de rapports détaillés
- Interface utilisateur Streamlit
- Support pour OpenAI, Azure et Gemini
- Visualisations et métriques avancées
- Gestion des configurations de sécurité
- Historique des analyses

## Installation

1. Cloner le repository
```bash
git clone https://github.com/abk1969/AuditronAI.git
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
- Configurer les variables d'environnement requises dans `.env`

5. Lancer l'application
```bash
streamlit run app/streamlit_app.py
```

## Structure du Projet

```
AuditronAI/
├── app/                    # Interface utilisateur Streamlit
├── core/                   # Logique métier principale
├── templates/              # Templates de prompts
└── tests/                  # Tests unitaires et d'intégration
```

## Tests

```bash
pytest tests/
```

## Docker

```bash
docker-compose up --build
```

## Licence

Copyright (c) 2024 abk1969. Tous droits réservés.

Ce logiciel est fourni sous une licence restrictive. Toute utilisation commerciale est strictement interdite sans l'accord explicite écrit du propriétaire (abk1969).

Voir le fichier [LICENSE.md](LICENSE.md) pour plus de détails.
