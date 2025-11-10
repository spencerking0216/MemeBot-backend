import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Twitter API
    TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
    TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
    TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

    # LLM API Keys
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    # Reddit API
    REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
    REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
    REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'MemeBot/1.0')

    # Database
    DATABASE_URL = os.getenv('DATABASE_URL')

    # Frontend
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

    # Bot Configuration
    POST_INTERVAL_HOURS = int(os.getenv('POST_INTERVAL_HOURS', 6))
    TREND_SCRAPE_INTERVAL_HOURS = int(os.getenv('TREND_SCRAPE_INTERVAL_HOURS', 1))
    BOT_ENABLED = os.getenv('BOT_ENABLED', 'true').lower() == 'true'

    # Content Generator Mode (no auto-posting, just generate and queue for review)
    CONTENT_GENERATOR_MODE = os.getenv('CONTENT_GENERATOR_MODE', 'true').lower() == 'true'
    GENERATE_INTERVAL_HOURS = int(os.getenv('GENERATE_INTERVAL_HOURS', 4))  # How often to generate content

    # Server
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    PORT = int(os.getenv('PORT', 8000))

    # Meme Generation Settings
    MAX_MEME_LENGTH = 280  # Twitter character limit
    MIN_ENGAGEMENT_THRESHOLD = 10  # Minimum likes to consider a meme successful

    # Subreddits to monitor
    MEME_SUBREDDITS = [
        'memes',
        'dankmemes',
        'MemeEconomy',
        'okbuddyretard',
        'me_irl',
        'DeepFriedMemes',
        'surrealmemes',
        'antimeme'
    ]

    # Irony levels for meme classification
    IRONY_LEVELS = ['literal', 'ironic', 'post-ironic', 'meta-ironic', 'absurdist']
