# Content Generator Mode Guide

## 🎯 What is Content Generator Mode?

Content Generator Mode lets you use the bot **without paying for Twitter API** ($100/month savings!). The bot generates high-quality meme content using AI, saves it to a review queue, and you manually post the ones you like.

**Cost: ~$25-30/month** (AI + hosting only, no Twitter API fees)

---

## 🚀 Quick Start

### 1. Set Environment Variables

In your `.env` file:

```bash
# REQUIRED
CLAUDE_API_KEY=your_claude_key  # or OPENAI_API_KEY
REDDIT_CLIENT_ID=your_reddit_id
REDDIT_CLIENT_SECRET=your_reddit_secret
DATABASE_URL=your_postgres_url

# Enable Content Generator Mode
CONTENT_GENERATOR_MODE=true
GENERATE_INTERVAL_HOURS=4  # Generate new content every 4 hours
BOT_ENABLED=true

# Optional: Twitter API (not required in generator mode)
# TWITTER_API_KEY=...
```

### 2. Run the Bot

```bash
python main.py
```

The bot will:
- ✅ Generate meme content every 4 hours
- ✅ Scrape current trends hourly
- ✅ Analyze trending memes
- ✅ Save generated content to review queue
- ✅ Run API server on `http://localhost:8000`

### 3. Review Content

Open in your browser:
```
http://localhost:8000/review
```

You'll see a UI showing:
- Generated meme text
- Quality scores (humor, authenticity, engagement)
- Trend context
- Meme format and irony level
- Topics/tags

### 4. Approve or Reject

**Keyboard Shortcuts:**
- `→ Right Arrow` = Approve
- `← Left Arrow` = Reject
- `↓ Down Arrow` = Skip

