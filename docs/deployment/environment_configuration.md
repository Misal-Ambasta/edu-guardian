# Environment Configuration Management

## Overview

This document outlines the environment configuration management system for the Edu-Guardian platform. It provides detailed information on managing different environments, configuration variables, and secrets management.

## Environment Types

The Edu-Guardian system supports the following environment types:

1. **Development**: For local development work
2. **Testing**: For automated tests and QA
3. **Staging**: For pre-production validation
4. **Production**: For live deployment

## Configuration Files

### Environment Files

The system uses `.env` files for environment-specific configuration:

- `.env.example`: Template with all required variables (no actual values)
- `.env.development`: Development environment configuration
- `.env.testing`: Testing environment configuration
- `.env.staging`: Staging environment configuration
- `.env.production`: Production environment configuration

### Configuration Structure

Each environment file follows this structure:

```
# Database Configuration
DB_HOST=hostname
DB_PORT=5432
DB_NAME=database_name
DB_USER=username
DB_PASSWORD=password

# Vector Database Configuration
CHROMA_HOST=hostname
CHROMA_PORT=8000

# Redis Configuration
REDIS_HOST=hostname
REDIS_PORT=6379
REDIS_PASSWORD=password

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true_or_false
API_SECRET_KEY=secret_key
API_ALLOWED_ORIGINS=comma_separated_origins

# Authentication Configuration
JWT_SECRET_KEY=jwt_secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Service Configuration
GEMINI_API_KEY=api_key

# Email Configuration
EMAIL_HOST=smtp_host
EMAIL_PORT=587
EMAIL_USERNAME=username
EMAIL_PASSWORD=password
EMAIL_FROM=email_address

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=logs/app.log

# Feature Flags
FEATURE_ADVANCED_EMOTION=true_or_false
FEATURE_PREDICTIVE_ANALYTICS=true_or_false
```

## Loading Configuration

### Backend Configuration

The backend uses the `pydantic-settings` package to load and validate configuration:

```python
# backend/app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    # Database settings
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    
    # Vector database settings
    CHROMA_HOST: str
    CHROMA_PORT: int
    
    # Redis settings
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    
    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_DEBUG: bool = False
    API_SECRET_KEY: str
    API_ALLOWED_ORIGINS: List[str]
    
    # Authentication settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI service settings
    GEMINI_API_KEY: str
    
    # Email settings
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: str
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: str = "logs/app.log"
    
    # Feature flags
    FEATURE_ADVANCED_EMOTION: bool = True
    FEATURE_PREDICTIVE_ANALYTICS: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

# Create settings instance
settings = Settings()
```

### Frontend Configuration

The frontend uses environment-specific configuration files:

```javascript
// frontend/src/config/config.js
const configs = {
  development: {
    apiUrl: 'http://localhost:8000/api',
    wsUrl: 'ws://localhost:8000/ws',
    debug: true,
    featureFlags: {
      advancedEmotion: true,
      predictiveAnalytics: true
    }
  },
  testing: {
    apiUrl: 'http://localhost:8000/api',
    wsUrl: 'ws://localhost:8000/ws',
    debug: true,
    featureFlags: {
      advancedEmotion: true,
      predictiveAnalytics: true
    }
  },
  staging: {
    apiUrl: 'https://staging-api.edu-guardian.com/api',
    wsUrl: 'wss://staging-api.edu-guardian.com/ws',
    debug: false,
    featureFlags: {
      advancedEmotion: true,
      predictiveAnalytics: true
    }
  },
  production: {
    apiUrl: 'https://api.edu-guardian.com/api',
    wsUrl: 'wss://api.edu-guardian.com/ws',
    debug: false,
    featureFlags: {
      advancedEmotion: true,
      predictiveAnalytics: true
    }
  }
};

const env = process.env.REACT_APP_ENV || 'development';
const config = configs[env];

export default config;
```

## Environment Selection

### Backend Environment Selection

The backend selects the environment based on the `ENV` environment variable:

```python
# backend/app/core/config.py
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # ... settings fields ...
    
    model_config = SettingsConfigDict(
        env_file=f".env.{os.getenv('ENV', 'development')}",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
```

### Frontend Environment Selection

The frontend environment is selected during the build process:

```json
// frontend/package.json
{
  "scripts": {
    "start": "REACT_APP_ENV=development react-scripts start",
    "build:dev": "REACT_APP_ENV=development react-scripts build",
    "build:staging": "REACT_APP_ENV=staging react-scripts build",
    "build:prod": "REACT_APP_ENV=production react-scripts build",
    "test": "REACT_APP_ENV=testing react-scripts test"
  }
}
```

## Secrets Management

### Development Secrets

For development, secrets are stored in the `.env.development` file, which is not committed to the repository.

### Production Secrets

For production environments, secrets should be managed using one of the following methods:

#### Docker Secrets

