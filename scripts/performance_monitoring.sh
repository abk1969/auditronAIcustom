#!/bin/bash

# Variables
METRICS_DIR="/var/log/metrics"
PROMETHEUS_URL="http://localhost:9090"
GRAFANA_API="http://localhost:3000/api"
ALERT_WEBHOOK="https://hooks.slack.com/services/xxx/yyy/zzz"

# Vérifier les performances de l'API
check_api_performance() {
    # Temps de réponse moyen
    response_time=$(curl -w "%{time_total}\n" -o /dev/null -s "http://localhost:8000/health")
    if (( $(echo "$response_time > 1.0" | bc -l) )); then
        message="ALERTE: Temps de réponse API élevé (${response_time}s)"
        curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"$message\"}" $ALERT_WEBHOOK
    fi

    # Taux d'erreur
    error_rate=$(grep "ERROR" $METRICS_DIR/api.log | wc -l)
    if [ $error_rate -gt 100 ]; then
        message="ALERTE: Taux d'erreur API élevé ($error_rate erreurs)"
        curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"$message\"}" $ALERT_WEBHOOK
    fi
}

# Vérifier les performances de la base de données
check_db_performance() {
    # Connexions actives
    active_connections=$(psql -h localhost -U postgres -c "SELECT count(*) FROM pg_stat_activity" -t)
    if [ $active_connections -gt 100 ]; then
        message="ALERTE: Nombre élevé de connexions DB ($active_connections)"
        curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"$message\"}" $ALERT_WEBHOOK
    fi

    # Temps de requête long
    slow_queries=$(psql -h localhost -U postgres -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active' AND now() - query_start > '30 seconds'::interval" -t)
    if [ $slow_queries -gt 5 ]; then
        message="ALERTE: Requêtes lentes détectées ($slow_queries requêtes)"
        curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"$message\"}" $ALERT_WEBHOOK
    fi
}

# Vérifier l'utilisation du cache Redis
check_redis_performance() {
    # Taux de hits du cache
    redis-cli INFO | grep "keyspace_hits\|keyspace_misses" > /tmp/redis_stats
    hits=$(grep "keyspace_hits" /tmp/redis_stats | cut -d: -f2)
    misses=$(grep "keyspace_misses" /tmp/redis_stats | cut -d: -f2)
    hit_rate=$(echo "scale=2; $hits/($hits+$misses)*100" | bc)
    
    if (( $(echo "$hit_rate < 80" | bc -l) )); then
        message="ALERTE: Faible taux de hits du cache Redis ($hit_rate%)"
        curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"$message\"}" $ALERT_WEBHOOK
    fi
}

# Boucle principale
while true; do
    check_api_performance
    check_db_performance
    check_redis_performance
    sleep 60
done 