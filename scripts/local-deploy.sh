#!/bin/bash
set -e

# Couleurs pour les logs
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Fonction de logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Vérifier les prérequis
check_prerequisites() {
    log "Vérification des prérequis..."
    
    command -v docker >/dev/null 2>&1 || error "Docker n'est pas installé"
    command -v docker-compose >/dev/null 2>&1 || error "Docker Compose n'est pas installé"
    command -v python3 >/dev/null 2>&1 || error "Python 3 n'est pas installé"
    command -v node >/dev/null 2>&1 || error "Node.js n'est pas installé"
}

# Configurer l'environnement
setup_environment() {
    log "Configuration de l'environnement..."
    
    # Créer les fichiers .env si nécessaire
    if [ ! -f "./backend/.env" ]; then
        cat > ./backend/.env << EOF
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/auditronai
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=local_development_secret
ENVIRONMENT=development
EOF
    fi

    if [ ! -f "./frontend/.env" ]; then
        cat > ./frontend/.env << EOF
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
EOF
    fi
}

# Installer les dépendances
install_dependencies() {
    log "Installation des dépendances..."
    
    # Backend
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..

    # Frontend
    cd frontend
    npm install
    cd ..
}

# Démarrer les services
start_services() {
    log "Démarrage des services..."
    
    # Services Docker (PostgreSQL, Redis)
    docker-compose -f docker-compose.local.yml up -d

    # Attendre que la base de données soit prête
    log "Attente de la base de données..."
    sleep 5

    # Migrations
    cd backend
    source venv/bin/activate
    alembic upgrade head
    cd ..

    # Démarrer le backend
    cd backend
    source venv/bin/activate
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    cd ..

    # Démarrer le frontend
    cd frontend
    npm start &
    cd ..
}

# Vérifier la santé des services
check_health() {
    log "Vérification de la santé des services..."
    
    # Vérifier le backend
    curl -f http://localhost:8000/health || error "Le backend ne répond pas"
    
    # Vérifier le frontend
    curl -f http://localhost:3000 || error "Le frontend ne répond pas"
    
    log "Tous les services sont opérationnels!"
}

# Exécuter les seeds
seed_database() {
    log "Seeding de la base de données..."
    cd backend
    source venv/bin/activate
    python -m app.db.seeds.seed_data
    cd ..
}

# Exécuter les tests de smoke
run_smoke_tests() {
    log "Exécution des tests de smoke..."
    python scripts/smoke_tests.py
}

# Exécuter les tests de performance
run_performance_tests() {
    log "Exécution des tests de performance..."
    python scripts/performance_tests.py
}

# Configurer le mode développement
setup_dev_mode() {
    log "Configuration du mode développement..."
    
    # Activer le hot-reload
    export WATCHFILES_FORCE_POLLING=true
    export CHOKIDAR_USEPOLLING=true
    
    # Configurer le debugging
    export PYTHONPATH=./backend
    export DEBUG=1
    export DEBUG_PORT=5678
    
    # Démarrer avec docker-compose.dev.yml
    docker-compose -f docker-compose.dev.yml up -d
    
    # Ajouter le profilage en mode dev
    setup_profiling
    
    # Configurer le profil de développement
    export ENVIRONMENT=development
    export CONFIG_PROFILE=development
}

# Ajouter une nouvelle fonction pour le profilage
setup_profiling() {
    log "Configuration du profilage..."
    
    # Créer les répertoires nécessaires
    mkdir -p profiling memory_snapshots logs
    
    # Configurer les variables d'environnement
    export PROFILING_ENABLED=1
    export MEMORY_TRACKING_ENABLED=1
}

# Fonction principale
main() {
    local mode="$1"
    
    case "$mode" in
        "dev")
            log "Démarrage en mode développement..."
            check_prerequisites
            setup_environment
            setup_dev_mode
            ;;
        "perf")
            log "Démarrage avec tests de performance..."
            check_prerequisites
            setup_environment
            install_dependencies
            start_services
            check_health
            seed_database
            run_performance_tests
            ;;
        "profile")
            log "Démarrage en mode profilage..."
            check_prerequisites
            setup_environment
            setup_profiling
            start_services
            check_health
            ;;
        *)
            # Mode normal (existant)
            log "Démarrage en mode normal..."
            check_prerequisites
            setup_environment
            install_dependencies
            start_services
            check_health
            seed_database
            run_smoke_tests
            ;;
    esac
    
    log "Déploiement local terminé avec succès!"
    log "Frontend: http://localhost:3000"
    log "Backend: http://localhost:8000"
    log "Documentation API: http://localhost:8000/docs"
}

# Gestion du nettoyage
cleanup() {
    log "Nettoyage..."
    docker-compose -f docker-compose.local.yml down
    pkill -f "uvicorn"
    pkill -f "npm start"
}

# Gestion des erreurs et interruptions
trap cleanup EXIT
trap 'error "Une erreur est survenue"' ERR

# Exécution
main "$1" 