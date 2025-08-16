# CI/CD Pipeline Configuration

## Overview

This document outlines the Continuous Integration and Continuous Deployment (CI/CD) pipeline configuration for the Edu-Guardian system. It provides detailed information on the automated build, test, and deployment processes.

## CI/CD Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Source Control │────▶│    CI Server    │────▶│  Deployment     │
│  (GitHub)       │     │  (GitHub Actions)│     │  Environments   │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## GitHub Actions Workflows

### Continuous Integration Workflow

The CI workflow runs on every pull request and push to the main branches:

```yaml
# .github/workflows/ci.yml
name: Continuous Integration

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  backend-tests:
    name: Backend Tests
    runs-on: ubuntu-latest
    env:
      ENV: testing
      DB_HOST: localhost
      DB_PORT: 5432
      DB_NAME: test_db
      DB_USER: postgres
      DB_PASSWORD: postgres
      CHROMA_HOST: localhost
      CHROMA_PORT: 8000
      REDIS_HOST: localhost
      REDIS_PORT: 6379
      REDIS_PASSWORD: redis
      API_SECRET_KEY: test_secret_key
      API_ALLOWED_ORIGINS: http://localhost:3000
      JWT_SECRET_KEY: test_jwt_secret
      GEMINI_API_KEY: ${{ secrets.TEST_GEMINI_API_KEY }}
    
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
      
      redis:
        image: redis:6
        ports:
          - 6379:6379
        options: --health-cmd "redis-cli ping" --health-interval 10s --health-timeout 5s --health-retries 5
    
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
        pip install pytest pytest-cov
    
    - name: Run linting
      run: |
        cd backend
        pip install flake8
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    
    - name: Run unit tests
      run: |
        cd backend
        pytest tests/unit --cov=app --cov-report=xml
    
    - name: Run integration tests
      run: |
        cd backend
        pytest tests/integration --cov=app --cov-report=xml --cov-append
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
        flags: backend
        fail_ci_if_error: true

  frontend-tests:
    name: Frontend Tests
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Run linting
      run: |
        cd frontend
        npm run lint
    
    - name: Run unit tests
      run: |
        cd frontend
        npm test -- --coverage
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./frontend/coverage/coverage-final.json
        flags: frontend
        fail_ci_if_error: true

  build-check:
    name: Build Check
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Build backend image
      uses: docker/build-push-action@v4
      with:
        context: ./backend
        push: false
        tags: edu-guardian/backend:test
        cache-from: type=gha
        cache-to: type=gha,mode=max
    
    - name: Build frontend image
      uses: docker/build-push-action@v4
      with:
        context: ./frontend
        push: false
        tags: edu-guardian/frontend:test
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

### Continuous Deployment Workflow

The CD workflow deploys to staging or production environments based on the branch:

```yaml
# .github/workflows/cd.yml
name: Continuous Deployment

on:
  push:
    branches:
      - main      # Production deployment
      - develop   # Staging deployment

jobs:
  deploy:
    name: Deploy
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set environment variables
      id: vars
      run: |
        if [[ ${{ github.ref }} == 'refs/heads/main' ]]; then
          echo "ENVIRONMENT=production" >> $GITHUB_ENV
          echo "DEPLOY_URL=api.edu-guardian.com" >> $GITHUB_ENV
        else
          echo "ENVIRONMENT=staging" >> $GITHUB_ENV
          echo "DEPLOY_URL=staging-api.edu-guardian.com" >> $GITHUB_ENV
        fi
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to DockerHub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
    
    - name: Build and push backend image
      uses: docker/build-push-action@v4
      with:
        context: ./backend
        push: true
        tags: |
          edu-guardian/backend:${{ github.sha }}
          edu-guardian/backend:${{ env.ENVIRONMENT }}
        build-args: |
          ENV=${{ env.ENVIRONMENT }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
    
    - name: Build and push frontend image
      uses: docker/build-push-action@v4
      with:
        context: ./frontend
        push: true
        tags: |
          edu-guardian/frontend:${{ github.sha }}
          edu-guardian/frontend:${{ env.ENVIRONMENT }}
        build-args: |
          REACT_APP_ENV=${{ env.ENVIRONMENT }}
          REACT_APP_API_URL=https://${{ env.DEPLOY_URL }}/api
        cache-from: type=gha
        cache-to: type=gha,mode=max
    
    - name: Deploy to environment
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.DEPLOY_HOST }}
        username: ${{ secrets.DEPLOY_USER }}
        key: ${{ secrets.DEPLOY_SSH_KEY }}
        script: |
          cd /opt/edu-guardian
          echo "Pulling latest images..."
          docker-compose -f docker-compose.${{ env.ENVIRONMENT }}.yml pull
          echo "Deploying new version..."
          docker-compose -f docker-compose.${{ env.ENVIRONMENT }}.yml up -d
          echo "Running database migrations..."
          docker-compose -f docker-compose.${{ env.ENVIRONMENT }}.yml exec -T backend alembic upgrade head
          echo "Cleaning up old images..."
          docker image prune -af --filter "until=24h"
    
    - name: Notify deployment status
      uses: rtCamp/action-slack-notify@v2
      env:
        SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
        SLACK_CHANNEL: deployments
        SLACK_COLOR: ${{ job.status }}
        SLACK_TITLE: Deployment to ${{ env.ENVIRONMENT }}
        SLACK_MESSAGE: 'Deployed version ${{ github.sha }} to ${{ env.ENVIRONMENT }} environment'
        SLACK_FOOTER: 'Edu-Guardian CI/CD Pipeline'
