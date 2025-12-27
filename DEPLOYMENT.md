# 🚀 Deployment Guide

This guide covers deploying the Cryptocurrency ETL & Backend System to production.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Local Testing](#local-testing)
- [AWS Deployment](#aws-deployment)
- [GCP Deployment](#gcp-deployment)
- [Azure Deployment](#azure-deployment)
- [Monitoring & Maintenance](#monitoring--maintenance)

## Prerequisites

- Docker & Docker Compose installed
- Cloud provider account (AWS/GCP/Azure)
- CoinPaprika API key (free from https://coinpaprika.com/)
- Domain name (optional, for custom URLs)

## Local Testing

### 1. Initial Setup

```bash
# Clone repository
cd /Users/charannaik/Documents/codes/BackendAssign

# Copy environment template
cp .env.example .env

# Edit .env and add your CoinPaprika API key
# COINPAPRIKA_API_KEY=your_actual_key_here
```

### 2. Build and Start

```bash
# Build Docker images
make build

# Start all services
make up

# Check logs
make logs
```

### 3. Verify Health

```bash
# Health check
curl http://localhost:8000/health

# Get data
curl "http://localhost:8000/data?page=1&page_size=5"

# Check stats
curl http://localhost:8000/stats

# View metrics
curl http://localhost:8000/metrics
```

### 4. Run Tests

```bash
# Run full test suite
make test

# Or run locally
pytest tests/ -v --cov=. --cov-report=html
```

### 5. Smoke Test

```bash
make smoke-test
```

## AWS Deployment

### Option 1: ECS (Elastic Container Service)

#### Step 1: Create ECR Repository

```bash
# Login to AWS
aws configure

# Create ECR repository
aws ecr create-repository \
    --repository-name crypto-etl-backend \
    --region us-east-1

# Get login credentials
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin \
    <account-id>.dkr.ecr.us-east-1.amazonaws.com
```

#### Step 2: Build and Push Docker Image

```bash
# Build image
docker build -t crypto-etl-backend .

# Tag for ECR
docker tag crypto-etl-backend:latest \
    <account-id>.dkr.ecr.us-east-1.amazonaws.com/crypto-etl-backend:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/crypto-etl-backend:latest
```

#### Step 3: Create RDS PostgreSQL Database

```bash
# Create RDS instance
aws rds create-db-instance \
    --db-instance-identifier crypto-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --engine-version 15.3 \
    --master-username crypto_user \
    --master-user-password <your-secure-password> \
    --allocated-storage 20 \
    --vpc-security-group-ids <security-group-id> \
    --db-name crypto_db \
    --region us-east-1
```

#### Step 4: Create ECS Task Definition

Create `ecs-task-definition.json`:

```json
{
  "family": "crypto-etl-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "crypto-etl-backend",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/crypto-etl-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "APP_ENV",
          "value": "production"
        },
        {
          "name": "LOG_LEVEL",
          "value": "INFO"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:<account-id>:secret:crypto-db-url"
        },
        {
          "name": "COINPAPRIKA_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:<account-id>:secret:coinpaprika-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/crypto-etl-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

Register task definition:

```bash
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json
```

#### Step 5: Create ECS Service

```bash
aws ecs create-service \
    --cluster crypto-cluster \
    --service-name crypto-etl-service \
    --task-definition crypto-etl-backend \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
    --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:<account-id>:targetgroup/crypto-tg/xxx,containerName=crypto-etl-backend,containerPort=8000"
```

#### Step 6: Set Up EventBridge for Scheduled ETL

Create rule for scheduled ETL runs:

```bash
aws events put-rule \
    --name crypto-etl-schedule \
    --schedule-expression "rate(30 minutes)" \
    --state ENABLED
```

Add ECS task as target:

```bash
aws events put-targets \
    --rule crypto-etl-schedule \
    --targets "Id=1,Arn=arn:aws:ecs:us-east-1:<account-id>:cluster/crypto-cluster,RoleArn=arn:aws:iam::<account-id>:role/ecsEventsRole,EcsParameters={TaskDefinitionArn=arn:aws:ecs:us-east-1:<account-id>:task-definition/crypto-etl-backend,TaskCount=1,LaunchType=FARGATE}"
```

### Option 2: EC2 with Docker Compose

#### Launch EC2 Instance

```bash
# Launch EC2 instance (Ubuntu 22.04)
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t3.small \
    --key-name your-key-pair \
    --security-group-ids sg-xxx \
    --subnet-id subnet-xxx \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=crypto-etl-backend}]'
```

#### Setup EC2

SSH into instance and run:

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone <your-repo-url> crypto-etl
cd crypto-etl

# Set environment variables
nano .env
# Add your configuration

# Start services
docker-compose up -d
```

## GCP Deployment

### Option 1: Cloud Run

#### Step 1: Setup GCP

```bash
# Set project
gcloud config set project crypto-etl-project

# Enable APIs
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

#### Step 2: Create Cloud SQL Instance

```bash
gcloud sql instances create crypto-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1

gcloud sql databases create crypto_db --instance=crypto-db

gcloud sql users create crypto_user \
    --instance=crypto-db \
    --password=<secure-password>
```

#### Step 3: Build and Push to Container Registry

```bash
# Build image
gcloud builds submit --tag gcr.io/crypto-etl-project/crypto-etl-backend

# Or use Docker
docker build -t gcr.io/crypto-etl-project/crypto-etl-backend .
docker push gcr.io/crypto-etl-project/crypto-etl-backend
```

#### Step 4: Deploy to Cloud Run

```bash
gcloud run deploy crypto-etl-backend \
    --image gcr.io/crypto-etl-project/crypto-etl-backend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars "APP_ENV=production,LOG_LEVEL=INFO" \
    --set-secrets "DATABASE_URL=crypto-db-url:latest,COINPAPRIKA_API_KEY=coinpaprika-key:latest" \
    --add-cloudsql-instances crypto-etl-project:us-central1:crypto-db
```

#### Step 5: Set Up Cloud Scheduler for ETL

```bash
gcloud scheduler jobs create http crypto-etl-schedule \
    --schedule="*/30 * * * *" \
    --uri="https://crypto-etl-backend-xxx.run.app/etl/run" \
    --http-method=POST \
    --oidc-service-account-email=<service-account>@crypto-etl-project.iam.gserviceaccount.com
```

## Azure Deployment

### Option 1: Azure Container Instances with Azure Database

#### Step 1: Create Resource Group

```bash
az group create --name crypto-etl-rg --location eastus
```

#### Step 2: Create Azure Database for PostgreSQL

```bash
az postgres flexible-server create \
    --resource-group crypto-etl-rg \
    --name crypto-db-server \
    --location eastus \
    --admin-user crypto_user \
    --admin-password <secure-password> \
    --sku-name Standard_B1ms \
    --version 15

az postgres flexible-server db create \
    --resource-group crypto-etl-rg \
    --server-name crypto-db-server \
    --database-name crypto_db
```

#### Step 3: Create Container Registry

```bash
az acr create \
    --resource-group crypto-etl-rg \
    --name cryptoetlregistry \
    --sku Basic
```

#### Step 4: Build and Push Image

```bash
az acr build \
    --registry cryptoetlregistry \
    --image crypto-etl-backend:latest .
```

#### Step 5: Deploy Container Instance

```bash
az container create \
    --resource-group crypto-etl-rg \
    --name crypto-etl-backend \
    --image cryptoetlregistry.azurecr.io/crypto-etl-backend:latest \
    --cpu 1 \
    --memory 1 \
    --registry-login-server cryptoetlregistry.azurecr.io \
    --registry-username <registry-username> \
    --registry-password <registry-password> \
    --dns-name-label crypto-etl-api \
    --ports 8000 \
    --environment-variables \
        APP_ENV=production \
        LOG_LEVEL=INFO \
    --secure-environment-variables \
        DATABASE_URL=<connection-string> \
        COINPAPRIKA_API_KEY=<your-key>
```

#### Step 6: Set Up Azure Logic Apps for Scheduled ETL

Create a Logic App with HTTP trigger scheduled every 30 minutes to call your API's `/etl/run` endpoint.

## Monitoring & Maintenance

### CloudWatch (AWS)

```bash
# View logs
aws logs tail /ecs/crypto-etl-backend --follow

# Create alarm for errors
aws cloudwatch put-metric-alarm \
    --alarm-name crypto-etl-errors \
    --alarm-description "Alert on ETL errors" \
    --metric-name Errors \
    --namespace AWS/ECS \
    --statistic Sum \
    --period 300 \
    --threshold 5 \
    --comparison-operator GreaterThanThreshold
```

### Cloud Logging (GCP)

```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=crypto-etl-backend" --limit 50

# Create alert
gcloud alpha monitoring policies create \
    --notification-channels=<channel-id> \
    --display-name="ETL Errors" \
    --condition-display-name="Error rate" \
    --condition-threshold-value=5
```

### Prometheus Metrics

The `/metrics` endpoint exposes Prometheus-compatible metrics:

```prometheus
# ETL metrics
etl_runs_total
etl_duration_seconds
etl_records_processed

# API metrics
api_requests_total
api_latency_seconds
```

### Health Checks

Set up periodic health checks:

```bash
# Simple health check script
#!/bin/bash
HEALTH_URL="https://your-api-url/health"

response=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $response != "200" ]; then
    echo "Health check failed with status: $response"
    # Send alert
fi
```

### Backup Strategy

```bash
# Automated PostgreSQL backups (AWS RDS)
aws rds create-db-snapshot \
    --db-instance-identifier crypto-db \
    --db-snapshot-identifier crypto-db-backup-$(date +%Y%m%d)

# GCP Cloud SQL automated backups (enabled by default)
gcloud sql backups create --instance=crypto-db
```

## Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check security groups/firewall rules
# Verify DATABASE_URL environment variable
# Test connection manually
psql $DATABASE_URL
```

**ETL Not Running**
```bash
# Check logs
docker-compose logs app

# Manually trigger ETL
curl -X POST http://localhost:8000/etl/run

# Verify API keys
env | grep API_KEY
```

**High Memory Usage**
```bash
# Reduce batch sizes in .env
CSV_BATCH_SIZE=50

# Increase container memory limits in docker-compose.yml
```

## Security Best Practices

1. **Never commit `.env` files** - Use secrets management
2. **Rotate API keys** regularly
3. **Use HTTPS** in production
4. **Enable database encryption** at rest
5. **Implement rate limiting** at the API gateway level
6. **Regular security updates** for dependencies

## Cost Optimization

### AWS
- Use Fargate Spot for non-critical workloads
- Enable auto-scaling based on CPU/memory
- Use RDS Reserved Instances for production

### GCP
- Use Cloud Run with minimum instances = 0
- Enable Cloud SQL automatic storage increase
- Use committed use discounts

### Azure
- Use Azure Container Instances with dynamic allocation
- Enable auto-pause for development databases
- Use Azure Reserved Instances

---

**Next Steps:**
1. Deploy to your chosen cloud platform
2. Set up monitoring and alerts
3. Configure automated backups
4. Implement CI/CD pipeline (see `.github/workflows/` for examples)
5. Set up custom domain and SSL certificate
