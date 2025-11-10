"""
Main entry point for the Meme Bot Backend

This file starts both the bot scheduler and the API server
"""

import threading
import logging
import signal
import sys
from bot.scheduler import MemeBot
from api.server import app
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global bot instance
bot = None


def start_bot():
    """Start the meme bot in a separate thread"""
    global bot
    try:
        bot = MemeBot()
        bot.start()
        logger.info("Bot thread started")

        # Keep the thread alive
        while bot.is_running:
            import time
            time.sleep(1)

    except Exception as e:
        logger.error(f"Error in bot thread: {e}", exc_info=True)


def start_api():
    """Start the Flask API server"""
    try:
        logger.info(f"Starting API server on port {Config.PORT}...")
        app.run(
            host='0.0.0.0',
            port=Config.PORT,
            debug=False,  # Don't use debug in production
            use_reloader=False  # Disable reloader to avoid duplicate bot instances
        )
    except Exception as e:
        logger.error(f"Error in API server: {e}", exc_info=True)


def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    global bot
    logger.info("Shutdown signal received. Stopping bot...")

    if bot:
        bot.stop()

    logger.info("Goodbye!")
    sys.exit(0)


def main():
    """Main entry point"""
    logger.info("=" * 50)
    logger.info("Starting Meme Bot Backend")
    logger.info("=" * 50)
    logger.info(f"Environment: {Config.ENVIRONMENT}")
    logger.info(f"Port: {Config.PORT}")
    logger.info(f"Bot Enabled: {Config.BOT_ENABLED}")
    logger.info("=" * 50)

    # Auto-initialize database on first run
    # If database initialization fails, we'll still start the API server
    # but bot features will be unavailable
    db_ready = False
    if Config.DATABASE_URL:
        logger.info("Checking database...")
        from auto_init_db import check_and_init_db
        db_ready = check_and_init_db()
        if not db_ready:
            logger.warning("Database initialization failed. API server will start but bot features will be unavailable.")
    else:
        logger.warning("DATABASE_URL not set. API server will start but bot features will be unavailable.")

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start bot in separate thread only if database is ready
    if Config.BOT_ENABLED and db_ready:
        bot_thread = threading.Thread(target=start_bot, daemon=True)
        bot_thread.start()
        logger.info("Bot scheduler thread started")
    else:
        logger.warning("Bot is disabled. Only API server will run.")

    # Start API server in main thread
    start_api()


if __name__ == '__main__':
    main()
