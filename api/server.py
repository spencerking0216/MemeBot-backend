from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
from config import Config
from database.models import Tweet, MemeTrend, BotAnalytics, MemeMedia, get_session
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')

# Configure CORS - allow all origins if FRONTEND_URL not set
cors_origins = Config.FRONTEND_URL if Config.FRONTEND_URL else '*'
CORS(app, origins=cors_origins)


# Review UI
@app.route('/')
@app.route('/review')
def review_ui():
    """Serve content review UI"""
    return send_from_directory('static', 'review.html')


# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })


# Tweet endpoints
@app.route('/api/tweets', methods=['GET'])
def get_tweets():
    """Get recent tweets posted by the bot"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)

        session = get_session()

        # Query tweets
        tweets = session.query(Tweet).order_by(
            Tweet.posted_at.desc()
        ).limit(limit).offset(offset).all()

        # Convert to dict
        result = []
        for tweet in tweets:
            result.append({
                'id': tweet.id,
                'tweet_id': tweet.tweet_id,
                'content': tweet.content,
                'image_url': tweet.image_url,
                'posted_at': tweet.posted_at.isoformat(),
                'likes': tweet.likes,
                'retweets': tweet.retweets,
                'replies': tweet.replies,
                'impressions': tweet.impressions,
                'meme_format': tweet.meme_format,
                'irony_level': tweet.irony_level,
                'topics': tweet.topics,
                'trend_context': tweet.trend_context
            })

        session.close()

        return jsonify({
            'tweets': result,
            'count': len(result),
            'limit': limit,
            'offset': offset
        })

    except Exception as e:
        logger.error(f"Error fetching tweets: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/tweets/<tweet_id>', methods=['GET'])
def get_tweet(tweet_id):
    """Get a specific tweet by ID"""
    try:
        session = get_session()

        tweet = session.query(Tweet).filter_by(tweet_id=tweet_id).first()

        if not tweet:
            session.close()
            return jsonify({'error': 'Tweet not found'}), 404

        result = {
            'id': tweet.id,
            'tweet_id': tweet.tweet_id,
            'content': tweet.content,
            'image_url': tweet.image_url,
            'posted_at': tweet.posted_at.isoformat(),
            'likes': tweet.likes,
            'retweets': tweet.retweets,
            'replies': tweet.replies,
            'impressions': tweet.impressions,
            'meme_format': tweet.meme_format,
            'irony_level': tweet.irony_level,
            'topics': tweet.topics,
            'trend_context': tweet.trend_context
        }

        session.close()

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error fetching tweet: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/tweets/top', methods=['GET'])
def get_top_tweets():
    """Get top performing tweets"""
    try:
        limit = request.args.get('limit', 10, type=int)
        days = request.args.get('days', 7, type=int)

        session = get_session()

        # Get tweets from last N days
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        tweets = session.query(Tweet).filter(
            Tweet.posted_at >= cutoff_date
        ).order_by(
            (Tweet.likes + Tweet.retweets * 2).desc()
        ).limit(limit).all()

        result = []
        for tweet in tweets:
            result.append({
                'id': tweet.id,
                'tweet_id': tweet.tweet_id,
                'content': tweet.content,
                'posted_at': tweet.posted_at.isoformat(),
                'likes': tweet.likes,
                'retweets': tweet.retweets,
                'replies': tweet.replies,
                'engagement_score': tweet.likes + tweet.retweets * 2,
                'meme_format': tweet.meme_format,
                'irony_level': tweet.irony_level
            })

        session.close()

        return jsonify({'tweets': result, 'count': len(result)})

    except Exception as e:
        logger.error(f"Error fetching top tweets: {e}")
        return jsonify({'error': str(e)}), 500


# Trends endpoints
@app.route('/api/trends', methods=['GET'])
def get_trends():
    """Get current meme trends"""
    try:
        limit = request.args.get('limit', 20, type=int)
        min_score = request.args.get('min_score', 0, type=float)

        session = get_session()

        trends = session.query(MemeTrend).filter(
            MemeTrend.popularity_score >= min_score
        ).order_by(
            MemeTrend.popularity_score.desc()
        ).limit(limit).all()

        result = []
        for trend in trends:
            result.append({
                'id': trend.id,
                'name': trend.name,
                'description': trend.description,
                'popularity_score': trend.popularity_score,
                'velocity': trend.velocity,
                'lifecycle_stage': trend.lifecycle_stage,
                'source_platform': trend.source_platform,
                'first_seen': trend.first_seen.isoformat(),
                'last_seen': trend.last_seen.isoformat(),
                'related_topics': trend.related_topics,
                'times_used': trend.times_used
            })

        session.close()

        return jsonify({'trends': result, 'count': len(result)})

    except Exception as e:
        logger.error(f"Error fetching trends: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/trends/trending', methods=['GET'])
def get_trending():
    """Get currently trending memes (rising/peak stage)"""
    try:
        limit = request.args.get('limit', 10, type=int)

        session = get_session()

        trends = session.query(MemeTrend).filter(
            MemeTrend.lifecycle_stage.in_(['rising', 'peak'])
        ).order_by(
            MemeTrend.popularity_score.desc()
        ).limit(limit).all()

        result = []
        for trend in trends:
            result.append({
                'id': trend.id,
                'name': trend.name,
                'description': trend.description,
                'popularity_score': trend.popularity_score,
                'velocity': trend.velocity,
                'lifecycle_stage': trend.lifecycle_stage,
                'source_platform': trend.source_platform
            })

        session.close()

        return jsonify({'trends': result, 'count': len(result)})

    except Exception as e:
        logger.error(f"Error fetching trending: {e}")
        return jsonify({'error': str(e)}), 500


# Analytics endpoints
@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get bot analytics"""
    try:
        days = request.args.get('days', 7, type=int)

        session = get_session()

        # Get analytics from last N days
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        analytics = session.query(BotAnalytics).filter(
            BotAnalytics.date >= cutoff_date
        ).order_by(
            BotAnalytics.date.desc()
        ).all()

        result = []
        for entry in analytics:
            result.append({
                'date': entry.date.isoformat(),
                'tweets_posted': entry.tweets_posted,
                'total_likes': entry.total_likes,
                'total_retweets': entry.total_retweets,
                'total_replies': entry.total_replies,
                'total_impressions': entry.total_impressions,
                'follower_count': entry.follower_count,
                'followers_gained': entry.followers_gained,
                'avg_engagement_rate': entry.avg_engagement_rate,
                'best_performing_format': entry.best_performing_format,
                'best_performing_irony_level': entry.best_performing_irony_level
            })

        session.close()

        return jsonify({'analytics': result, 'count': len(result)})

    except Exception as e:
        logger.error(f"Error fetching analytics: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """Get summary analytics"""
    try:
        session = get_session()

        # Get total stats
        from sqlalchemy import func

        total_tweets = session.query(func.count(Tweet.id)).scalar()
        total_likes = session.query(func.sum(Tweet.likes)).scalar() or 0
        total_retweets = session.query(func.sum(Tweet.retweets)).scalar() or 0

        # Get recent performance (last 7 days)
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        recent_tweets = session.query(Tweet).filter(
            Tweet.posted_at >= cutoff_date
        ).all()

        recent_likes = sum(t.likes for t in recent_tweets)
        recent_retweets = sum(t.retweets for t in recent_tweets)

        # Calculate averages
        avg_likes = recent_likes / len(recent_tweets) if recent_tweets else 0
        avg_retweets = recent_retweets / len(recent_tweets) if recent_tweets else 0

        session.close()

        return jsonify({
            'total_tweets': total_tweets,
            'total_likes': total_likes,
            'total_retweets': total_retweets,
            'recent_tweets_7d': len(recent_tweets),
            'recent_likes_7d': recent_likes,
            'recent_retweets_7d': recent_retweets,
            'avg_likes_per_tweet': round(avg_likes, 2),
            'avg_retweets_per_tweet': round(avg_retweets, 2)
        })

    except Exception as e:
        logger.error(f"Error fetching analytics summary: {e}")
        return jsonify({'error': str(e)}), 500


# Media endpoints
@app.route('/api/media', methods=['GET'])
def get_media():
    """Get analyzed media"""
    try:
        limit = request.args.get('limit', 20, type=int)
        media_type = request.args.get('type', None)
        min_score = request.args.get('min_score', 0, type=float)

        session = get_session()

        query = session.query(MemeMedia).filter(
            MemeMedia.meme_potential_score >= min_score
        )

        if media_type:
            query = query.filter(MemeMedia.media_type == media_type)

        media_items = query.order_by(
            MemeMedia.meme_potential_score.desc()
        ).limit(limit).all()

        result = []
        for media in media_items:
            result.append({
                'id': media.id,
                'media_url': media.media_url,
                'media_type': media.media_type,
                'visual_description': media.visual_description,
                'meme_format': media.meme_format,
                'humor_type': media.humor_type,
                'irony_level': media.irony_level,
                'topics': media.topics,
                'meme_potential_score': media.meme_potential_score,
                'analyzed_at': media.analyzed_at.isoformat()
            })

        session.close()

        return jsonify({'media': result, 'count': len(result)})

    except Exception as e:
        logger.error(f"Error fetching media: {e}")
        return jsonify({'error': str(e)}), 500


# Content Queue endpoints (for content generator mode)
@app.route('/api/queue', methods=['GET'])
def get_content_queue():
    """Get content queue for review"""
    try:
        status = request.args.get('status', 'pending')
        limit = request.args.get('limit', 20, type=int)

        session = get_session()
        from database.models import ContentQueue

        query = session.query(ContentQueue)

        if status:
            query = query.filter(ContentQueue.status == status)

        items = query.order_by(
            ContentQueue.created_at.desc()
        ).limit(limit).all()

        result = []
        for item in items:
            result.append({
                'id': item.id,
                'content': item.content,
                'meme_format': item.meme_format,
                'irony_level': item.irony_level,
                'topics': item.topics,
                'trend_context': item.trend_context,
                'quality_score': item.quality_score,
                'humor_score': item.humor_score,
                'authenticity_score': item.authenticity_score,
                'engagement_score': item.engagement_score,
                'status': item.status,
                'created_at': item.created_at.isoformat(),
                'evaluation_data': item.evaluation_data
            })

        session.close()

        return jsonify({'queue': result, 'count': len(result)})

    except Exception as e:
        logger.error(f"Error fetching content queue: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/queue/<int:item_id>', methods=['GET'])
def get_queue_item(item_id):
    """Get specific queue item"""
    try:
        session = get_session()
        from database.models import ContentQueue

        item = session.query(ContentQueue).filter_by(id=item_id).first()

        if not item:
            session.close()
            return jsonify({'error': 'Item not found'}), 404

        result = {
            'id': item.id,
            'content': item.content,
            'meme_format': item.meme_format,
            'irony_level': item.irony_level,
            'topics': item.topics,
            'trend_context': item.trend_context,
            'quality_score': item.quality_score,
            'humor_score': item.humor_score,
            'authenticity_score': item.authenticity_score,
            'engagement_score': item.engagement_score,
            'evaluation_data': item.evaluation_data,
            'status': item.status,
            'reviewer_notes': item.reviewer_notes,
            'created_at': item.created_at.isoformat(),
            'reviewed_at': item.reviewed_at.isoformat() if item.reviewed_at else None,
            'posted_at': item.posted_at.isoformat() if item.posted_at else None,
            'posted_tweet_id': item.posted_tweet_id
        }

        session.close()

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error fetching queue item: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/queue/<int:item_id>/approve', methods=['POST'])
def approve_queue_item(item_id):
    """Approve a queue item"""
    try:
        session = get_session()
        from database.models import ContentQueue

        item = session.query(ContentQueue).filter_by(id=item_id).first()

        if not item:
            session.close()
            return jsonify({'error': 'Item not found'}), 404

        data = request.json or {}

        item.status = 'approved'
        item.reviewed_at = datetime.utcnow()
        item.reviewer_notes = data.get('notes', '')

        session.commit()
        session.close()

        return jsonify({'success': True, 'message': 'Item approved'})

    except Exception as e:
        logger.error(f"Error approving queue item: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/queue/<int:item_id>/reject', methods=['POST'])
def reject_queue_item(item_id):
    """Reject a queue item"""
    try:
        session = get_session()
        from database.models import ContentQueue

        item = session.query(ContentQueue).filter_by(id=item_id).first()

        if not item:
            session.close()
            return jsonify({'error': 'Item not found'}), 404

        data = request.json or {}

        item.status = 'rejected'
        item.reviewed_at = datetime.utcnow()
        item.reviewer_notes = data.get('notes', '')

        session.commit()
        session.close()

        return jsonify({'success': True, 'message': 'Item rejected'})

    except Exception as e:
        logger.error(f"Error rejecting queue item: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/queue/<int:item_id>/mark-posted', methods=['POST'])
def mark_queue_item_posted(item_id):
    """Mark a queue item as posted (after manual posting)"""
    try:
        session = get_session()
        from database.models import ContentQueue

        item = session.query(ContentQueue).filter_by(id=item_id).first()

        if not item:
            session.close()
            return jsonify({'error': 'Item not found'}), 404

        data = request.json or {}

        item.status = 'posted'
        item.posted_at = datetime.utcnow()
        item.posted_tweet_id = data.get('tweet_id', '')

        session.commit()
        session.close()

        return jsonify({'success': True, 'message': 'Item marked as posted'})

    except Exception as e:
        logger.error(f"Error marking item as posted: {e}")
        return jsonify({'error': str(e)}), 500


# Bot status endpoint
@app.route('/api/status', methods=['GET'])
def get_bot_status():
    """Get bot status"""
    try:
        # This would interact with the running bot instance
        # For now, return basic info
        return jsonify({
            'status': 'running',
            'enabled': Config.BOT_ENABLED,
            'content_generator_mode': Config.CONTENT_GENERATOR_MODE,
            'post_interval_hours': Config.POST_INTERVAL_HOURS,
            'generate_interval_hours': Config.GENERATE_INTERVAL_HOURS,
            'trend_scrape_interval_hours': Config.TREND_SCRAPE_INTERVAL_HOURS
        })

    except Exception as e:
        logger.error(f"Error fetching bot status: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=Config.PORT,
        debug=(Config.ENVIRONMENT == 'development')
    )
