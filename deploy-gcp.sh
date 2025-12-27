#!/bin/bash
set -e

echo "=== GCP Cloud Run Deployment Script ==="
echo ""

# Configuration
PROJECT_ID="${GCP_PROJECT_ID}"
REGION="us-central1"
SERVICE_NAME="crypto-etl-backend"
SQL_INSTANCE_NAME="crypto-postgres"
DATABASE_NAME="crypto_etl"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if project ID is set
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: GCP_PROJECT_ID environment variable not set${NC}"
    echo "Please set it with: export GCP_PROJECT_ID=your-project-id"
    exit 1
fi

echo -e "${YELLOW}Project ID: ${PROJECT_ID}${NC}"
echo -e "${YELLOW}Region: ${REGION}${NC}"
echo -e "${YELLOW}Service Name: ${SERVICE_NAME}${NC}"
echo ""

# Step 1: Build and push container to Artifact Registry
echo -e "${GREEN}Step 1: Building and pushing container...${NC}"
gcloud builds submit --tag gcr.io/${PROJECT_ID}/${SERVICE_NAME} \
    --dockerfile=Dockerfile.cloudrun \
    --project=${PROJECT_ID}

# Step 2: Get Cloud SQL connection name
echo -e "${GREEN}Step 2: Getting Cloud SQL connection info...${NC}"
SQL_CONNECTION_NAME=$(gcloud sql instances describe ${SQL_INSTANCE_NAME} \
    --project=${PROJECT_ID} \
    --format='value(connectionName)')

echo "Cloud SQL Connection Name: ${SQL_CONNECTION_NAME}"

# Step 3: Deploy to Cloud Run
echo -e "${GREEN}Step 3: Deploying to Cloud Run...${NC}"
gcloud run deploy ${SERVICE_NAME} \
    --image gcr.io/${PROJECT_ID}/${SERVICE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --add-cloudsql-instances ${SQL_CONNECTION_NAME} \
    --set-env-vars "DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@/${DATABASE_NAME}?host=/cloudsql/${SQL_CONNECTION_NAME}" \
    --set-env-vars "ENVIRONMENT=production" \
    --set-env-vars "LOG_LEVEL=INFO" \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --timeout 300 \
    --project=${PROJECT_ID}

# Step 4: Get the service URL
echo -e "${GREEN}Step 4: Getting service URL...${NC}"
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --platform managed \
    --region ${REGION} \
    --project=${PROJECT_ID} \
    --format='value(status.url)')

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Service URL: ${YELLOW}${SERVICE_URL}${NC}"
echo ""
echo "Test your endpoints:"
echo "  Health: ${SERVICE_URL}/health"
echo "  Data:   ${SERVICE_URL}/data"
echo "  Stats:  ${SERVICE_URL}/stats"
echo ""
echo -e "${YELLOW}Note: Update the DATABASE_URL password in the deployment command before running!${NC}"
