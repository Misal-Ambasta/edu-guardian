# Edu-Guardian Deployment Documentation

## Overview

This document provides comprehensive instructions for deploying the Edu-Guardian system in various environments. It covers environment setup, configuration management, deployment procedures, and CI/CD pipeline configuration.

## Prerequisites

### Hardware Requirements

- **Production Environment**:
  - CPU: 8+ cores
  - RAM: 16+ GB
  - Storage: 100+ GB SSD
  - Network: 1 Gbps

- **Development Environment**:
  - CPU: 4+ cores
  - RAM: 8+ GB
  - Storage: 50+ GB SSD

### Software Requirements

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- Docker 20+
- Docker Compose 2+
- Git

## Environment Setup

### Development Environment

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-organization/edu-guardian.git
   cd edu-guardian
   ```

2. **Backend Setup**:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/Scripts/activate  # On Windows
   # source .venv/bin/activate  # On Unix/Linux
   pip install -r requirements.txt
   ```

3. **Frontend Setup**:
   ```bash
   cd ../frontend
   npm install
   ```

4. **Database Setup**:
   - For local development, you can use Docker:
     ```bash
     docker-compose up -d db redis
     ```
   - Or connect to an existing NeonDB instance by configuring the environment variables

5. **Environment Configuration**:
   - Copy the example environment file:
     ```bash
     cp .env.example .env
     ```
   - Edit the `.env` file with your configuration values

### Production Environment

1. **Server Preparation**:
   - Set up a server with the required hardware specifications
   - Install Docker and Docker Compose
   - Configure firewall to allow necessary ports

2. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-organization/edu-guardian.git
   cd edu-guardian
   ```

3. **Environment Configuration**:
   - Create a production environment file:
     ```bash
     cp .env.example .env.production
     ```
   - Edit the `.env.production` file with production configuration values

4. **SSL Certificate Setup**:
   - Obtain SSL certificates for your domain
   - Place the certificates in the designated directory

## Configuration Management

### Environment Variables

The Edu-Guardian system uses environment variables for configuration. The following variables are required:

#### Database Configuration

```
DB_HOST=your-db-host
DB_PORT=5432
DB_NAME=edu_guardian
DB_USER=your-db-user
DB_PASSWORD=your-db-password
```

#### Vector Database Configuration

```
CHROMA_HOST=your-chroma-host
CHROMA_PORT=8000
```

#### Redis Configuration

```
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
```

#### API Configuration

```
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false
API_SECRET_KEY=your-secret-key
API_ALLOWED_ORIGINS=https://your-domain.com
```

#### Authentication Configuration

```
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### AI Service Configuration

```
GEMINI_API_KEY=your-gemini-api-key
```

#### Email Configuration

```
EMAIL_HOST=your-smtp-host
EMAIL_PORT=587
EMAIL_USERNAME=your-email-username
EMAIL_PASSWORD=your-email-password
EMAIL_FROM=noreply@your-domain.com
```

### Configuration Files

In addition to environment variables, the system uses the following configuration files:

- `backend/config/logging.yaml`: Logging configuration
- `backend/config/celery.yaml`: Celery configuration for background tasks
- `frontend/src/config/config.js`: Frontend configuration

## Deployment Procedures

### Docker Deployment (Recommended)

1. **Build the Docker Images**:
   ```bash
   docker-compose -f docker-compose.prod.yml build
   ```

2. **Start the Services**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Run Database Migrations**:
   ```bash
   docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
   ```

4. **Initialize Vector Database**:
   ```bash
   docker-compose -f docker-compose.prod.yml exec backend python -m scripts.init_vector_db
   ```

5. **Verify Deployment**:
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   ```

### Manual Deployment

1. **Backend Deployment**:
   ```bash
   cd backend
   source .venv/Scripts/activate  # On Windows
   # source .venv/bin/activate  # On Unix/Linux
   alembic upgrade head
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

2. **Frontend Deployment**:
   ```bash
   cd frontend
   npm run build
   ```
   - Serve the built files using Nginx or another web server

3. **Background Worker Deployment**:
   ```bash
   cd backend
   source .venv/Scripts/activate  # On Windows
   # source .venv/bin/activate  # On Unix/Linux
   celery -A app.worker worker --loglevel=info
   ```

### Deployment with Kubernetes

1. **Apply Kubernetes Manifests**:
   ```bash
   kubectl apply -f k8s/namespace.yaml
   kubectl apply -f k8s/configmap.yaml
   kubectl apply -f k8s/secret.yaml
   kubectl apply -f k8s/backend-deployment.yaml
   kubectl apply -f k8s/frontend-deployment.yaml
   kubectl apply -f k8s/worker-deployment.yaml
   kubectl apply -f k8s/service.yaml
   kubectl apply -f k8s/ingress.yaml
   ```

2. **Verify Deployment**:
   ```bash
   kubectl get pods -n edu-guardian
   ```

## CI/CD Pipeline Configuration

### GitHub Actions

