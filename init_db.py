"""
Database initialization script

Run this to create all tables in the database
"""

from database.models import init_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("Initializing database...")
    try:
        init_db()
        logger.info("Database initialized successfully!")
        logger.info("All tables have been created.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