```

## Docker Compose Configuration

### Development Environment

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    environment:
      - ENV=development
    env_file:
      - .env.development
    depends_on:
      - db
      - redis
  
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_ENV=development
    env_file:
      - .env.development
  
  db:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=${DB_NAME}
    ports:
      - "5432:5432"
  
  redis:
    image: redis:6
    ports:
      - "6379:6379"
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Staging Environment

```yaml
# docker-compose.staging.yml
version: '3.8'

services:
  backend:
    image: edu-guardian/backend:staging
    restart: always
    ports:
      - "8000:8000"
    environment:
      - ENV=staging
    env_file:
      - .env.staging
    depends_on:
      - redis
  
  frontend:
    image: edu-guardian/frontend:staging
    restart: always
    ports:
      - "3000:80"
  
  redis:
    image: redis:6
    restart: always
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
  
  worker:
    image: edu-guardian/backend:staging
    restart: always
    command: celery -A app.worker worker --loglevel=info
    environment:
      - ENV=staging
    env_file:
      - .env.staging
    depends_on:
      - redis
  
  nginx:
    image: nginx:1.21
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/staging.conf:/etc/nginx/conf.d/default.conf
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    depends_on:
      - backend
      - frontend
  
  certbot:
    image: certbot/certbot
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"

volumes:
  redis_data:
```

### Production Environment

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  backend:
    image: edu-guardian/backend:production
    restart: always
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
        order: start-first
      restart_policy:
        condition: any
        delay: 5s
        max_attempts: 3
        window: 120s
    ports:
      - "8000:8000"
    environment:
      - ENV=production
    env_file:
      - .env.production
    depends_on:
      - redis
  
  frontend:
    image: edu-guardian/frontend:production
    restart: always
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        delay: 10s
        order: start-first
      restart_policy:
        condition: any
        delay: 5s
        max_attempts: 3
        window: 120s
    ports:
      - "3000:80"
  
  redis:
    image: redis:6
    restart: always
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    deploy:
      restart_policy:
        condition: any
        delay: 5s
        max_attempts: 3
        window: 120s
  
  worker:
    image: edu-guardian/backend:production
    restart: always
    command: celery -A app.worker worker --loglevel=info
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        delay: 10s
        order: start-first
      restart_policy:
        condition: any
        delay: 5s
        max_attempts: 3
        window: 120s
    environment:
      - ENV=production
    env_file:
      - .env.production
    depends_on:
      - redis
  
  nginx:
    image: nginx:1.21
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/production.conf:/etc/nginx/conf.d/default.conf
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    depends_on:
      - backend
      - frontend
    deploy:
      restart_policy:
        condition: any
        delay: 5s
        max_attempts: 3
        window: 120s
  
  certbot:
    image: certbot/certbot
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"

volumes:
  redis_data:
```

## Kubernetes Deployment

### Namespace Configuration

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: edu-guardian
```

### ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: edu-guardian-config
  namespace: edu-guardian
data:
  ENV: "production"
  DB_HOST: "neon-db-host"
  DB_PORT: "5432"
  DB_NAME: "edu_guardian"
  CHROMA_HOST: "chroma-service"
  CHROMA_PORT: "8000"
  REDIS_HOST: "redis-service"
  REDIS_PORT: "6379"
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  API_DEBUG: "false"
  API_ALLOWED_ORIGINS: "https://edu-guardian.com"
  LOG_LEVEL: "INFO"
  LOG_FORMAT: "json"
  FEATURE_ADVANCED_EMOTION: "true"
  FEATURE_PREDICTIVE_ANALYTICS: "true"
```

### Secrets

