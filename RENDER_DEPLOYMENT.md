# Render.com Deployment Guide

## Prerequisites
- GitHub account
- Render.com account (free - no credit card needed)

## Deployment Steps

### 1. Push Code to GitHub

```bash
# Initialize git (if not already done)
cd /Users/charannaik/Documents/codes/BackendAssign
git init

# Add all files
git add .
git commit -m "Initial commit - Crypto ETL Backend"

# Create repo on GitHub and push
git remote add origin https://github.com/YOUR_USERNAME/crypto-etl-backend.git
git branch -M main
git push -u origin main
```

### 2. Create Render Account
1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access your repositories

### 3. Create PostgreSQL Database

1. Click **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name**: `crypto-postgres`
   - **Database**: `crypto_etl`
   - **User**: `crypto_user` (or leave default)
   - **Region**: Choose closest to you
   - **Plan**: **Free**
3. Click **"Create Database"**
4. Wait ~2 minutes for database to provision
5. **Save the "Internal Database URL"** from the database info page

### 4. Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `crypto-etl-backend`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Runtime**: **Docker**
   - **Dockerfile Path**: `./Dockerfile` (use existing one)
   - **Plan**: **Free**

4. **Environment Variables** (click "Advanced"):
   ```
   DATABASE_URL = [paste Internal Database URL from step 3]
   ENVIRONMENT = production
   LOG_LEVEL = INFO
   ```

5. Click **"Create Web Service"**

### 5. Wait for Deployment
- First deployment takes 5-10 minutes
- Watch the logs in Render dashboard
- You'll see: "Starting application...", "Database initialized", etc.

### 6. Get Your URL
- Once deployed, Render provides a URL like: `https://crypto-etl-backend-xxxx.onrender.com`
- Test it: `https://YOUR-URL.onrender.com/health`

## Testing Your Deployment

```bash
# Health check
curl https://YOUR-URL.onrender.com/health

# Get data
curl https://YOUR-URL.onrender.com/data?limit=10

# Get stats
curl https://YOUR-URL.onrender.com/stats

# API docs
open https://YOUR-URL.onrender.com/docs
```

## Important Notes

### Free Tier Limitations
- **Database**: 90 days free, then needs upgrade or migrate
- **Web Service**: Spins down after 15 min of inactivity (cold start ~30s)
- **Resources**: 512 MB RAM, 0.1 CPU
- Perfect for demo/internship submission!

### Cold Starts
- First request after inactivity takes ~30 seconds
- Subsequent requests are instant
- This is normal for free tier

### Environment Variables
If you need to update environment variables:
1. Go to your service dashboard
2. Click **"Environment"** tab
3. Add/edit variables
4. Service will auto-redeploy

### Logs
View real-time logs:
1. Go to service dashboard
2. Click **"Logs"** tab
3. See all application output

## Troubleshooting

### Database Connection Failed
- Check DATABASE_URL is set correctly
- Verify internal database URL (not external)
- Check database is in "Available" state

### Service Won't Start
- Check logs for errors
- Verify Dockerfile builds locally: `docker build -t test .`
- Check all required files are committed to GitHub

### ETL Not Running
- Check logs for startup errors
- CoinGecko may be rate-limited (expected on free tier)
- CSV and CoinPaprika should work fine

## Cost
- **Free tier**: $0/month
- Perfect for internship demonstration
- Can upgrade later if needed

## Alternative: Railway.app

If Render doesn't work, Railway is another excellent option:
1. Go to https://railway.app
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Add PostgreSQL service from Railway's marketplace
5. Railway auto-detects Dockerfile and deploys

Both are free and excellent for this project!
