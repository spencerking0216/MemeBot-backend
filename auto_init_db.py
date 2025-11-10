"""
Auto-initialize database on first run
This runs before the main app starts
"""

import logging
from database.models import init_db, get_session
from sqlalchemy.exc import OperationalError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_and_init_db():
    """Check if database is initialized, if not, initialize it"""
    try:
        session = get_session()

        # Try to query a table - if it doesn't exist, this will fail
        from database.models import ContentQueue
        session.query(ContentQueue).first()

        session.close()
        logger.info("Database already initialized")
        return True

    except OperationalError as e:
        # Tables don't exist, initialize them
        logger.info("Database not initialized. Creating tables...")

        try:
            init_db()
            logger.info("Database initialized successfully!")
            return True
        except Exception as init_error:
            logger.error(f"Failed to initialize database: {init_error}")
            return False

    except Exception as e:
        logger.error(f"Error checking database: {e}")
        return False


if __name__ == '__main__':
    check_and_init_db()