When using Docker Swarm:

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    image: edu-guardian/backend:latest
    secrets:
      - db_password
      - jwt_secret
      - gemini_api_key
    environment:
      - DB_PASSWORD_FILE=/run/secrets/db_password
      - JWT_SECRET_KEY_FILE=/run/secrets/jwt_secret
      - GEMINI_API_KEY_FILE=/run/secrets/gemini_api_key

secrets:
  db_password:
    external: true
  jwt_secret:
    external: true
  gemini_api_key:
    external: true
```

#### Kubernetes Secrets

When using Kubernetes:

```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: edu-guardian-secrets
  namespace: edu-guardian
type: Opaque
data:
  db_password: base64_encoded_password
  jwt_secret: base64_encoded_secret
  gemini_api_key: base64_encoded_api_key
```

```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: edu-guardian
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: edu-guardian/backend:latest
        env:
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: edu-guardian-secrets
              key: db_password
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: edu-guardian-secrets
              key: jwt_secret
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: edu-guardian-secrets
              key: gemini_api_key
```

#### Vault Integration

For advanced secrets management, HashiCorp Vault can be integrated:

```python
# backend/app/core/vault.py
import hvac
import os

class VaultClient:
    def __init__(self):
        self.client = hvac.Client(
            url=os.getenv('VAULT_ADDR'),
            token=os.getenv('VAULT_TOKEN')
        )
    
    def get_secret(self, path, key):
        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                path=path
            )
            return response['data']['data'].get(key)
        except Exception as e:
            print(f"Error retrieving secret: {e}")
            return None

# Usage
vault = VaultClient()
db_password = vault.get_secret('edu-guardian/database', 'password')
```

## Configuration Validation

### Backend Validation

The backend validates configuration at startup:

```python
# backend/app/core/config.py
from pydantic import validator

class Settings(BaseSettings):
    # ... settings fields ...
    
    @validator('API_ALLOWED_ORIGINS', pre=True)
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('DB_PORT', 'CHROMA_PORT', 'REDIS_PORT', 'EMAIL_PORT')
    def validate_ports(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError(f'Port must be between 1 and 65535, got {v}')
        return v
```

### Configuration Testing

Configuration tests ensure that all environments have the required variables:

```python
# backend/tests/test_config.py
import os
import pytest
from app.core.config import Settings

@pytest.mark.parametrize('env', ['development', 'testing', 'staging', 'production'])
def test_environment_config(env):
    os.environ['ENV'] = env
    settings = Settings()
    
    # Test required settings are present
    assert settings.DB_HOST
    assert settings.DB_PORT
    assert settings.DB_NAME
    assert settings.DB_USER
    assert settings.DB_PASSWORD
    
    # Test environment-specific settings
    if env == 'development' or env == 'testing':
        assert settings.API_DEBUG is True
    else:
        assert settings.API_DEBUG is False
```

## Feature Flags

Feature flags allow for enabling or disabling features in different environments:

```python
# backend/app/core/feature_flags.py
from app.core.config import settings

def is_feature_enabled(feature_name):
    feature_flag_name = f"FEATURE_{feature_name.upper()}"
    return getattr(settings, feature_flag_name, False)

# Usage
if is_feature_enabled('advanced_emotion'):
    # Use advanced emotion analysis
else:
    # Use basic emotion analysis
```

## Environment-Specific Behavior

### Environment-Specific Logging

```python
# backend/app/core/logging.py
import logging
import json
import os
from app.core.config import settings

def setup_logging():
    log_level = getattr(logging, settings.LOG_LEVEL)
    log_format = settings.LOG_FORMAT
    log_file = settings.LOG_FILE
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure logging
    if log_format == 'json':
        formatter = logging.Formatter(lambda record: json.dumps({
            'timestamp': record.created,
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }))
    else:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Set debug level for specific loggers in development
    if settings.API_DEBUG:
        logging.getLogger('app').setLevel(logging.DEBUG)
```

### Environment-Specific Database Configuration

```python
# backend/app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Construct database URL
DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

# Create engine with environment-specific settings
engine_args = {
    'pool_pre_ping': True,
}

# Add environment-specific engine arguments
if settings.API_DEBUG:
    engine_args.update({
        'echo': True,  # Log SQL queries
        'pool_size': 5,
        'max_overflow': 10
    })
else:
    engine_args.update({
        'pool_size': 20,
        'max_overflow': 30
    })

engine = create_engine(DATABASE_URL, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

## CI/CD Environment Configuration

### GitHub Actions Environment Variables

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    env:
      ENV: testing
      DB_HOST: localhost
      DB_PORT: 5432
      DB_NAME: test_db
      DB_USER: postgres
      DB_PASSWORD: postgres
      # ... other environment variables ...
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        cd backend
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run tests
      run: |
        cd backend
        pytest
```

## Conclusion

This document provides a comprehensive guide to environment configuration management in the Edu-Guardian system. By following these practices, you can ensure consistent configuration across different environments and secure management of sensitive information.