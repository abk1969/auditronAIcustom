# API Documentation

## Types et Structures de Données

### Utilisateur

```typescript
interface User {
  id: string;
  email: string;
  username: string;
  role: UserRole; // 'ADMIN' | 'USER' | 'ANALYST'
  is_active: boolean;
  is_verified: boolean;
  preferences: Record<string, any>;
  profile: Record<string, any>;
  created_at: string;
  updated_at: string;
}
```

### Analyse

```typescript
interface Analysis {
  id: string;
  user_id: string;
  repository_url?: string;
  code_snippet?: string;
  language: string;
  status: AnalysisStatus; // 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED'
  metrics: {
    [key: string]: any;
  };
  issues: Array<{
    type: string;
    severity: string;
    message: string;
    line?: number;
    column?: number;
    file?: string;
    code?: string;
    suggestion?: string;
  }>;
  suggestions: Array<{
    type: string;
    message: string;
    code?: string;
    impact?: string;
    effort?: string;
  }>;
  lines_of_code: number;
  complexity_score: number;
  security_score: number;
  performance_score: number;
  created_at: string;
  updated_at: string;
}
```

## Endpoints API

### Authentification

#### POST /auth/login
- **Request Body**: `{ email: string, password: string }`
- **Response**: `{ token: string, user: User }`

### Analyses

#### GET /analysis
- **Response**: `{ analyses: Analysis[] }`

#### POST /analysis
- **Request Body**:
```typescript
{
  repository_url?: string;
  code_snippet?: string;
  language: string;
}
```
- **Response**: `{ analysis: Analysis }`

#### GET /analysis/{id}
- **Response**: `{ analysis: Analysis }`

### Monitoring

#### GET /monitoring/metrics
- **Response**:
```typescript
{
  cpu: {
    usage: number;
    cores: number;
  };
  memory: {
    total: number;
    used: number;
    free: number;
  };
  requests: {
    total: number;
    successful: number;
    failed: number;
    averageResponseTime: number;
  };
  timestamp: string;
}
```

### Settings

#### GET /settings
- **Response**:
```typescript
{
  aiModel: string;
  theme: string;
  notifications: {
    enabled: boolean;
    email: boolean;
    desktop: boolean;
  };
  language: string;
  codeAnalysis: {
    maxFileSize: number;
    excludedPatterns: string[];
  };
}
```

## Base de données

### Tables

#### users
- id: UUID (PK)
- email: string (unique)
- username: string (unique)
- password_hash: string
- role: enum (ADMIN, USER, ANALYST)
- is_active: boolean
- is_verified: boolean
- preferences: jsonb
- profile: jsonb
- created_at: timestamp
- updated_at: timestamp
- created_by: string
- updated_by: string

#### analyses
- id: UUID (PK)
- user_id: UUID (FK -> users.id)
- repository_url: string (nullable)
- code_snippet: text (nullable)
- language: string
- status: enum (PENDING, PROCESSING, COMPLETED, FAILED)
- metrics: jsonb
- issues: jsonb[]
- suggestions: jsonb[]
- lines_of_code: integer
- complexity_score: float
- security_score: float
- performance_score: float
- created_at: timestamp
- updated_at: timestamp
- created_by: string
- updated_by: string
