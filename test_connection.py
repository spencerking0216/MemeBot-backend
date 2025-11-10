"""
Test script to verify all connections are working

Run this before deploying to ensure everything is configured correctly
"""

import logging
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_twitter_connection():
    """Test Twitter API connection"""
    try:
        from bot.twitter_client import TwitterClient
        client = TwitterClient()
        account = client.get_account_metrics()
        logger.info(f"Twitter connection successful!")
        logger.info(f"Account metrics: {account}")
        return True
    except Exception as e:
        logger.error(f"Twitter connection failed: {e}")
        return False


def test_llm_connection():
    """Test LLM API connection"""
    try:
        from services.llm_service import LLMService
        llm = LLMService(provider='claude')
        result = llm.generate_meme_content(
            context="Test context for connection check",
            irony_level='ironic'
        )
        logger.info("LLM connection successful!")
        logger.info(f"Test generation: {result['text'][:100]}...")
        return True
    except Exception as e:
        logger.error(f"LLM connection failed: {e}")
        return False


def test_database_connection():
    """Test database connection"""
    try:
        from database.models import get_session
        session = get_session()
        session.execute("SELECT 1")
        session.close()
        logger.info("Database connection successful!")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def test_reddit_connection():
    """Test Reddit API connection"""
    try:
        from services.meme_scraper import MemeScraper
        scraper = MemeScraper()
        if scraper.reddit:
            logger.info("Reddit connection successful!")
            return True
        else:
            logger.warning("Reddit connection failed - check credentials")
            return False
    except Exception as e:
        logger.error(f"Reddit connection failed: {e}")
        return False


if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("Testing Connections")
    logger.info("=" * 50)

    results = {
        'Database': test_database_connection(),
        'Twitter': test_twitter_connection(),
        'LLM (Claude/GPT)': test_llm_connection(),
        'Reddit': test_reddit_connection()
    }

    logger.info("=" * 50)
    logger.info("Connection Test Results:")
    logger.info("=" * 50)

    all_passed = True
    for service, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{service}: {status}")
        if not passed:
            all_passed = False

    logger.info("=" * 50)

    if all_passed:
        logger.info("All connections successful! Ready to deploy.")
    else:
        logger.warning("Some connections failed. Please check configuration.")
        logger.warning("Review .env file and ensure all credentials are correct.")
