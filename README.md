# Meme Bot Backend

A sophisticated Twitter meme bot powered by AI that understands post-irony, meme culture, and creates engaging content based on trending topics. Includes multimodal analysis (images, videos, audio) and comprehensive trend monitoring.

## Features

### Core Functionality
- **AI-Powered Content Generation**: Uses Claude (Anthropic) or GPT-4 to generate culturally-aware meme content
- **Post-Ironic Understanding**: Deep understanding of modern meme culture, meta-humor, and absurdism
- **Automated Posting**: Scheduled tweet posting with configurable intervals
- **Trend Monitoring**: Real-time scraping of Reddit, Know Your Meme, and Twitter trends
- **Multimodal Analysis**: Analyzes images, videos, and audio to understand meme formats

### Advanced Features
- **Learning System**: Continuously learns from top-performing memes
- **Quality Control**: Self-evaluation before posting to ensure quality
- **Engagement Tracking**: Monitors likes, retweets, and replies
- **Analytics Dashboard**: Comprehensive performance metrics
- **REST API**: Full API for frontend integration

## Tech Stack

- **Language**: Python 3.11
- **Framework**: Flask (REST API)
- **Database**: PostgreSQL (via SQLAlchemy)
- **AI**: Anthropic Claude & OpenAI GPT-4
- **Scheduling**: APScheduler
- **Twitter API**: Tweepy
- **Image Analysis**: Claude Vision, GPT-4V
- **Video Processing**: OpenCV
- **Audio Processing**: OpenAI Whisper
- **Deployment**: Railway

## Architecture

```
backend/
├── api/
│   └── server.py              # Flask REST API
├── bot/
│   ├── twitter_client.py      # Twitter API integration
│   ├── content_generator.py   # Content generation orchestrator
│   └── scheduler.py           # Bot scheduler
├── services/
│   ├── llm_service.py         # LLM integration (Claude/GPT)
│   ├── meme_scraper.py        # Trend scraping
│   └── multimodal_analyzer.py # Image/video/audio analysis
├── database/
│   └── models.py              # SQLAlchemy models
├── config.py                  # Configuration
├── main.py                    # Application entry point
└── requirements.txt
```

## Setup

### Prerequisites
- Python 3.11+
- PostgreSQL database
- Twitter Developer Account with API access
- Claude API key OR OpenAI API key
- Reddit API credentials

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd backend
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required environment variables:
- `TWITTER_API_KEY` - Twitter API key
- `TWITTER_API_SECRET` - Twitter API secret
- `TWITTER_ACCESS_TOKEN` - Twitter access token
- `TWITTER_ACCESS_TOKEN_SECRET` - Twitter access token secret
- `TWITTER_BEARER_TOKEN` - Twitter bearer token
- `CLAUDE_API_KEY` - Anthropic Claude API key (or use OpenAI)
- `OPENAI_API_KEY` - OpenAI API key (optional if using Claude)
- `REDDIT_CLIENT_ID` - Reddit API client ID
- `REDDIT_CLIENT_SECRET` - Reddit API secret
- `DATABASE_URL` - PostgreSQL connection string
- `FRONTEND_URL` - Your frontend URL for CORS

4. **Initialize the database**
```bash
python -c "from database.models import init_db; init_db()"
```

5. **Run the application**
```bash
python main.py
```

## Deployment on Railway

### Step 1: Create Railway Project

