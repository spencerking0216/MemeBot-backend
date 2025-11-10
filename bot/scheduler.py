from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
from config import Config
from bot.twitter_client import TwitterClient
from bot.content_generator import ContentGenerator
from services.meme_scraper import MemeScraper
from database.models import BotAnalytics, get_session, init_db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MemeBot:
    """
    Main bot scheduler that orchestrates all bot activities
    """

    def __init__(self):
        """Initialize the bot"""
        logger.info("Initializing Meme Bot...")

        # Initialize database
        init_db()

        # Initialize components
        self.twitter = TwitterClient()
        self.content_gen = ContentGenerator(llm_provider='claude')
        self.scraper = MemeScraper()

        # Initialize scheduler
        self.scheduler = BackgroundScheduler()

        # Bot state
        self.is_running = False

        logger.info("Meme Bot initialized successfully")

    def start(self):
        """Start the bot with all scheduled jobs"""
        if not Config.BOT_ENABLED:
            logger.warning("Bot is disabled in config. Set BOT_ENABLED=true to enable.")
            return

        logger.info("Starting Meme Bot...")

        # Schedule jobs
        self._schedule_posting()
        self._schedule_trend_scraping()
        self._schedule_metric_updates()
        self._schedule_learning()
        self._schedule_analytics()

        # Start scheduler
        self.scheduler.start()
        self.is_running = True

        logger.info("Meme Bot started successfully!")
        logger.info(f"Posting interval: Every {Config.POST_INTERVAL_HOURS} hours")
        logger.info(f"Trend scraping interval: Every {Config.TREND_SCRAPE_INTERVAL_HOURS} hour(s)")

    def stop(self):
        """Stop the bot"""
        logger.info("Stopping Meme Bot...")
        self.scheduler.shutdown()
        self.is_running = False
        logger.info("Meme Bot stopped")

    def _schedule_posting(self):
        """Schedule regular meme posting or content generation"""

        if Config.CONTENT_GENERATOR_MODE:
            # Content generator mode: generate and queue for review
            self.scheduler.add_job(
                func=self.generate_content_to_queue,
                trigger=IntervalTrigger(hours=Config.GENERATE_INTERVAL_HOURS),
                id='generate_content',
                name='Generate Content to Queue',
                replace_existing=True
            )

            # Generate one immediately on startup
            self.scheduler.add_job(
                func=self.generate_content_to_queue,
                trigger='date',
                run_date=datetime.now(),
                id='initial_generate',
                name='Initial Content Generation'
            )

            logger.info(f"Scheduled: Content generation every {Config.GENERATE_INTERVAL_HOURS} hours (GENERATOR MODE)")
        else:
            # Auto-posting mode: post directly to Twitter
            self.scheduler.add_job(
                func=self.post_meme,
                trigger=IntervalTrigger(hours=Config.POST_INTERVAL_HOURS),
                id='post_meme',
                name='Post Meme Tweet',
                replace_existing=True
            )

            # Also post one immediately on startup
            self.scheduler.add_job(
                func=self.post_meme,
                trigger='date',
                run_date=datetime.now(),
                id='initial_post',
                name='Initial Post'
            )

            logger.info(f"Scheduled: Auto-posting every {Config.POST_INTERVAL_HOURS} hours")

    def _schedule_trend_scraping(self):
        """Schedule trend scraping from various sources"""
        self.scheduler.add_job(
            func=self.scrape_trends,
            trigger=IntervalTrigger(hours=Config.TREND_SCRAPE_INTERVAL_HOURS),
            id='scrape_trends',
            name='Scrape Meme Trends',
            replace_existing=True
        )

        # Run once on startup
        self.scheduler.add_job(
            func=self.scrape_trends,
            trigger='date',
            run_date=datetime.now(),
            id='initial_scrape',
            name='Initial Trend Scrape'
        )

        logger.info(f"Scheduled: Scraping trends every {Config.TREND_SCRAPE_INTERVAL_HOURS} hour(s)")

    def _schedule_metric_updates(self):
        """Schedule updates of tweet engagement metrics"""
        # Update metrics every 2 hours
        self.scheduler.add_job(
            func=self.update_tweet_metrics,
            trigger=IntervalTrigger(hours=2),
            id='update_metrics',
            name='Update Tweet Metrics',
            replace_existing=True
        )

        logger.info("Scheduled: Updating tweet metrics every 2 hours")

    def _schedule_learning(self):
        """Schedule learning sessions from top memes"""
        # Learn from top memes daily at 2 AM
        self.scheduler.add_job(
            func=self.learning_session,
            trigger=CronTrigger(hour=2, minute=0),
            id='learning_session',
            name='Daily Learning Session',
            replace_existing=True
        )

        logger.info("Scheduled: Daily learning session at 2:00 AM")

    def _schedule_analytics(self):
        """Schedule analytics collection"""
        # Collect analytics daily at midnight
        self.scheduler.add_job(
            func=self.collect_analytics,
            trigger=CronTrigger(hour=0, minute=0),
            id='collect_analytics',
            name='Daily Analytics Collection',
            replace_existing=True
        )

        logger.info("Scheduled: Daily analytics at midnight")

    def generate_content_to_queue(self):
        """Generate meme content and save to queue for manual review"""
        try:
            logger.info("Generating meme content for queue...")

            # Generate meme tweet
            meme = self.content_gen.generate_meme_tweet(
                use_trend=True,
                irony_level='post-ironic'
            )

            if not meme:
                logger.error("Failed to generate meme content")
                return

            # Save to content queue
            session = get_session()
            from database.models import ContentQueue

            evaluation = meme.get('evaluation', {})

            content_item = ContentQueue(
                content=meme['text'],
                meme_format=meme.get('meme_format'),
                irony_level=meme.get('irony_level'),
                topics=meme.get('topics', []),
                trend_context=meme.get('trend_context'),
                quality_score=meme.get('quality_score', 0),
                humor_score=evaluation.get('humor_score', 0),
                authenticity_score=evaluation.get('authenticity_score', 0),
                engagement_score=evaluation.get('engagement_score', 0),
                evaluation_data=evaluation,
                generation_prompt=meme.get('trend_context'),
                status='pending'
            )

            session.add(content_item)
            session.commit()

            logger.info(f"Content saved to queue (ID: {content_item.id}, Score: {content_item.quality_score})")
            logger.info(f"Preview: {meme['text'][:100]}...")

            session.close()

        except Exception as e:
            logger.error(f"Error generating content to queue: {e}", exc_info=True)

    def post_meme(self):
        """Generate and post a meme tweet (AUTO-POST MODE ONLY)"""
        try:
            logger.info("Generating meme content...")

            # Generate meme tweet
            meme = self.content_gen.generate_meme_tweet(
                use_trend=True,
                irony_level='post-ironic'
            )

            if not meme:
                logger.error("Failed to generate meme content")
                return

            # Check if quality is acceptable
            if not meme.get('should_post', True):
                logger.warning(f"Meme quality too low (score: {meme.get('quality_score', 0)}), skipping post")
                return

            # Post to Twitter
            logger.info(f"Posting tweet: {meme['text'][:50]}...")

            tweet = self.twitter.post_tweet(
                text=meme['text'],
                image_path=None  # For now, text-only tweets
            )

            # Update database with meme metadata
            session = get_session()
            from database.models import Tweet
            db_tweet = session.query(Tweet).filter_by(tweet_id=tweet.tweet_id).first()

            if db_tweet:
                db_tweet.meme_format = meme.get('meme_format')
                db_tweet.irony_level = meme.get('irony_level')
                db_tweet.topics = meme.get('topics', [])
                db_tweet.trend_context = meme.get('trend_context')
                db_tweet.generation_prompt = str(meme.get('evaluation', {}))
                session.commit()

            session.close()

            logger.info(f"Successfully posted meme tweet! Tweet ID: {tweet.tweet_id}")

        except Exception as e:
            logger.error(f"Error posting meme: {e}", exc_info=True)

    def scrape_trends(self):
        """Scrape meme trends from all sources"""
        try:
            logger.info("Scraping meme trends...")

            # Run full scrape
            count = self.scraper.run_full_scrape()

            logger.info(f"Trend scraping complete. Processed {count} trends")

        except Exception as e:
            logger.error(f"Error scraping trends: {e}", exc_info=True)

    def update_tweet_metrics(self):
        """Update engagement metrics for recent tweets"""
        try:
            logger.info("Updating tweet metrics...")

            session = get_session()
            from database.models import Tweet
            from datetime import timedelta

            # Get tweets from last 7 days
            cutoff_date = datetime.utcnow() - timedelta(days=7)
            recent_tweets = session.query(Tweet).filter(
                Tweet.posted_at >= cutoff_date
            ).all()

            for tweet in recent_tweets:
                try:
                    self.twitter.update_tweet_metrics(tweet.tweet_id)
                except Exception as e:
                    logger.warning(f"Failed to update metrics for tweet {tweet.tweet_id}: {e}")

            session.close()

            logger.info(f"Updated metrics for {len(recent_tweets)} tweets")

        except Exception as e:
            logger.error(f"Error updating tweet metrics: {e}", exc_info=True)

    def learning_session(self):
        """Run a learning session to analyze top memes"""
        try:
            logger.info("Starting learning session...")

            # Analyze top memes
            count = self.content_gen.learn_from_top_memes(limit=30)

            # Get content strategy summary
            strategy = self.content_gen.get_content_strategy_summary()

            logger.info(f"Learning session complete. Analyzed {count} memes")
            logger.info(f"Current strategy: {strategy}")

        except Exception as e:
            logger.error(f"Error in learning session: {e}", exc_info=True)

    def collect_analytics(self):
        """Collect daily analytics"""
        try:
            logger.info("Collecting daily analytics...")

            session = get_session()
            from database.models import Tweet

            # Get today's tweets
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_tweets = session.query(Tweet).filter(
                Tweet.posted_at >= today_start
            ).all()

            # Calculate metrics
            total_likes = sum(t.likes for t in today_tweets)
            total_retweets = sum(t.retweets for t in today_tweets)
            total_replies = sum(t.replies for t in today_tweets)
            total_impressions = sum(t.impressions for t in today_tweets)

            # Get account metrics
            account_metrics = self.twitter.get_account_metrics()

            # Find best performing tweet
            if today_tweets:
                best_tweet = max(today_tweets, key=lambda t: t.likes + t.retweets * 2)
                best_tweet_id = best_tweet.tweet_id
                best_format = best_tweet.meme_format
                best_irony = best_tweet.irony_level
            else:
                best_tweet_id = None
                best_format = None
                best_irony = None

            # Store analytics
            analytics = BotAnalytics(
                date=today_start,
                tweets_posted=len(today_tweets),
                total_likes=total_likes,
                total_retweets=total_retweets,
                total_replies=total_replies,
                total_impressions=total_impressions,
                follower_count=account_metrics.get('followers', 0) if account_metrics else 0,
                best_performing_tweet_id=best_tweet_id,
                best_performing_format=best_format,
                best_performing_irony_level=best_irony
            )

            session.add(analytics)
            session.commit()
            session.close()

            logger.info(f"Analytics collected: {len(today_tweets)} tweets, {total_likes} likes, {total_retweets} RTs")

        except Exception as e:
            logger.error(f"Error collecting analytics: {e}", exc_info=True)

    def post_now(self):
        """Manually trigger a post (useful for testing)"""
        logger.info("Manual post triggered")
        self.post_meme()

    def get_status(self):
        """Get bot status"""
        return {
            'running': self.is_running,
            'enabled': Config.BOT_ENABLED,
            'next_jobs': [
                {
                    'id': job.id,
                    'name': job.name,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in self.scheduler.get_jobs()
            ]
        }
