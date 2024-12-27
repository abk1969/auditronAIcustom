#!/bin/bash
set -e

# Variables
CLUSTER_NAME="auditronai-local"
KUBECTL="kubectl"

# Créer le cluster kind
create_cluster() {
    echo "Creating Kind cluster..."
    kind create cluster --name $CLUSTER_NAME --config k8s/local/kind-config.yaml

    echo "Waiting for cluster to be ready..."
    $KUBECTL wait --for=condition=Ready nodes --all --timeout=300s
}

# Installer les dépendances
install_dependencies() {
    echo "Installing Ingress NGINX..."
    $KUBECTL apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/static/provider/kind/deploy.yaml

    echo "Installing Metrics Server..."
    $KUBECTL apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

    echo "Waiting for deployments to be ready..."
    $KUBECTL -n ingress-nginx wait --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=300s
}

# Déployer l'application
deploy_application() {
    echo "Deploying application..."
    $KUBECTL apply -k k8s/overlays/local

    echo "Waiting for deployments to be ready..."
    $KUBECTL -n auditronai wait --for=condition=available deployment --all --timeout=300s
}

# Fonction principale
main() {
    create_cluster
    install_dependencies
    deploy_application

    echo "Application deployed successfully!"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
}

main 