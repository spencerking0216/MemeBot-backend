# Quick Start Guide

Get your meme bot up and running in 5 minutes!

## Prerequisites

Before starting, you need:

1. **Twitter Developer Account**
   - Go to https://developer.twitter.com
   - Create a new app
   - Get API keys (API Key, API Secret, Access Token, Access Token Secret, Bearer Token)
   - Enable OAuth 1.0a and OAuth 2.0

2. **Claude API Key** (Recommended) OR **OpenAI API Key**
   - Claude: https://console.anthropic.com
   - OpenAI: https://platform.openai.com

3. **Reddit API Credentials**
   - Go to https://www.reddit.com/prefs/apps
   - Create an app
   - Note the client ID and secret

4. **Railway Account** (for deployment)
   - Sign up at https://railway.app

## Local Setup (5 Steps)

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Note: On Windows, you may need to install Visual C++ Build Tools for some packages.

### Step 2: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```env
# Twitter (REQUIRED)
TWITTER_API_KEY=your_key_here
TWITTER_API_SECRET=your_secret_here
TWITTER_ACCESS_TOKEN=your_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_token_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here

# AI (REQUIRED - choose one)
CLAUDE_API_KEY=your_claude_key_here
# OR
OPENAI_API_KEY=your_openai_key_here

# Reddit (REQUIRED)
REDDIT_CLIENT_ID=your_reddit_id
REDDIT_CLIENT_SECRET=your_reddit_secret

# Database (REQUIRED)
DATABASE_URL=postgresql://user:password@localhost:5432/memebot
```

### Step 3: Set Up Database

If using local PostgreSQL:
```bash
# Create database
createdb memebot

# Initialize tables
python init_db.py
```

If using Railway PostgreSQL (skip this step, Railway creates it automatically)

### Step 4: Test Connections

```bash
python test_connection.py
```

This will verify:
- ✓ Twitter API working
- ✓ Claude/GPT API working
- ✓ Database connected
- ✓ Reddit API working

### Step 5: Run the Bot

```bash
python main.py
```

You should see:
```
Starting Meme Bot Backend
Bot scheduler thread started
Starting API server on port 8000...
```

The bot is now:
- Posting memes every 6 hours
- Scraping trends every hour
- Running API server on http://localhost:8000

## Deploying to Railway (3 Steps)

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo>
git push -u origin main
```

### Step 2: Create Railway Project

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will auto-detect the configuration

### Step 3: Add Database and Environment Variables

1. In Railway project, click "+ New" → "Database" → "PostgreSQL"
2. Go to your service → "Variables"
3. Add all variables from `.env` (except DATABASE_URL, that's auto-set)

```
TWITTER_API_KEY=xxx
TWITTER_API_SECRET=xxx
TWITTER_ACCESS_TOKEN=xxx
TWITTER_ACCESS_TOKEN_SECRET=xxx
TWITTER_BEARER_TOKEN=xxx
CLAUDE_API_KEY=xxx
REDDIT_CLIENT_ID=xxx
REDDIT_CLIENT_SECRET=xxx
BOT_ENABLED=true
FRONTEND_URL=https://your-frontend.vercel.app
ENVIRONMENT=production
PORT=8000
```

4. Click "Deploy"

Done! Your bot is now live on Railway!

## Verify It's Working

### Check Health
```bash
curl https://your-app.railway.app/health
```

Should return:
```json
{
  "status": "healthy",
  "timestamp": "2024-..."
}
```

### Check API
```bash
curl https://your-app.railway.app/api/status
```

### View Recent Tweets
```bash
curl https://your-app.railway.app/api/tweets
```

## Customization

### Change Posting Frequency

In `.env` or Railway variables:
```env
POST_INTERVAL_HOURS=6    # Post every 6 hours
```

### Change Trend Scraping Frequency

```env
TREND_SCRAPE_INTERVAL_HOURS=1    # Scrape every hour
```

### Disable Automated Posting

```env
BOT_ENABLED=false    # Only run API, no auto-posting
```

### Choose LLM Provider

Default is Claude. To use OpenAI instead, edit `bot/content_generator.py`:
```python
# Change this line:
self.llm = LLMService(provider='claude')

# To this:
self.llm = LLMService(provider='openai')
```

## Monitoring

### View Logs (Railway)

1. Go to your Railway project
2. Click on your service
3. Click "Logs" tab
4. Watch real-time logs

### View Analytics

Visit your frontend or use API:
```bash
curl https://your-app.railway.app/api/analytics/summary
```

## Troubleshooting

### "No module named 'config'"
- Make sure you're in the `backend/` directory
- Run `pip install -r requirements.txt`

### "Twitter authentication failed"
- Double-check your Twitter API credentials
- Ensure your app has read/write permissions
- Verify tokens haven't expired

### "Database connection failed"
- Check `DATABASE_URL` format
- Ensure PostgreSQL is running (local)
- Verify Railway database is provisioned (Railway)

### "Bot not posting"
- Check `BOT_ENABLED=true`
- Review logs for errors
- Verify Twitter credentials
- Check Railway deployment status

### "API returns 500 errors"
- Check Railway logs
- Verify all environment variables are set
- Test connections with `python test_connection.py`

## Next Steps

1. **Monitor Performance**: Check `/api/analytics` regularly
2. **Adjust Strategy**: Based on what's working, tune irony levels and topics
3. **Build Frontend**: Connect a Next.js frontend to visualize tweets
4. **Scale Up**: Increase posting frequency as you gain followers
5. **Iterate**: Learn from engagement metrics and improve content

## Support

- Check logs first: `railway logs` or Railway dashboard
- Review README.md for detailed documentation
- Test connections: `python test_connection.py`
- Open an issue on GitHub if stuck

## Pro Tips

1. **Start Conservative**: Begin with 2-3 posts per day, increase as you grow
2. **Monitor Trends**: Check `/api/trends/trending` to see what the bot is learning
3. **Quality Over Quantity**: Let the bot's self-evaluation filter low-quality posts
4. **Engage**: Manually engage with replies to build community
5. **Iterate**: Use analytics to refine what works

---

Happy memeing! 🔥
