import tweepy
from config import Config
from database.models import Tweet, get_session
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TwitterClient:
    """Handles all Twitter API interactions"""

    def __init__(self):
        self.api = self._authenticate()
        self.client = self._authenticate_v2()

    def _authenticate(self):
        """Authenticate with Twitter API v1.1 (for media upload)"""
        try:
            auth = tweepy.OAuthHandler(
                Config.TWITTER_API_KEY,
                Config.TWITTER_API_SECRET
            )
            auth.set_access_token(
                Config.TWITTER_ACCESS_TOKEN,
                Config.TWITTER_ACCESS_TOKEN_SECRET
            )
            api = tweepy.API(auth)
            api.verify_credentials()
            logger.info("Twitter API v1.1 authentication successful")
            return api
        except Exception as e:
            logger.error(f"Twitter API v1.1 authentication failed: {e}")
            raise

    def _authenticate_v2(self):
        """Authenticate with Twitter API v2 (for posting and metrics)"""
        try:
            client = tweepy.Client(
                bearer_token=Config.TWITTER_BEARER_TOKEN,
                consumer_key=Config.TWITTER_API_KEY,
                consumer_secret=Config.TWITTER_API_SECRET,
                access_token=Config.TWITTER_ACCESS_TOKEN,
                access_token_secret=Config.TWITTER_ACCESS_TOKEN_SECRET
            )
            logger.info("Twitter API v2 authentication successful")
            return client
        except Exception as e:
            logger.error(f"Twitter API v2 authentication failed: {e}")
            raise

    def post_tweet(self, text, image_path=None):
        """
        Post a tweet with optional image

        Args:
            text: Tweet text content
            image_path: Optional path to image file

        Returns:
            Tweet object with tweet_id
        """
        try:
            media_id = None

            # Upload image if provided
            if image_path:
                media = self.api.media_upload(image_path)
                media_id = media.media_id
                logger.info(f"Image uploaded with media_id: {media_id}")

            # Post tweet using API v2
            if media_id:
                response = self.client.create_tweet(
                    text=text,
                    media_ids=[media_id]
                )
            else:
                response = self.client.create_tweet(text=text)

            tweet_id = response.data['id']
            logger.info(f"Tweet posted successfully: {tweet_id}")

            # Save to database
            session = get_session()
            tweet = Tweet(
                tweet_id=str(tweet_id),
                content=text,
                image_url=image_path,
                posted_at=datetime.utcnow()
            )
            session.add(tweet)
            session.commit()
            session.close()

            return tweet

        except Exception as e:
            logger.error(f"Failed to post tweet: {e}")
            raise

    def get_tweet_metrics(self, tweet_id):
        """
        Fetch engagement metrics for a specific tweet

        Args:
            tweet_id: Twitter tweet ID

        Returns:
            Dictionary with metrics
        """
        try:
            tweet = self.client.get_tweet(
                tweet_id,
                tweet_fields=['public_metrics']
            )

            metrics = tweet.data.public_metrics

            return {
                'likes': metrics['like_count'],
                'retweets': metrics['retweet_count'],
                'replies': metrics['reply_count'],
                'impressions': metrics.get('impression_count', 0)
            }
        except Exception as e:
            logger.error(f"Failed to fetch metrics for tweet {tweet_id}: {e}")
            return None

    def update_tweet_metrics(self, tweet_id):
        """
        Update database with latest tweet metrics

        Args:
            tweet_id: Twitter tweet ID
        """
        metrics = self.get_tweet_metrics(tweet_id)
        if not metrics:
            return

        session = get_session()
        tweet = session.query(Tweet).filter_by(tweet_id=str(tweet_id)).first()

        if tweet:
            tweet.likes = metrics['likes']
            tweet.retweets = metrics['retweets']
            tweet.replies = metrics['replies']
            tweet.impressions = metrics['impressions']
            tweet.last_updated = datetime.utcnow()
            session.commit()
            logger.info(f"Updated metrics for tweet {tweet_id}")

        session.close()

    def get_trending_topics(self, location_id=23424977):
        """
        Get current trending topics on Twitter

        Args:
            location_id: WOEID for location (default: United States)

        Returns:
            List of trending topics
        """
        try:
            trends = self.api.get_place_trends(location_id)
            trending_topics = []

            for trend in trends[0]['trends']:
                trending_topics.append({
                    'name': trend['name'],
                    'tweet_volume': trend.get('tweet_volume'),
                    'url': trend['url']
                })

            logger.info(f"Fetched {len(trending_topics)} trending topics")
            return trending_topics

        except Exception as e:
            logger.error(f"Failed to fetch trending topics: {e}")
            return []

    def search_tweets(self, query, max_results=10):
        """
        Search for tweets matching a query

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of tweets
        """
        try:
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=['public_metrics', 'created_at']
            )

            if not tweets.data:
                return []

            results = []
            for tweet in tweets.data:
                results.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'metrics': tweet.public_metrics
                })

            return results

        except Exception as e:
            logger.error(f"Failed to search tweets: {e}")
            return []

    def get_account_metrics(self):
        """
        Get metrics for the bot's own account

        Returns:
            Dictionary with account metrics
        """
        try:
            # Get authenticated user
            user = self.client.get_me(user_fields=['public_metrics'])

            return {
                'followers': user.data.public_metrics['followers_count'],
                'following': user.data.public_metrics['following_count'],
                'tweet_count': user.data.public_metrics['tweet_count']
            }
        except Exception as e:
            logger.error(f"Failed to fetch account metrics: {e}")
            return None
