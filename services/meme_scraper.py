import praw
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from config import Config
from database.models import MemeTrend, TwitterTrend, get_session
from services.llm_service import LLMService
from services.enhanced_scraper import EnhancedMemeScraper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemeScraper:
    """Scrapes meme trends from various sources"""

    def __init__(self):
        self.reddit = self._init_reddit()
        self.llm = LLMService(provider='claude')
        self.enhanced_scraper = EnhancedMemeScraper()

    def _init_reddit(self):
        """Initialize Reddit API client"""
        try:
            reddit = praw.Reddit(
                client_id=Config.REDDIT_CLIENT_ID,
                client_secret=Config.REDDIT_CLIENT_SECRET,
                user_agent=Config.REDDIT_USER_AGENT
            )
            logger.info("Reddit API initialized successfully")
            return reddit
        except Exception as e:
            logger.error(f"Failed to initialize Reddit API: {e}")
            return None

    def scrape_reddit_memes(self, limit=50):
        """
        Scrape trending memes from Reddit including images, videos, and text

        Args:
            limit: Number of posts to fetch per subreddit

        Returns:
            List of meme trends
        """
        if not self.reddit:
            logger.warning("Reddit client not initialized")
            return []

        all_trends = []

        for subreddit_name in Config.MEME_SUBREDDITS:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)

                # Get hot posts
                for submission in subreddit.hot(limit=limit):
                    # Skip if too old (older than 24 hours)
                    post_age = datetime.utcnow() - datetime.fromtimestamp(submission.created_utc)
                    if post_age > timedelta(days=1):
                        continue

                    # Calculate popularity score based on upvotes and comments
                    popularity_score = self._calculate_popularity_score(
                        submission.score,
                        submission.num_comments
                    )

                    # Determine media type
                    media_type = self._detect_media_type(submission)
                    media_url = self._extract_media_url(submission)

                    trend_data = {
                        'name': submission.title[:200],
                        'description': submission.selftext[:500] if submission.selftext else '',
                        'popularity_score': popularity_score,
                        'source_platform': f'reddit/{subreddit_name}',
                        'url': f"https://reddit.com{submission.permalink}",
                        'media_type': media_type,
                        'media_url': media_url,
                        'upvotes': submission.score,
                        'comments': submission.num_comments
                    }

                    all_trends.append(trend_data)

                logger.info(f"Scraped {len(all_trends)} posts from r/{subreddit_name}")

            except Exception as e:
                logger.error(f"Error scraping r/{subreddit_name}: {e}")
                continue

        return all_trends

    def _detect_media_type(self, submission):
        """Detect the type of media in a Reddit submission"""
        if hasattr(submission, 'is_video') and submission.is_video:
            return 'video'
        elif hasattr(submission, 'post_hint'):
            if submission.post_hint == 'image':
                return 'image'
            elif submission.post_hint == 'hosted:video':
                return 'video'
            elif submission.post_hint == 'rich:video':
                return 'video'
        elif submission.url:
            url_lower = submission.url.lower()
            if any(ext in url_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                return 'image'
            elif any(ext in url_lower for ext in ['.mp4', '.webm', '.mov']):
                return 'video'
            elif 'v.redd.it' in url_lower:
                return 'video'
        return 'text'

    def _extract_media_url(self, submission):
        """Extract media URL from submission"""
        if hasattr(submission, 'is_video') and submission.is_video:
            return submission.media.get('reddit_video', {}).get('fallback_url', '')
        elif submission.url:
            return submission.url
        return None

    def _calculate_popularity_score(self, upvotes, comments, max_score=100):
        """
        Calculate popularity score based on engagement

        Args:
            upvotes: Number of upvotes
            comments: Number of comments
            max_score: Maximum score (default 100)

        Returns:
            Popularity score (0-100)
        """
        # Weight upvotes and comments
        engagement = (upvotes * 0.7) + (comments * 10 * 0.3)

        # Normalize to 0-100 scale (assuming 10k engagement = 100 score)
        score = min((engagement / 10000) * max_score, max_score)

        return round(score, 2)

    def analyze_and_store_trends(self, trends):
        """
        Analyze trends with LLM and store in database

        Args:
            trends: List of trend data dictionaries
        """
        session = get_session()

        for trend_data in trends:
            try:
                # Check if trend already exists
                existing = session.query(MemeTrend).filter_by(
                    name=trend_data['name']
                ).first()

                if existing:
                    # Update existing trend
                    existing.popularity_score = trend_data['popularity_score']
                    existing.last_seen = datetime.utcnow()

                    # Update velocity (rate of change in popularity)
                    if existing.popularity_score > 0:
                        velocity = (
                            (trend_data['popularity_score'] - existing.popularity_score) /
                            existing.popularity_score * 100
                        )
                        existing.velocity = round(velocity, 2)

                    # Update lifecycle stage
                    existing.lifecycle_stage = self._determine_lifecycle_stage(
                        existing.popularity_score,
                        existing.velocity
                    )

                else:
                    # Create new trend
                    new_trend = MemeTrend(
                        name=trend_data['name'],
                        description=trend_data.get('description', ''),
                        popularity_score=trend_data['popularity_score'],
                        velocity=0.0,
                        lifecycle_stage='new',
                        source_platform=trend_data['source_platform'],
                        first_seen=datetime.utcnow(),
                        last_seen=datetime.utcnow(),
                        example_urls=[trend_data.get('url', '')],
                        keywords=[],
                        related_topics=[]
                    )

                    session.add(new_trend)

                session.commit()
                logger.info(f"Stored/updated trend: {trend_data['name'][:50]}...")

            except Exception as e:
                logger.error(f"Error processing trend: {e}")
                session.rollback()
                continue

        session.close()

    def _determine_lifecycle_stage(self, popularity_score, velocity):
        """
        Determine lifecycle stage of a meme trend

        Args:
            popularity_score: Current popularity (0-100)
            velocity: Rate of change

        Returns:
            Lifecycle stage string
        """
        if popularity_score < 20:
            if velocity > 50:
                return 'rising'
            else:
                return 'new'
        elif popularity_score < 60:
            if velocity > 20:
                return 'rising'
            elif velocity < -20:
                return 'declining'
            else:
                return 'stable'
        else:  # popularity_score >= 60
            if velocity < -10:
                return 'declining'
            else:
                return 'peak'

    def get_top_trends(self, limit=10, min_score=30):
        """
        Get top meme trends from database

        Args:
            limit: Maximum number of trends to return
            min_score: Minimum popularity score

        Returns:
            List of MemeTrend objects
        """
        session = get_session()

        trends = session.query(MemeTrend).filter(
            MemeTrend.popularity_score >= min_score,
            MemeTrend.lifecycle_stage.in_(['rising', 'peak', 'stable'])
        ).order_by(
            MemeTrend.popularity_score.desc()
        ).limit(limit).all()

        session.close()

        return trends

    def run_full_scrape(self):
        """
        Run a full scraping cycle from all sources

        Returns:
            Number of trends processed
        """
        logger.info("Starting full meme scrape cycle...")

        all_trends = []

        # Scrape Reddit
        reddit_trends = self.scrape_reddit_memes(limit=50)
        all_trends.extend(reddit_trends)

        # Scrape Know Your Meme (enhanced)
        kym_trends = self.enhanced_scraper.scrape_know_your_meme_trending()
        for kym in kym_trends:
            all_trends.append({
                'name': kym['name'],
                'description': kym['description'],
                'popularity_score': kym['popularity_score'],
                'source_platform': 'knowyourmeme',
                'url': kym['url'],
                'media_type': 'text',
                'media_url': None
            })

        # Scrape Google Trends
        google_trends = self.enhanced_scraper.scrape_google_trends()
        for gt in google_trends:
            all_trends.append({
                'name': gt['topic'],
                'description': gt.get('news_context', ''),
                'popularity_score': gt['popularity_score'],
                'source_platform': 'google_trends',
                'url': '',
                'media_type': 'text',
                'media_url': None
            })

        # Analyze and store
        if all_trends:
            self.analyze_and_store_trends(all_trends)

        logger.info(f"Scrape complete. Processed {len(all_trends)} trends")

        return len(all_trends)

    def get_current_meme_context_for_generation(self):
        """
        Get comprehensive current meme context for content generation

        Returns:
            String summary of current meme landscape
        """
        return self.enhanced_scraper.get_meme_context_summary()