```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: edu-guardian-secrets
  namespace: edu-guardian
type: Opaque
data:
  DB_USER: base64_encoded_user
  DB_PASSWORD: base64_encoded_password
  REDIS_PASSWORD: base64_encoded_redis_password
  API_SECRET_KEY: base64_encoded_api_secret
  JWT_SECRET_KEY: base64_encoded_jwt_secret
  JWT_ALGORITHM: base64_encoded_algorithm
  JWT_ACCESS_TOKEN_EXPIRE_MINUTES: base64_encoded_minutes
  GEMINI_API_KEY: base64_encoded_gemini_key
  EMAIL_HOST: base64_encoded_email_host
  EMAIL_PORT: base64_encoded_email_port
  EMAIL_USERNAME: base64_encoded_email_username
  EMAIL_PASSWORD: base64_encoded_email_password
  EMAIL_FROM: base64_encoded_email_from
```

### Backend Deployment

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
        image: edu-guardian/backend:production
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: edu-guardian-config
        - secretRef:
            name: edu-guardian-secrets
        resources:
          limits:
            cpu: "1"
            memory: "2Gi"
          requests:
            cpu: "500m"
            memory: "1Gi"
        readinessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 20
```

### Frontend Deployment

```yaml
# k8s/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: edu-guardian
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: edu-guardian/frontend:production
        ports:
        - containerPort: 80
        resources:
          limits:
            cpu: "500m"
            memory: "512Mi"
          requests:
            cpu: "200m"
            memory: "256Mi"
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 15
          periodSeconds: 20
```

### Worker Deployment

```yaml
# k8s/worker-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: worker
  namespace: edu-guardian
spec:
  replicas: 2
  selector:
    matchLabels:
      app: worker
  template:
    metadata:
      labels:
        app: worker
    spec:
      containers:
      - name: worker
        image: edu-guardian/backend:production
        command: ["celery", "-A", "app.worker", "worker", "--loglevel=info"]
        envFrom:
        - configMapRef:
            name: edu-guardian-config
        - secretRef:
            name: edu-guardian-secrets
        resources:
          limits:
            cpu: "1"
            memory: "2Gi"
          requests:
            cpu: "500m"
            memory: "1Gi"
```

### Services

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: edu-guardian
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  namespace: edu-guardian
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
  namespace: edu-guardian
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
  type: ClusterIP
```

### Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: edu-guardian-ingress
  namespace: edu-guardian
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - api.edu-guardian.com
    - edu-guardian.com
    secretName: edu-guardian-tls
  rules:
  - host: api.edu-guardian.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8000
  - host: edu-guardian.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
```

## Deployment Strategies

### Blue-Green Deployment

For zero-downtime deployments, we use a blue-green deployment strategy:

1. Deploy the new version alongside the existing version
2. Run smoke tests on the new version
3. Switch traffic to the new version
4. Monitor for any issues
5. If successful, remove the old version; if not, roll back to the old version

### Canary Deployment

For high-risk changes, we use a canary deployment strategy:

1. Deploy the new version to a small subset of users (e.g., 10%)
2. Monitor for any issues
3. Gradually increase the percentage of users on the new version
4. If successful, complete the rollout; if not, roll back to the old version

## Monitoring and Alerting

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
  - static_configs:
    - targets:
      - alertmanager:9093

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
    - targets: ['localhost:9090']

  - job_name: 'backend'
    metrics_path: '/api/metrics'
    static_configs:
    - targets: ['backend:8000']

  - job_name: 'node-exporter'
    static_configs:
    - targets: ['node-exporter:9100']

  - job_name: 'cadvisor'
    static_configs:
    - targets: ['cadvisor:8080']
```

### Alert Rules

```yaml
# monitoring/alert_rules.yml
groups:
- name: edu-guardian
  rules:
  - alert: HighCPUUsage
    expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: High CPU usage detected
      description: CPU usage is above 80% for more than 5 minutes.

  - alert: HighMemoryUsage
    expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: High memory usage detected
      description: Memory usage is above 80% for more than 5 minutes.

  - alert: APIHighResponseTime
    expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le)) > 1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: API response time is high
      description: 95th percentile of API response time is above 1 second for more than 5 minutes.

  - alert: APIHighErrorRate
    expr: sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) > 0.05
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: API error rate is high
      description: API error rate is above 5% for more than 5 minutes.
```

## Rollback Procedures

### Docker Compose Rollback

```bash
# Rollback to previous version
docker-compose -f docker-compose.production.yml down
docker tag edu-guardian/backend:previous edu-guardian/backend:production
docker tag edu-guardian/frontend:previous edu-guardian/frontend:production
docker-compose -f docker-compose.production.yml up -d
```

### Kubernetes Rollback

```bash
# Rollback to previous version
kubectl rollout undo deployment/backend -n edu-guardian
kubectl rollout undo deployment/frontend -n edu-guardian
kubectl rollout undo deployment/worker -n edu-guardian
```

## Conclusion

This CI/CD pipeline configuration provides a robust framework for automating the build, test, and deployment processes of the Edu-Guardian system. By following these practices, you can ensure consistent, reliable, and efficient deployments across different environments.