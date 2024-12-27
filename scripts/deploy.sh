#!/bin/bash
set -e

# Variables
ENV=$1
AWS_REGION="eu-west-1"
ECR_REPO="auditronai"
CLUSTER_NAME="auditron-cluster"

# Vérifier l'environnement
if [ "$ENV" != "staging" ] && [ "$ENV" != "production" ]; then
    echo "Usage: $0 [staging|production]"
    exit 1
fi

# Configuration AWS
aws configure set default.region $AWS_REGION

# Login ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO

# Build et push des images
VERSION=$(git rev-parse --short HEAD)
docker-compose -f docker-compose.yml -f docker-compose.$ENV.yml build
docker-compose -f docker-compose.yml -f docker-compose.$ENV.yml push

# Mise à jour ECS
aws ecs update-service --cluster $CLUSTER_NAME --service auditron-$ENV --force-new-deployment

# Attendre que le déploiement soit terminé
echo "Attente de la fin du déploiement..."
aws ecs wait services-stable --cluster $CLUSTER_NAME --services auditron-$ENV

echo "Déploiement terminé avec succès!" 