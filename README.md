# 🚀 Cryptocurrency ETL & Backend System

A production-grade backend system for ingesting, normalizing, and serving cryptocurrency data from multiple sources.

## 📋 Table of Contents
- [Architecture Overview](#architecture-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)

## 🏗️ Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  CoinPaprika    │     │   CoinGecko     │     │   CSV Source    │
│      API        │     │      API        │     │    (Local)      │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         └───────────────┬───────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   ETL Ingestion      │
              │   - Rate Limiting    │
              │   - Retry Logic      │
              │   - Validation       │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   PostgreSQL DB      │
              │   - raw_* tables     │
              │   - normalized data  │
              │   - checkpoints      │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   FastAPI Backend    │
              │   - /data            │
              │   - /health          │
              │   - /stats           │
              │   - /metrics         │
              └──────────────────────┘
```

### Design Decisions

**1. Incremental Ingestion Strategy**
- Checkpoint-based tracking per data source
- Idempotent writes using upsert operations
- Resume-on-failure capability with last successful state

**2. Schema Normalization**
- Unified `coins` table with source tracking
- Type validation using Pydantic models
- Automatic data type coercion and cleaning

**3. Error Handling & Recovery**
- Exponential backoff for API failures
- Circuit breaker pattern for sustained failures
- Comprehensive logging with structured JSON format

**4. Rate Limiting**
- Per-source rate limit configuration
- Token bucket algorithm implementation
- Automatic request throttling

## ✨ Features

### P0 - Foundation Layer ✅
- ✅ ETL pipeline for CoinPaprika API
- ✅ ETL pipeline for CSV source
- ✅ Raw data storage in PostgreSQL
- ✅ Normalized unified schema
- ✅ Type validation with Pydantic
- ✅ Incremental ingestion
- ✅ Secure API key handling
- ✅ GET /data endpoint (pagination, filtering, metadata)
- ✅ GET /health endpoint (DB + ETL status)
- ✅ Dockerized system (make up/down/test)
- ✅ Basic test suite

### P1 - Growth Layer ✅
- ✅ CoinGecko API as third data source
- ✅ Checkpoint table for state management
- ✅ Resume-on-failure logic
- ✅ Idempotent writes
- ✅ GET /stats endpoint (ETL summaries)
- ✅ Comprehensive test coverage
- ✅ Clean architecture with separation of concerns

### P2 - Differentiator Layer ✅
- ✅ Rate limiting with exponential backoff
- ✅ Observability with /metrics endpoint
- ✅ Structured JSON logging
- ✅ ETL metadata tracking
- ✅ Docker health checks
- ✅ Failure injection testing

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic v2
- **Testing**: pytest, pytest-asyncio
- **Containerization**: Docker, Docker Compose
- **Task Orchestration**: APScheduler
- **Monitoring**: Prometheus metrics format

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Make (optional, for convenience)

**Note**: Both CoinPaprika and CoinGecko free tiers work without API keys!

### Setup

1. **Clone and navigate to the project**
```bash
cd /Users/charannaik/Documents/codes/BackendAssign
```

2. **Start the system (no API key needed!)**
```bash
make up
```

3. **Verify health**
```bash
curl http://localhost:8000/health
```

4. **Stop the system**
```bash
make down
```

### Makefile Commands

```bash
make up          # Start all services (PostgreSQL + API)
make down        # Stop all services
make test        # Run test suite
make logs        # View application logs
make db-migrate  # Run database migrations
make clean       # Clean up containers and volumes
```

## 📚 API Documentation

Once running, visit:
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints

#### GET /data
Retrieve cryptocurrency data with pagination and filtering.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 50, max: 100)
- `source` (str): Filter by data source (coinpaprika, coingecko, csv)
- `symbol` (str): Filter by cryptocurrency symbol (e.g., BTC, ETH)

**Response:**
```json
{
  "data": [...],
  "metadata": {
    "request_id": "uuid-here",
    "api_latency_ms": 45.2,
    "page": 1,
    "page_size": 50,
    "total_count": 150
  }
}
```

#### GET /health
System health check.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "etl_status": {
    "last_run": "2025-12-27T10:30:00Z",
    "status": "success",
    "sources": {
      "coinpaprika": "success",
      "coingecko": "success",
      "csv": "success"
    }
  }
}
```

#### GET /stats
ETL execution statistics.

**Response:**
```json
{
  "total_runs": 42,
  "records_processed": 15420,
  "last_success": "2025-12-27T10:30:00Z",
  "last_failure": "2025-12-26T15:20:00Z",
  "average_duration_seconds": 12.5,
  "by_source": {
    "coinpaprika": {...},
    "coingecko": {...},
    "csv": {...}
  }
}
```

#### GET /metrics
Prometheus-compatible metrics.

## 📁 Project Structure

```
BackendAssign/
├── ingestion/              # ETL pipeline modules
│   ├── __init__.py
│   ├── base.py            # Base ETL class
│   ├── coinpaprika.py     # CoinPaprika ETL
│   ├── coingecko.py       # CoinGecko ETL
│   └── csv_source.py      # CSV ETL
├── api/                    # FastAPI application
│   ├── __init__.py
│   ├── main.py            # FastAPI app initialization
│   ├── routes.py          # API route handlers
│   └── dependencies.py    # Dependency injection
├── services/               # Business logic layer
│   ├── __init__.py
│   ├── etl_service.py     # ETL orchestration
│   └── data_service.py    # Data retrieval service
├── schemas/                # Pydantic models
│   ├── __init__.py
│   ├── coin.py            # Coin data schemas
│   └── api_models.py      # API request/response models
├── core/                   # Core utilities
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── database.py        # Database connection
│   ├── models.py          # SQLAlchemy ORM models
│   ├── logging.py         # Structured logging
│   └── rate_limiter.py    # Rate limiting implementation
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── conftest.py        # Pytest fixtures
│   ├── test_etl.py        # ETL tests
│   ├── test_api.py        # API endpoint tests
│   └── test_integration.py # Integration tests
├── data/                   # Sample data files
│   └── crypto_data.csv    # Sample CSV data
├── docker-compose.yml      # Multi-container setup
├── Dockerfile             # Application container
├── Makefile               # Build automation
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
└── README.md              # This file
```

## 🧪 Testing

### Run All Tests
```bash
make test
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/test_etl.py -v

# Integration tests
pytest tests/test_integration.py -v

# With coverage
pytest --cov=. --cov-report=html
```

### Test Coverage Includes
- ✅ ETL transformation logic
- ✅ Incremental ingestion
- ✅ Failure recovery scenarios
- ✅ Schema validation
- ✅ API endpoints
- ✅ Rate limiting
- ✅ Database operations

## 🔧 Development

### Local Development Setup

1. **Create virtual environment**
```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Start PostgreSQL**
```bash
docker-compose up -d postgres
```

4. **Run migrations**
```bash
python -m alembic upgrade head
```

5. **Start development server**
```bash
uvicorn api.main:app --reload --port 8000
```

### Adding New Data Sources

1. Create new ETL class in `ingestion/`
2. Inherit from `BaseETL`
3. Implement `extract()`, `transform()`, `load()` methods
4. Register in `services/etl_service.py`
5. Add tests in `tests/test_etl.py`

## 🚀 Deployment

### Docker Deployment

The system is designed to run entirely in Docker:

```bash
# Build and start
docker-compose up --build -d

# View logs
docker-compose logs -f app

# Stop
docker-compose down
```

### Cloud Deployment (AWS Example)

**Prerequisites:**
- AWS Account
- AWS CLI configured
- ECR repository created

**Steps:**

1. **Build and push Docker image**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and tag
docker build -t crypto-etl-backend .
docker tag crypto-etl-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/crypto-etl-backend:latest

# Push
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/crypto-etl-backend:latest
```

2. **Deploy to ECS/EKS** (See DEPLOYMENT.md for detailed AWS/GCP/Azure guides)

3. **Set up EventBridge cron** for scheduled ETL runs

### Environment Variables

Required environment variables:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/crypto_db

# API Keys (Optional - free tiers don't require keys)
COINPAPRIKA_API_KEY=
COINGECKO_API_KEY=

# Application
APP_ENV=production
LOG_LEVEL=INFO
ENABLE_METRICS=true

# Rate Limiting
COINPAPRIKA_RATE_LIMIT=10
COINGECKO_RATE_LIMIT=50
```

## 📊 Monitoring & Observability

### Structured Logging
All logs are in JSON format for easy parsing:
```json
{
  "timestamp": "2025-12-27T10:30:00Z",
  "level": "INFO",
  "service": "etl",
  "source": "coinpaprika",
  "message": "ETL run completed",
  "duration_seconds": 12.5,
  "records_processed": 150
}
```

### Metrics
Prometheus metrics available at `/metrics`:
- `etl_runs_total` - Total ETL executions
- `etl_duration_seconds` - ETL execution time
- `etl_records_processed` - Records processed per run
- `api_requests_total` - API request counter
- `api_latency_seconds` - API response time

## 🐛 Troubleshooting

### Common Issues

**ETL Not Running**
```bash
# Check logs
docker-compose logs app

# Verify environment variables
docker-compose exec app env | grep API_KEY
```

**Database Connection Failed**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres psql -U crypto_user -d crypto_db
```

**Rate Limit Errors**
- Check your API key validity
- Verify rate limit settings in `.env`
- Review logs for backoff behavior

## ✅ Deployment Verification

### Live Production Deployment

**Production URL**: https://kasparro-backend-charan-naik.onrender.com
**Platform**: Render.com
**Status**: ✅ LIVE AND OPERATIONAL

### Verify Deployment from Code

This project includes comprehensive deployment verification:

#### 1. Automated Verification Script
```bash
# Run the deployment verification script
./verify-deployment.sh
```

This script verifies:
- ✅ API is accessible
- ✅ Database connection
- ✅ ETL pipeline operational
- ✅ All endpoints responding
- ✅ HTTPS certificate valid
- ✅ Prometheus metrics available

#### 2. Manual Verification Commands

```bash
# Health check
curl https://kasparro-backend-charan-naik.onrender.com/health

# Get cryptocurrency data
curl "https://kasparro-backend-charan-naik.onrender.com/data?limit=5"

# View ETL statistics
curl https://kasparro-backend-charan-naik.onrender.com/stats

# Interactive API docs
open https://kasparro-backend-charan-naik.onrender.com/docs
```

#### 3. Deployment Configuration Files

The deployment is verifiable from the codebase:

- **`render.json`** - Render Blueprint with exact service configuration
- **`render.yaml`** - Infrastructure-as-code deployment specification
- **`Dockerfile`** - Production container configuration
- **`DEPLOYMENT_VERIFICATION.md`** - Comprehensive deployment documentation
- **`verify-deployment.sh`** - Automated verification script

#### 4. Expected Responses

**Health Endpoint** (`/health`):
```json
{
  "status": "healthy",
  "database": "connected",
  "etl_status": {
    "sources": {
      "csv": "success",
      "coinpaprika": "success",
      "coingecko": "failure"
    }
  }
}
```
*Note: CoinGecko may show "failure" due to rate limiting on free tier (expected)*

**Data Endpoint** (`/data?limit=3`):
```json
{
  "data": [
    {
      "coin_id": "btc-bitcoin",
      "symbol": "BTC",
      "name": "Bitcoin",
      "current_price": 87440.0,
      "market_cap": 1745978218739.0,
      ...
    }
  ],
  "metadata": {
    "total_count": 115,
    "page": 1,
    "page_size": 50
  }
}
```

#### 5. Deployment Architecture

```
GitHub Repository (main branch)
    ↓
Render.com (Auto-deploy on push)
    ↓
Docker Build (Multi-stage)
    ↓
Container Deployment
    ↓
PostgreSQL Database (Render)
    ↓
Public HTTPS Endpoint
```

### Deployment Evidence

1. **Code-Based Proof**:
   - `render.json` blueprint matches deployed configuration
   - Dockerfile builds successfully
   - Environment variables properly configured
   - Health checks implemented

2. **Runtime Proof**:
   - Live API responses from production URL
   - Database connectivity verified via `/health`
   - ETL pipeline execution shown in `/stats`
   - 115+ cryptocurrency records loaded

3. **Infrastructure Proof**:
   - HTTPS certificate valid (Render-provided SSL)
   - Render headers in HTTP responses
   - GitHub integration active (auto-deploy)
   - PostgreSQL database operational

See `DEPLOYMENT_VERIFICATION.md` for complete deployment verification documentation.

## 📄 License

This project is part of the Kasparro internship assignment.

## 👨‍💻 Author

Built with production-grade standards and modern engineering practices.

---

**Note**: This system demonstrates end-to-end ownership of a production backend system with ETL pipelines, clean architecture, comprehensive testing, and deployment-ready configuration.