**Actions:**
- **Approve** = Mark as good content (you can post it)
- **Reject** = Mark as bad (learn from what doesn't work)
- **Skip** = Review later

### 5. Post Manually

Copy approved content and post to Twitter manually via:
- Twitter web app
- Twitter mobile app
- TweetDeck
- Any Twitter client

---

## 🎨 How It Works

### Content Generation Flow

```
1. Bot scrapes trending memes
   ↓
2. Gathers current meme context
   - Know Your Meme trending
   - Reddit hot memes
   - Google Trends
   - Urban Dictionary slang
   ↓
3. AI generates meme using context
   ↓
4. Self-evaluates quality
   ↓
5. Saves to review queue
   ↓
6. You review and approve
   ↓
7. You manually post to Twitter
```

### What Makes the Content Good?

The bot uses:

1. **Current Meme Context**
   - Real-time scraping of Know Your Meme
   - Reddit trending memes (r/memes, r/dankmemes, etc.)
   - Google Trends for current events
   - Urban Dictionary for latest slang

2. **AI Understanding**
   - Post-ironic humor
   - Meta-awareness
   - Cultural references
   - Generational humor (Gen Z)

3. **Quality Evaluation**
   - Humor score (is it funny?)
   - Authenticity score (does it feel native to internet culture?)
   - Engagement score (will people interact?)
   - Overall quality score

---

## 📊 Review UI Features

### Stats Dashboard
- **Pending**: Content waiting for review
- **Approved**: Content you liked
- **Rejected**: Content you didn't like

### Content Card Shows:
- **Text**: The generated meme tweet
- **Format**: Meme template used (if any)
- **Irony Level**: Type of humor
- **Topics**: What it's about
- **Scores**: Quality metrics (0-10 scale)
- **Trend Context**: What trend it's based on
- **Created Date**: When it was generated

### Score Bars:
- **Humor**: How funny it is
- **Authenticity**: How natural it feels
- **Engagement**: Predicted interaction level

---

## 🔧 Configuration

### Generation Frequency

```bash
# Generate content every 4 hours (6 memes per day)
GENERATE_INTERVAL_HOURS=4

# Or more frequently:
GENERATE_INTERVAL_HOURS=2  # 12 memes per day
GENERATE_INTERVAL_HOURS=6  # 4 memes per day
```

### Trend Scraping

```bash
# Scrape trends every hour (more current context)
TREND_SCRAPE_INTERVAL_HOURS=1

# Or less frequently:
TREND_SCRAPE_INTERVAL_HOURS=2  # Every 2 hours
```

### Bot Control

```bash
# Enable/disable bot
BOT_ENABLED=true  # Bot runs
BOT_ENABLED=false  # Bot stopped (API still runs)

# Generator mode (avoid Twitter API costs)
CONTENT_GENERATOR_MODE=true  # Save to queue
CONTENT_GENERATOR_MODE=false  # Auto-post to Twitter
```

---

## 🌐 API Endpoints

### Get Pending Content
```bash
GET /api/queue?status=pending&limit=20
```

### Get Specific Item
```bash
GET /api/queue/123
```

### Approve Content
```bash
POST /api/queue/123/approve
```

### Reject Content
```bash
POST /api/queue/123/reject
```

### Mark as Posted
```bash
POST /api/queue/123/mark-posted
Body: { "tweet_id": "1234567890" }
```

---

## 💡 Pro Tips

### 1. Build a Posting Routine
- Review queue 2-3 times per day
- Post approved content during peak hours
- Track which types perform best

### 2. Learn from Rejections
- The bot learns from patterns
- Rejected content helps refine future generation
- Over time, quality improves

### 3. Mix Manual and Generated
- Use generated content as inspiration
- Modify tweets before posting
- Add your own voice

### 4. Monitor Trends
- Check `/api/trends/trending` to see what bot is learning
- Adjust subreddits in config if needed
- Focus on niches you want to target

### 5. Quality Over Quantity
- Don't post everything generated
- Only post 7/10+ quality scores
- Build reputation with consistent quality

---

## 🎯 Best Practices

### Approval Criteria

**APPROVE if:**
- ✅ Makes you laugh
- ✅ Feels authentic to internet culture
- ✅ References current trends
- ✅ Quality score > 7
- ✅ You'd post it yourself

**REJECT if:**
- ❌ Forced or trying too hard
- ❌ Offensive or problematic
- ❌ Out of touch or dated
- ❌ Quality score < 5
- ❌ Doesn't make sense

### Posting Strategy

1. **Start Conservative**: Post 2-3 times per day
2. **Peak Hours**: Post when your audience is active
3. **Consistency**: Regular posting > sporadic bursts
4. **Engagement**: Reply to comments on your posts
5. **Track Performance**: Note which types of memes work

---

## 📈 Scaling Up

### Phase 1: Testing (Month 1)
- Generate 4-6 memes per day
- Post 2-3 manually
- Learn what works
- **Cost: ~$25/month**

### Phase 2: Growth (Month 2-3)
- Generate 8-12 memes per day
- Post 4-5 manually
- Build audience
- **Cost: ~$30/month**

### Phase 3: Automation (Month 4+)
- Once profitable or validated
- Upgrade to Twitter API ($100/month)
- Enable auto-posting
- **Cost: ~$130/month**

---

## 🔍 Monitoring

### Check Bot Status
```bash
curl http://localhost:8000/api/status
```

### View Logs
```bash
# If running locally
tail -f logs/bot.log

# If on Railway
railway logs
```

### Database Stats
```bash
# Pending count
curl http://localhost:8000/api/queue?status=pending

# Approved count
curl http://localhost:8000/api/queue?status=approved
```

---

## 🐛 Troubleshooting

### No Content Being Generated

**Check:**
1. Is `BOT_ENABLED=true`?
2. Is `CONTENT_GENERATOR_MODE=true`?
3. Are API keys valid (Claude/OpenAI)?
4. Check logs for errors

**Fix:**
```bash
# Restart bot
python main.py

# Check status
curl http://localhost:8000/api/status
```

### Low Quality Content

**Possible Causes:**
- Not enough current meme context
- Trend scraping failing
- Need to adjust prompts

**Fix:**
1. Check `/api/trends` - are trends being scraped?
2. Verify Reddit API credentials
3. Adjust `GENERATE_INTERVAL_HOURS` to get fresh context

### Review UI Not Loading

**Check:**
1. Is API server running on port 8000?
2. Try http://localhost:8000/health
3. Check browser console for errors

**Fix:**
```bash
# Ensure Flask is running
python api/server.py
```

---

## 🎨 Customization

### Adjust Irony Levels

Edit `bot/scheduler.py`:
```python
# Line ~186
meme = self.content_gen.generate_meme_tweet(
    use_trend=True,
    irony_level='post-ironic'  # Change to: literal, ironic, meta-ironic, absurdist
)
```

### Add More Subreddits

Edit `config.py`:
```python
MEME_SUBREDDITS = [
    'memes',
    'dankmemes',
    'MemeEconomy',
    'okbuddyretard',
    'me_irl',
    'DeepFriedMemes',
    'surrealmemes',
    'antimeme',
    'ProgrammerHumor',  # Add your own!
    'gaming',
    'PrequelMemes'
]
```

### Change Generation Prompts

Edit `services/llm_service.py` to customize how the AI generates memes.

---

## 💰 Cost Breakdown (Content Generator Mode)

### Monthly Costs
- **Claude API**: $15-20
  - ~180 meme generations per month
  - ~100 trend analyses
  - ~50 quality evaluations
- **Railway Hosting**: $10-15
  - Web service + PostgreSQL
- **Reddit API**: FREE
- **Google Trends**: FREE
- **Know Your Meme**: FREE (web scraping)

**Total: ~$25-35/month**

### Cost Savings
- **Without Twitter API**: $25/month
- **With Twitter API**: $130/month
- **Savings**: **$105/month** (81% reduction!)

---

## 🚀 Next Steps

Once you've validated the bot generates good content:

1. **Keep using generator mode** and posting manually (cheapest)
2. **Switch to Bluesky** (free API, auto-posting) - see Bluesky guide
3. **Upgrade to Twitter API** ($100/month for auto-posting)

---

## ❓ FAQ

**Q: Can I use this without Twitter at all?**
A: Yes! Post to Bluesky, Mastodon, or Reddit instead (all have free APIs).

**Q: How many memes should I generate per day?**
A: Start with 4-6. You won't post all of them, but it gives options.

**Q: Can I edit generated content before posting?**
A: Absolutely! Treat it as a starting point and add your own voice.

**Q: Will the quality improve over time?**
A: Yes! The bot learns from successful memes and trending content.

**Q: Can I run this 24/7 on Railway?**
A: Yes! It's designed for continuous operation.

**Q: What if I want to stop generating content temporarily?**
A: Set `BOT_ENABLED=false` in Railway. API still runs for reviewing old content.

---

## 📞 Support

- Check logs first
- Review `/api/status` endpoint
- Verify environment variables
- Test connections with `python test_connection.py`

---

**Ready to start?** Run `python main.py` and visit `http://localhost:8000/review`!
