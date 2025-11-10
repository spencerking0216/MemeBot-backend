from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import Config

Base = declarative_base()

class Tweet(Base):
    """Stores all tweets posted by the bot"""
    __tablename__ = 'tweets'

    id = Column(Integer, primary_key=True)
    tweet_id = Column(String(50), unique=True, nullable=False)  # Twitter's tweet ID
    content = Column(Text, nullable=False)
    image_url = Column(String(500))
    posted_at = Column(DateTime, default=datetime.utcnow)

    # Engagement metrics
    likes = Column(Integer, default=0)
    retweets = Column(Integer, default=0)
    replies = Column(Integer, default=0)
    impressions = Column(Integer, default=0)

    # Meme classification
    meme_format = Column(String(100))  # e.g., "drake", "distracted boyfriend"
    irony_level = Column(String(50))   # literal, ironic, post-ironic, meta-ironic
    topics = Column(JSON)              # ["gaming", "politics", etc.]

    # Metadata
    trend_context = Column(Text)       # What trend/topic this was responding to
    generation_prompt = Column(Text)   # The prompt used to generate this

    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MemeTrend(Base):
    """Tracks current meme trends and formats"""
    __tablename__ = 'meme_trends'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True, nullable=False)
    description = Column(Text)

    # Trend metrics
    popularity_score = Column(Float, default=0.0)  # 0-100 scale
    velocity = Column(Float, default=0.0)          # Rate of growth/decline
    lifecycle_stage = Column(String(50))           # new, rising, peak, declining, dead

    # Sources
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    source_platform = Column(String(50))           # twitter, reddit, tiktok

    # Context
    related_topics = Column(JSON)
    example_urls = Column(JSON)
    keywords = Column(JSON)

    # Usage tracking
    times_used = Column(Integer, default=0)
    avg_engagement = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MemeTemplate(Base):
    """Stores meme templates/formats"""
    __tablename__ = 'meme_templates'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True, nullable=False)
    description = Column(Text)

    # Template structure
    format_type = Column(String(100))  # image_macro, text_only, reaction, etc.
    text_positions = Column(JSON)      # Where text goes on the image
    example_template = Column(Text)    # Example of how to use this template

    # Classification
    irony_compatibility = Column(JSON)  # Which irony levels work with this
    topics = Column(JSON)               # What topics this works for

    # Performance
    success_rate = Column(Float, default=0.0)
    times_used = Column(Integer, default=0)
    avg_engagement = Column(Float, default=0.0)

    # Status
    is_active = Column(Boolean, default=True)
    is_overused = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MemeMedia(Base):
    """Stores analyzed media content (images, videos, audio)"""
    __tablename__ = 'meme_media'

    id = Column(Integer, primary_key=True)
    media_url = Column(String(500), unique=True, nullable=False)
    media_type = Column(String(50))  # image, video, audio

    # Analysis results
    visual_description = Column(Text)
    meme_format = Column(String(100))
    text_content = Column(JSON)  # Array of text extracted from media
    humor_type = Column(String(100))
    irony_level = Column(String(50))
    cultural_references = Column(JSON)
    emotional_tone = Column(String(100))
    topics = Column(JSON)

    # Scores
    meme_potential_score = Column(Float, default=0.0)

    # Metadata
    analysis_data = Column(JSON)  # Full analysis results
    source_url = Column(String(500))  # Original source (Reddit, Twitter, etc.)
    analyzed_at = Column(DateTime, default=datetime.utcnow)

    # Usage tracking
    used_for_inspiration = Column(Boolean, default=False)
    times_referenced = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)


class TwitterTrend(Base):
    """Tracks trending topics on Twitter"""
    __tablename__ = 'twitter_trends'

    id = Column(Integer, primary_key=True)
    trend_name = Column(String(200), nullable=False)
    tweet_volume = Column(Integer)

    # Metadata
    category = Column(String(100))  # politics, entertainment, sports, etc.
    location = Column(String(100), default='United States')

    # Tracking
    first_detected = Column(DateTime, default=datetime.utcnow)
    last_checked = Column(DateTime, default=datetime.utcnow)
    is_current = Column(Boolean, default=True)

    # Meme potential
    meme_worthy = Column(Boolean, default=False)
    meme_potential_score = Column(Float, default=0.0)
    used_by_bot = Column(Boolean, default=False)


class ContentQueue(Base):
    """Stores generated content pending review/approval"""
    __tablename__ = 'content_queue'

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)

    # Generation metadata
    meme_format = Column(String(100))
    irony_level = Column(String(50))
    topics = Column(JSON)
    trend_context = Column(Text)

    # Quality scoring
    quality_score = Column(Float, default=0.0)
    humor_score = Column(Float, default=0.0)
    authenticity_score = Column(Float, default=0.0)
    engagement_score = Column(Float, default=0.0)

    # Evaluation data
    evaluation_data = Column(JSON)  # Full LLM evaluation
    generation_prompt = Column(Text)

    # Status
    status = Column(String(20), default='pending')  # pending, approved, rejected, posted
    reviewed_at = Column(DateTime)
    posted_at = Column(DateTime)
    posted_tweet_id = Column(String(50))  # If manually posted, you can add the tweet ID

    # Notes
    reviewer_notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BotAnalytics(Base):
    """Stores overall bot performance analytics"""
    __tablename__ = 'bot_analytics'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow)

    # Daily metrics
    tweets_posted = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    total_retweets = Column(Integer, default=0)
    total_replies = Column(Integer, default=0)
    total_impressions = Column(Integer, default=0)

    # Follower growth
    follower_count = Column(Integer, default=0)
    followers_gained = Column(Integer, default=0)
    followers_lost = Column(Integer, default=0)

    # Performance
    avg_engagement_rate = Column(Float, default=0.0)
    best_performing_tweet_id = Column(String(50))
    best_performing_format = Column(String(100))
    best_performing_irony_level = Column(String(50))

    # Trend analysis
    trends_monitored = Column(Integer, default=0)
    trends_used = Column(Integer, default=0)


# Database initialization
def init_db():
    """Initialize database with all tables"""
    engine = create_engine(Config.DATABASE_URL)
    Base.metadata.create_all(engine)
    return engine

def get_session():
    """Get database session"""
    engine = create_engine(Config.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return Session()
