#!/bin/bash

# Variables
LOG_DIR="/var/log/auditronai"
ALERT_WEBHOOK="https://hooks.slack.com/services/xxx/yyy/zzz"
FAIL2BAN_LOG="/var/log/fail2ban.log"

# Vérifier les tentatives d'intrusion
check_intrusion_attempts() {
    # Vérifier les logs SSH
    ssh_attempts=$(grep "Failed password" /var/log/auth.log | wc -l)
    if [ $ssh_attempts -gt 100 ]; then
        message="ALERTE: Nombreuses tentatives de connexion SSH échouées ($ssh_attempts)"
        curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"$message\"}" $ALERT_WEBHOOK
    fi

    # Vérifier les logs d'application
    api_attempts=$(grep "401 Unauthorized" $LOG_DIR/api.log | wc -l)
    if [ $api_attempts -gt 1000 ]; then
        message="ALERTE: Nombreuses tentatives d'accès API non autorisées ($api_attempts)"
        curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"$message\"}" $ALERT_WEBHOOK
    fi
}

# Vérifier les fichiers critiques
check_file_integrity() {
    if [ ! -f "/var/lib/aide/aide.db" ]; then
        aide --init
        mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db
    fi

    aide --check | grep -i "changed" > /tmp/aide_changes
    if [ -s /tmp/aide_changes ]; then
        message="ALERTE: Modifications détectées dans les fichiers système"
        curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"$message\"}" $ALERT_WEBHOOK
    fi
}

# Vérifier les processus suspects
check_suspicious_processes() {
    # Processus avec utilisation CPU anormale
    cpu_hogs=$(ps aux | awk '$3 > 80.0' | grep -v "root")
    if [ ! -z "$cpu_hogs" ]; then
        message="ALERTE: Processus suspect avec haute utilisation CPU détecté"
        curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"$message\"}" $ALERT_WEBHOOK
    fi

    # Processus réseau suspects
    netstat -tuln | grep "LISTEN" | grep -v "127.0.0.1" > /tmp/network_listeners
    diff /tmp/network_listeners /etc/baseline/network_listeners
    if [ $? -ne 0 ]; then
        message="ALERTE: Nouveaux ports en écoute détectés"
        curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"$message\"}" $ALERT_WEBHOOK
    fi
}

# Boucle principale
while true; do
    check_intrusion_attempts
    check_file_integrity
    check_suspicious_processes
    sleep 300
done 