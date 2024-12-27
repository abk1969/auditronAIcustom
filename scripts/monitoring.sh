#!/bin/bash

# Variables
PROMETHEUS_URL="http://localhost:9090"
ALERT_WEBHOOK="https://hooks.slack.com/services/xxx/yyy/zzz"

# Vérifier l'état des services
check_service() {
    local service=$1
    local status=$(curl -s -o /dev/null -w "%{http_code}" $service)
    
    if [ $status -ne 200 ]; then
        message="ALERTE: Le service $service est DOWN (status: $status)"
        curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"$message\"}" $ALERT_WEBHOOK
    fi
}

# Vérifier l'utilisation des ressources
check_resources() {
    # CPU
    cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d. -f1)
    if [ $cpu_usage -gt 80 ]; then
        message="ALERTE: Utilisation CPU élevée ($cpu_usage%)"
        curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"$message\"}" $ALERT_WEBHOOK
    fi
    
    # Mémoire
    memory_usage=$(free | grep Mem | awk '{print $3/$2 * 100.0}' | cut -d. -f1)
    if [ $memory_usage -gt 80 ]; then
        message="ALERTE: Utilisation mémoire élevée ($memory_usage%)"
        curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"$message\"}" $ALERT_WEBHOOK
    fi
}

# Boucle principale
while true; do
    check_service "http://localhost:8000/health"
    check_service "http://localhost:3000"
    check_resources
    sleep 60
done 