The repository includes GitHub Actions workflows for continuous integration and deployment:

- `.github/workflows/ci.yml`: Runs tests and linting on pull requests
- `.github/workflows/cd.yml`: Deploys to staging or production on merge to specific branches

#### CI Workflow

The CI workflow performs the following steps:

1. Checkout code
2. Set up Python and Node.js
3. Install dependencies
4. Run linting
5. Run unit tests
6. Run integration tests

#### CD Workflow

The CD workflow performs the following steps:

1. Checkout code
2. Set up Docker Buildx
3. Login to Docker registry
4. Build and push Docker images
5. Deploy to staging or production

### Jenkins Pipeline

Alternatively, you can use the included `Jenkinsfile` for deployment with Jenkins:

```groovy
pipeline {
    agent {
        docker {
            image 'docker:20.10.16'
            args '-v /var/run/docker.sock:/var/run/docker.sock'
        }
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build') {
            steps {
                sh 'docker-compose -f docker-compose.prod.yml build'
            }
        }
        stage('Test') {
            steps {
                sh 'docker-compose -f docker-compose.test.yml up --exit-code-from tests'
            }
        }
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh 'docker-compose -f docker-compose.prod.yml up -d'
            }
        }
    }
}
```

## Scaling the Deployment

### Horizontal Scaling

To scale the application horizontally:

1. **With Docker Compose**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --scale backend=3 --scale worker=2
   ```

2. **With Kubernetes**:
   ```bash
   kubectl scale deployment backend -n edu-guardian --replicas=3
   kubectl scale deployment worker -n edu-guardian --replicas=2
   ```

### Database Scaling

- For NeonDB, scaling is managed through their dashboard
- For self-hosted PostgreSQL, consider setting up read replicas and connection pooling

## Monitoring and Logging

### Prometheus and Grafana

1. **Deploy Monitoring Stack**:
   ```bash
   docker-compose -f docker-compose.monitoring.yml up -d
   ```

2. **Access Grafana**:
   - Open `http://your-server:3000` in your browser
   - Login with the default credentials (admin/admin)
   - Import the provided dashboards from `monitoring/dashboards`

### Log Management

1. **Centralized Logging**:
   - The system is configured to send logs to a centralized logging service
   - Logs are stored in the `logs` directory by default

2. **Log Rotation**:
   - Log rotation is configured to prevent disk space issues
   - Logs are rotated daily and kept for 30 days by default

## Backup and Recovery

### Database Backup

1. **Automated Backups**:
   - NeonDB provides automated backups
   - For self-hosted PostgreSQL, use the provided backup script:
     ```bash
     ./scripts/backup_db.sh
     ```

2. **Manual Backup**:
   ```bash
   docker-compose -f docker-compose.prod.yml exec db pg_dump -U your-db-user edu_guardian > backup.sql
   ```

### Recovery Procedure

1. **Restore from Backup**:
   ```bash
   docker-compose -f docker-compose.prod.yml exec -T db psql -U your-db-user edu_guardian < backup.sql
   ```

2. **Vector Database Reindexing**:
   ```bash
   docker-compose -f docker-compose.prod.yml exec backend python -m scripts.reindex_vector_db
   ```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**:
   - Check the database credentials in the environment variables
   - Verify that the database is running and accessible
   - Check network connectivity and firewall rules

2. **API Errors**:
   - Check the API logs for detailed error messages
   - Verify that all required environment variables are set
   - Check that the database migrations have been applied

3. **Frontend Issues**:
   - Check the browser console for JavaScript errors
   - Verify that the API URL is correctly configured in the frontend
   - Clear browser cache and reload

### Diagnostic Commands

1. **Check Service Status**:
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   ```

2. **View Logs**:
   ```bash
   docker-compose -f docker-compose.prod.yml logs -f backend
   ```

3. **Check Database Connectivity**:
   ```bash
   docker-compose -f docker-compose.prod.yml exec backend python -c "from app.db.session import engine; print(engine.connect())"
   ```

4. **Verify API Health**:
   ```bash
   curl http://your-server:8000/api/health
   ```

## Security Considerations

### Production Hardening

1. **Secure Environment Variables**:
   - Use a secrets management solution for production credentials
   - Never commit sensitive information to the repository

2. **Network Security**:
   - Use a reverse proxy (e.g., Nginx) in front of the application
   - Configure proper HTTPS with strong ciphers
   - Implement IP-based access restrictions for admin interfaces

3. **Container Security**:
   - Run containers with non-root users
   - Use read-only file systems where possible
   - Regularly update base images

### Regular Updates

1. **Dependency Updates**:
   - Regularly update dependencies to patch security vulnerabilities
   - Use automated tools like Dependabot to keep dependencies up to date

2. **System Updates**:
   - Keep the host system updated with security patches
   - Configure automatic updates for critical components

## Conclusion

This deployment documentation provides a comprehensive guide for deploying and maintaining the Edu-Guardian system. Follow these instructions to ensure a smooth deployment process and reliable operation of the system.