1. Go to [Railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your backend repository

### Step 2: Add PostgreSQL Database

1. In your Railway project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically provision a database
4. The `DATABASE_URL` will be automatically set

### Step 3: Configure Environment Variables

In Railway project settings, add all environment variables from `.env.example`:

```
TWITTER_API_KEY=xxx
TWITTER_API_SECRET=xxx
TWITTER_ACCESS_TOKEN=xxx
TWITTER_ACCESS_TOKEN_SECRET=xxx
TWITTER_BEARER_TOKEN=xxx
CLAUDE_API_KEY=xxx
REDDIT_CLIENT_ID=xxx
REDDIT_CLIENT_SECRET=xxx
FRONTEND_URL=https://your-frontend.vercel.app
BOT_ENABLED=true
POST_INTERVAL_HOURS=6
TREND_SCRAPE_INTERVAL_HOURS=1
ENVIRONMENT=production
PORT=8000
```

### Step 4: Deploy

1. Railway will automatically detect the `railway.json` and `nixpacks.toml`
2. Click "Deploy"
3. Your bot will start running automatically!

### Step 5: Monitor

- Check logs in Railway dashboard
- Visit `https://your-app.railway.app/health` to verify it's running
- Monitor the API at `https://your-app.railway.app/api/status`

## API Endpoints

### Tweets
- `GET /api/tweets` - Get recent tweets
- `GET /api/tweets/:tweet_id` - Get specific tweet
- `GET /api/tweets/top` - Get top performing tweets

### Trends
- `GET /api/trends` - Get all meme trends
- `GET /api/trends/trending` - Get currently trending memes

### Analytics
- `GET /api/analytics` - Get bot analytics
- `GET /api/analytics/summary` - Get analytics summary

### Media
- `GET /api/media` - Get analyzed media (images/videos/audio)

### Status
- `GET /api/status` - Get bot status
- `GET /health` - Health check

## Configuration

### Bot Behavior

Edit `config.py` or set environment variables:

- `POST_INTERVAL_HOURS` - How often to post (default: 6 hours)
- `TREND_SCRAPE_INTERVAL_HOURS` - How often to scrape trends (default: 1 hour)
- `BOT_ENABLED` - Enable/disable automated posting
- `MEME_SUBREDDITS` - List of subreddits to monitor

### Irony Levels

The bot supports multiple irony levels:
- `literal` - Straightforward humor
- `ironic` - Traditional ironic humor
- `post-ironic` - Blend of sincerity and irony (default)
- `meta-ironic` - Self-aware meta humor
- `absurdist` - Random, nonsensical humor

## How It Works

### 1. Trend Monitoring
The bot continuously scrapes:
- Reddit (r/memes, r/dankmemes, etc.)
- Know Your Meme
- Twitter trending topics

### 2. Multimodal Analysis
When trends include media:
- **Images**: Analyzed with Claude Vision or GPT-4V to understand format, text, and humor
- **Videos**: Key frames extracted and analyzed
- **Audio**: Transcribed and analyzed for meme potential

### 3. Content Generation
1. Select trending topic or relatable situation
2. Analyze related successful memes
3. Generate content using LLM with cultural awareness
4. Self-evaluate quality
5. Post if quality threshold met

### 4. Learning Loop
- Track engagement on posted tweets
- Identify successful patterns
- Adjust content strategy
- Continuous improvement

## Development

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set up .env file
cp .env.example .env
# Edit .env with your credentials

# Initialize database
python -c "from database.models import init_db; init_db()"

# Run the application
python main.py
```

### Testing Individual Components

```python
# Test Twitter client
from bot.twitter_client import TwitterClient
client = TwitterClient()
client.post_tweet("Test tweet")

# Test content generation
from bot.content_generator import ContentGenerator
gen = ContentGenerator()
meme = gen.generate_meme_tweet()
print(meme)

# Test trend scraping
from services.meme_scraper import MemeScraper
scraper = MemeScraper()
trends = scraper.scrape_reddit_memes(limit=10)

# Test multimodal analysis
from services.multimodal_analyzer import MultimodalAnalyzer
analyzer = MultimodalAnalyzer()
result = analyzer.analyze_image("https://example.com/meme.jpg")
```

## Troubleshooting

### Bot not posting
- Check `BOT_ENABLED` is set to `true`
- Verify Twitter API credentials
- Check logs for errors

### Database connection errors
- Verify `DATABASE_URL` is correct
- Ensure PostgreSQL is running
- Check Railway database is provisioned

### API errors
- Check Claude/OpenAI API keys
- Verify API rate limits
- Review logs for specific errors

### No trends being scraped
- Verify Reddit API credentials
- Check internet connectivity
- Review scraper logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
4. Submit a pull request

## License

MIT License - feel free to use and modify

## Support

For issues and questions:
- Check the logs first
- Review Railway documentation
- Open an issue on GitHub

---

Built with Python, Claude AI, and a deep understanding of internet culture.
