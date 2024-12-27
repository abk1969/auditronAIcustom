#!/bin/bash
set -e

# Variables
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgres"
S3_BUCKET="auditronai-backups"

# Créer le répertoire de backup si nécessaire
mkdir -p $BACKUP_DIR

# Backup de la base de données
echo "Démarrage du backup..."
pg_dump -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -F c -f $BACKUP_DIR/backup_$TIMESTAMP.dump

# Compression
echo "Compression du backup..."
gzip $BACKUP_DIR/backup_$TIMESTAMP.dump

# Upload vers S3
echo "Upload vers S3..."
aws s3 cp $BACKUP_DIR/backup_$TIMESTAMP.dump.gz s3://$S3_BUCKET/postgres/backup_$TIMESTAMP.dump.gz

# Nettoyage des anciens backups (garder 7 jours)
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup terminé avec succès!" 