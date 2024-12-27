# Documentation de l'API AuditronAI

## Base URL
```
http://localhost:8000/api
```

## Authentification

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "string",
  "password": "string"
}

Response 200:
{
  "token": "string",
  "user": {
    "id": "string",
    "email": "string",
    "firstName": "string",
    "lastName": "string"
  }
}
```

### Register
```http
POST /auth/register
Content-Type: application/json

{
  "email": "string",
  "password": "string",
  "firstName": "string",
  "lastName": "string"
}

Response 201:
{
  "token": "string",
  "user": {
    "id": "string",
    "email": "string",
    "firstName": "string",
    "lastName": "string"
  }
}
```

## Audits

### Démarrer un audit
```http
POST /audits/start
Content-Type: application/json
Authorization: Bearer <token>

{
  "projectName": "string",
  "scope": ["string"],
  "rules": ["string"],
  "priority": "low" | "medium" | "high",
  "customRules": {
    "key": "value"
  }
}

Response 200:
{
  "auditId": "string"
}
```

### Obtenir le statut d'un audit
```http
GET /audits/{auditId}/status
Authorization: Bearer <token>

Response 200:
{
  "id": "string",
  "status": "pending" | "running" | "completed" | "failed",
  "progress": number,
  "findings": [
    {
      "id": "string",
      "severity": "low" | "medium" | "high" | "critical",
      "category": "string",
      "description": "string",
      "location": "string",
      "recommendation": "string",
      "risk": "string"
    }
  ],
  "summary": {
    "totalIssues": number,
    "criticalIssues": number,
    "highIssues": number,
    "mediumIssues": number,
    "lowIssues": number,
    "score": number
  },
  "startedAt": "string",
  "completedAt": "string",
  "error": "string"
}
```

## Notifications

### Obtenir les notifications
```http
GET /notifications
Authorization: Bearer <token>
Query Parameters:
  - unreadOnly: boolean
  - limit: number
  - offset: number

Response 200:
{
  "notifications": [
    {
      "id": "string",
      "type": "info" | "warning" | "error" | "success",
      "title": "string",
      "message": "string",
      "read": boolean,
      "createdAt": "string",
      "link": "string",
      "metadata": {
        "key": "value"
      }
    }
  ],
  "total": number
}
```

### Marquer comme lu
```http
PATCH /notifications/{notificationId}/read
Authorization: Bearer <token>

Response 200:
{}
```

## WebSocket

### Connexion
```websocket
ws://localhost:8000/ws/notifications?token=<token>
```

### Format des messages
```json
{
  "type": "info" | "warning" | "error" | "success",
  "title": "string",
  "message": "string",
  "timestamp": "string",
  "data": {
    "key": "value"
  }
}
```

## Codes d'erreur

| Code | Description |
|------|-------------|
| 400  | Requête invalide |
| 401  | Non authentifié |
| 403  | Non autorisé |
| 404  | Ressource non trouvée |
| 422  | Données invalides |
| 429  | Trop de requêtes |
| 500  | Erreur serveur |

## Limites de l'API

- Rate limit: 100 requêtes par minute par IP
- Taille maximale des requêtes: 10MB
- Timeout des requêtes: 30 secondes
- Durée de validité du token: 7 jours
- Nombre maximum de connexions WebSocket simultanées: 10 par utilisateur 