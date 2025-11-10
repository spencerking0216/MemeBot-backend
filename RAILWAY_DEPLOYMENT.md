# 🚂 Railway Deployment Guide

Complete guide to deploy your meme bot to Railway (backend + database).

---

## 📋 Prerequisites

- GitHub account
- Railway account (sign up at https://railway.app)
- Your API credentials ready:
  - Claude API key
  - Reddit client ID & secret

---

## 🚀 Step-by-Step Deployment

### Step 1: Push Code to GitHub

```bash
cd backend

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial meme bot backend"

# Create new repo on GitHub at github.com/new
# Then connect and push:
git remote add origin https://github.com/YOUR_USERNAME/meme-bot-backend.git
git branch -M main
git push -u origin main
```

---

### Step 2: Create Railway Project

1. Go to https://railway.app
2. Click **"Login"** (use GitHub login - easiest)
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Authorize Railway to access your GitHub
6. Select your `meme-bot-backend` repository
7. Click **"Deploy Now"**

Railway will start deploying immediately!

---

### Step 3: Add PostgreSQL Database

In your Railway project dashboard:

1. Click **"+ New"** (top right)
2. Select **"Database"**
3. Choose **"PostgreSQL"**
4. Railway will provision the database

**Important:** The `DATABASE_URL` is automatically linked! No manual setup needed.

---

### Step 4: Configure Environment Variables

Click on your **backend service** (not the database):

1. Go to **"Variables"** tab
2. Click **"+ New Variable"** or **"Raw Editor"**
3. Paste these variables:

```bash
CLAUDE_API_KEY=sk-ant-api03-xxxxx
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USER_AGENT=MemeBot/1.0
CONTENT_GENERATOR_MODE=true
GENERATE_INTERVAL_HOURS=4
BOT_ENABLED=true
TREND_SCRAPE_INTERVAL_HOURS=1
ENVIRONMENT=production
PORT=8000
```

Replace with your actual credentials!

**Note:** Don't add `DATABASE_URL` - Railway adds it automatically!

---

### Step 5: Configure Frontend URL (After Vercel Deployment)

Once your Vercel frontend is deployed (see next section), add:

```bash
FRONTEND_URL=https://your-app.vercel.app
```

For now, you can set:
```bash
FRONTEND_URL=http://localhost:3000
```

---

### Step 6: Deploy!

Railway automatically deploys when you:
- ✅ Push to GitHub
- ✅ Change environment variables
- ✅ Click "Deploy"

The deployment will:
1. Install dependencies from `requirements.txt`
2. Auto-initialize database tables (our script handles this!)
3. Start the bot and API server

---

### Step 7: Get Your Backend URL

After deployment completes:

1. Click on your backend service
2. Go to **"Settings"** tab
3. Scroll to **"Networking"**
4. Click **"Generate Domain"**

You'll get a URL like:
```
https://meme-bot-backend-production.up.railway.app
```

This is your backend API URL!

---

### Step 8: Test Your Deployment

Visit these URLs in your browser:

**Health Check:**
```
https://your-app.railway.app/health
```

Should return:
```json
{
  "status": "healthy",
  "timestamp": "2024-..."
}
```

**Review UI:**
```
https://your-app.railway.app/review
```

You should see the content review interface!

**API Status:**
```
https://your-app.railway.app/api/status
```

Should show bot configuration.

---

## 📊 Monitor Your Bot

### View Logs

In Railway dashboard:
1. Click on your backend service
2. Go to **"Logs"** tab
3. See real-time output

You should see:
```
Starting Meme Bot Backend
Checking database...
Database initialized successfully!
Bot scheduler thread started
Starting API server on port 8000...
```

### Check Database

1. Click on your PostgreSQL service
2. Go to **"Data"** tab
3. You can browse tables and data

---

## 🔧 Configuration

### Change Generation Frequency

In Railway Variables, update:
```bash
GENERATE_INTERVAL_HOURS=2  # Generate every 2 hours
```

### Disable Bot Temporarily

```bash
BOT_ENABLED=false  # Stops generation, keeps API running
```

### Enable Auto-Posting (requires Twitter API)

```bash
CONTENT_GENERATOR_MODE=false  # Switch to auto-posting
# Add Twitter API credentials
```

---

## 💰 Railway Pricing

**Starter Plan (Free):**
- $5 credit/month
- Enough for ~150-200 hours runtime
- Good for testing

**Developer Plan ($20/month):**
- Unlimited runtime
- Better for production
- What you'll likely need

**Cost Breakdown:**
- Web Service: ~$8-12/month
- PostgreSQL: ~$5/month
- **Total: ~$13-17/month**

Plus Claude API (~$15-20/month) = **~$30-35/month total**

---

## 🔄 Update Your Bot

To deploy updates:

```bash
# Make changes to your code
git add .
git commit -m "Update bot"
git push

# Railway auto-deploys!
```

---

## 🐛 Troubleshooting

### Deployment Failed

**Check Logs:**
- Go to Deployments tab
- Click on failed deployment
- Read error messages

**Common Issues:**
- Missing environment variables
- Wrong Python version (should be 3.11)
- Database not connected

### Bot Not Generating Content

**Check:**
1. Is `BOT_ENABLED=true`?
2. Are API keys correct?
3. Check logs for errors

**Fix:**
```bash
# In Railway, restart the service
Click service → Settings → Restart
```

### Database Connection Failed

**Check:**
1. Is PostgreSQL service running?
2. Is it in the same Railway project?
3. Railway auto-links them - if not, check "Variables"

**Fix:**
- Delete PostgreSQL service
- Re-add it
- Railway will auto-configure

### Can't Access Review UI

**Check:**
1. Is domain generated? (Settings → Networking)
2. Is port 8000 exposed?
3. Check logs for startup errors

---

## 🌐 Vercel Frontend (Next Step)

Once your backend is deployed, you'll deploy the frontend to Vercel.

The frontend will:
- Display generated tweets
- Show analytics
- Provide better review interface

Backend URL from Railway will be used as `NEXT_PUBLIC_API_URL` in Vercel.

---

## 📝 Environment Variables Reference

Required in Railway:
```bash
CLAUDE_API_KEY          # Your Claude API key
REDDIT_CLIENT_ID        # Reddit app client ID
REDDIT_CLIENT_SECRET    # Reddit app secret
REDDIT_USER_AGENT       # Bot identifier
CONTENT_GENERATOR_MODE  # true (generator) or false (auto-post)
GENERATE_INTERVAL_HOURS # How often to generate (4 recommended)
BOT_ENABLED            # true to run bot
TREND_SCRAPE_INTERVAL_HOURS # How often to scrape (1 recommended)
ENVIRONMENT            # production
PORT                   # 8000
FRONTEND_URL           # Your Vercel URL (add after frontend deployed)
```

Auto-provided by Railway:
```bash
DATABASE_URL           # PostgreSQL connection (automatic)
RAILWAY_ENVIRONMENT    # Railway's environment info
```

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Railway project created
- [ ] PostgreSQL database added
- [ ] Environment variables configured
- [ ] Deployment successful
- [ ] Health check working (`/health`)
- [ ] Review UI accessible (`/review`)
- [ ] Bot generating content (check logs)
- [ ] Database tables created (auto-initialized)

---

## 🎉 Success!

Your bot is now:
- ✅ Running 24/7 on Railway
- ✅ Auto-generating meme content
- ✅ Scraping current trends
- ✅ Accessible via web UI
- ✅ Costing ~$15/month (Railway) + $15-20/month (Claude)

**Next:** Deploy frontend to Vercel to get a better interface!

---

## 🔗 Useful Links

- Railway Dashboard: https://railway.app/dashboard
- Railway Docs: https://docs.railway.app
- Your Backend URL: `https://your-app.railway.app`
- Review UI: `https://your-app.railway.app/review`

---

Happy deploying! 🚀
