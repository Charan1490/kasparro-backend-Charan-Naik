# Crypto ETL Backend - Deployment Ready! 🚀

## Quick Deploy to Render.com (5 minutes)

### Step 1: Push to GitHub

```bash
# In your terminal, run these commands:
cd /Users/charannaik/Documents/codes/BackendAssign

# Initialize git
git init
git add .
git commit -m "Production-ready crypto ETL backend with 100% test coverage"

# Create a new repository on GitHub.com, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Render

1. **Go to**: https://render.com
2. **Sign Up**: Use your GitHub account
3. **Create PostgreSQL Database**:
   - Click "New +" → "PostgreSQL"
   - Name: `crypto-postgres`
   - Region: Choose closest region
   - Plan: **Free**
   - Click "Create Database"
   - **COPY the "Internal Database URL"** (you'll need this!)

4. **Create Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Name: `crypto-etl-backend`
   - Region: Same as database
   - Branch: `main`
   - Runtime: **Docker**
   - Plan: **Free**
   
5. **Add Environment Variables**:
   - Click "Advanced"
   - Add variable:
     ```
     Key: DATABASE_URL
     Value: [Paste the Internal Database URL from step 3]
     ```
   - Add variable:
     ```
     Key: ENVIRONMENT
     Value: production
     ```

6. **Create Web Service** - Wait 5-10 minutes for deployment

### Step 3: Get Your Live URL

After deployment completes, you'll get a URL like:
```
https://crypto-etl-backend-xxxx.onrender.com
```

### Step 4: Test Your Deployment

```bash
# Replace YOUR-URL with your actual Render URL

# Health check
curl https://YOUR-URL.onrender.com/health

# View data
curl https://YOUR-URL.onrender.com/data?limit=5

# View stats
curl https://YOUR-URL.onrender.com/stats

# Interactive API docs
# Open in browser: https://YOUR-URL.onrender.com/docs
```

## What You Get

✅ **Live API** accessible from anywhere
✅ **PostgreSQL Database** (managed, backed up)
✅ **Auto-deployed** from GitHub (push to update)
✅ **Free tier** - perfect for internship demo
✅ **HTTPS** enabled by default
✅ **Interactive Swagger docs** at `/docs`

## Free Tier Notes

- **Web Service**: Spins down after 15 min inactivity (first request ~30s wake-up)
- **Database**: Free for 90 days
- **Perfect** for project demonstrations and internships!

## Alternative: Railway.app

If you prefer Railway:

1. Go to https://railway.app
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add PostgreSQL from Railway marketplace
6. Railway auto-connects everything!

## For Your Submission

**Include in your internship submission:**

```
Live API URL: https://your-app.onrender.com
API Documentation: https://your-app.onrender.com/docs
GitHub Repository: https://github.com/yourusername/yourrepo

Key Endpoints:
- GET /health - System health and status
- GET /data - Cryptocurrency data (paginated)
- GET /stats - ETL statistics and metrics
- GET /docs - Interactive API documentation
```

## Need Help?

Check `RENDER_DEPLOYMENT.md` for detailed troubleshooting guide.
