from services.llm_service import LLMService
from services.multimodal_analyzer import MultimodalAnalyzer
from services.meme_scraper import MemeScraper
from database.models import MemeTrend, MemeMedia, MemeTemplate, get_session
import logging
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentGenerator:
    """
    Orchestrates meme content generation using trends, templates, and AI
    """

    def __init__(self, llm_provider='claude'):
        """
        Initialize content generator

        Args:
            llm_provider: 'claude' or 'openai'
        """
        self.llm = LLMService(provider=llm_provider)
        self.multimodal = MultimodalAnalyzer(provider=llm_provider)
        self.scraper = MemeScraper()

    def generate_meme_tweet(self, use_trend=True, irony_level='post-ironic'):
        """
        Generate a complete meme tweet

        Args:
            use_trend: Whether to base on current trends
            irony_level: Level of irony to use

        Returns:
            Dictionary with tweet content and metadata
        """
        try:
            # Get context
            if use_trend:
                context = self._get_trend_context()
            else:
                context = self._get_random_context()

            # Analyze related media if available
            media_insights = self._get_media_insights(context)

            # Get current meme landscape context
            current_meme_context = self.scraper.get_current_meme_context_for_generation()

            # Build enhanced context with media insights and current meme landscape
            enhanced_context = self._build_enhanced_context(context, media_insights, current_meme_context)

            # Generate meme content
            meme_data = self.llm.generate_meme_content(
                context=enhanced_context,
                irony_level=irony_level
            )

            # Self-evaluate quality
            evaluation = self.llm.evaluate_generated_meme(meme_data['text'])

            # If quality is too low, regenerate once
            if evaluation.get('overall_score', 0) < 5:
                logger.info("Low quality meme, regenerating...")
                meme_data = self.llm.generate_meme_content(
                    context=enhanced_context,
                    irony_level=irony_level
                )
                evaluation = self.llm.evaluate_generated_meme(meme_data['text'])

            result = {
                'text': meme_data['text'],
                'meme_format': meme_data.get('format'),
                'irony_level': irony_level,
                'topics': meme_data.get('topics', []),
                'trend_context': context,
                'quality_score': evaluation.get('overall_score', 5),
                'should_post': evaluation.get('should_post', True),
                'evaluation': evaluation
            }

            logger.info(f"Generated meme tweet (score: {result['quality_score']}): {result['text'][:50]}...")

            return result

        except Exception as e:
            logger.error(f"Failed to generate meme tweet: {e}")
            return None

    def _get_trend_context(self):
        """Get context from current trends"""
        session = get_session()

        # Get top trends
        trends = session.query(MemeTrend).filter(
            MemeTrend.popularity_score >= 30,
            MemeTrend.lifecycle_stage.in_(['rising', 'peak'])
        ).order_by(
            MemeTrend.popularity_score.desc()
        ).limit(5).all()

        session.close()

        if not trends:
            return "Current internet culture and relatable situations"

        # Pick a random trend from top trends
        trend = random.choice(trends)

        context = f"{trend.name}"
        if trend.description:
            context += f" - {trend.description[:200]}"

        return context

    def _get_random_context(self):
        """Get random relatable context"""
        contexts = [
            "Being chronically online and understanding way too many references",
            "The experience of doom scrolling at 3am",
            "Pretending to understand crypto/NFTs",
            "Existential dread but make it funny",
            "When the group chat is fire",
            "Main character energy vs side quest energy",
            "The duality of wanting to be productive vs wanting to rot in bed",
            "That specific kind of anxiety only gen z understands",
            "Touch grass? In this economy?",
            "When the algorithm knows you too well",
        ]

        return random.choice(contexts)

    def _get_media_insights(self, context):
        """Get insights from related media in database"""
        session = get_session()

        # Try to find related media based on topics
        # For now, get recent high-scoring media
        media = session.query(MemeMedia).filter(
            MemeMedia.meme_potential_score >= 60
        ).order_by(
            MemeMedia.analyzed_at.desc()
        ).limit(3).all()

        session.close()

        if not media:
            return None

        # Extract insights
        insights = {
            'formats': [],
            'humor_types': [],
            'references': [],
            'successful_patterns': []
        }

        for m in media:
            if m.meme_format:
                insights['formats'].append(m.meme_format)
            if m.humor_type:
                insights['humor_types'].append(m.humor_type)
            if m.cultural_references:
                insights['references'].extend(m.cultural_references)

        return insights

    def _build_enhanced_context(self, base_context, media_insights, current_meme_context=None):
        """Build enhanced context with media insights and current meme landscape"""
        context = base_context

        if media_insights:
            if media_insights['formats']:
                context += f"\n\nSuccessful formats recently: {', '.join(set(media_insights['formats'][:3]))}"

            if media_insights['references']:
                context += f"\nCultural references trending: {', '.join(set(media_insights['references'][:5]))}"

        # Add current meme landscape for maximum relevance
        if current_meme_context:
            context += f"\n\n--- CURRENT MEME LANDSCAPE ---\n{current_meme_context[:1000]}"

        return context

    def analyze_and_learn_from_media(self, media_url, media_type='image'):
        """
        Analyze media and store learnings in database

        Args:
            media_url: URL to media
            media_type: 'image', 'video', or 'audio'

        Returns:
            MemeMedia object or None
        """
        try:
            session = get_session()

            # Check if already analyzed
            existing = session.query(MemeMedia).filter_by(media_url=media_url).first()
            if existing:
                logger.info(f"Media already analyzed: {media_url}")
                session.close()
                return existing

            # Analyze based on type
            if media_type == 'image':
                analysis = self.multimodal.analyze_image(media_url)
            elif media_type == 'video':
                analysis = self.multimodal.analyze_video(media_url)
            elif media_type == 'audio':
                analysis = self.multimodal.analyze_audio(media_url)
            else:
                logger.warning(f"Unknown media type: {media_type}")
                session.close()
                return None

            if not analysis or 'error' in analysis:
                logger.warning(f"Failed to analyze media: {media_url}")
                session.close()
                return None

            # Store in database
            media_obj = MemeMedia(
                media_url=media_url,
                media_type=media_type,
                visual_description=analysis.get('visual_description', ''),
                meme_format=analysis.get('meme_format'),
                text_content=analysis.get('text_content', []),
                humor_type=analysis.get('humor_type'),
                irony_level=analysis.get('irony_level'),
                cultural_references=analysis.get('cultural_references', []),
                emotional_tone=analysis.get('emotional_tone'),
                topics=analysis.get('topics', []),
                meme_potential_score=analysis.get('meme_potential_score', 0),
                analysis_data=analysis,
                source_url=media_url
            )

            session.add(media_obj)
            session.commit()

            logger.info(f"Analyzed and stored media: {media_url}")

            media_id = media_obj.id
            session.close()

            # Return fresh object
            session = get_session()
            result = session.query(MemeMedia).filter_by(id=media_id).first()
            session.close()

            return result

        except Exception as e:
            logger.error(f"Error analyzing media: {e}")
            if session:
                session.rollback()
                session.close()
            return None

    def learn_from_top_memes(self, limit=20):
        """
        Scrape and analyze top memes to learn patterns

        Args:
            limit: Number of memes to analyze

        Returns:
            Number of memes analyzed
        """
        logger.info("Starting learning session from top memes...")

        # Scrape recent trends
        trends = self.scraper.scrape_reddit_memes(limit=limit)

        analyzed_count = 0

        for trend in trends:
            media_url = trend.get('media_url')
            media_type = trend.get('media_type', 'text')

            if media_url and media_type in ['image', 'video']:
                try:
                    result = self.analyze_and_learn_from_media(media_url, media_type)
                    if result:
                        analyzed_count += 1
                except Exception as e:
                    logger.error(f"Error analyzing {media_url}: {e}")
                    continue

        logger.info(f"Learning session complete. Analyzed {analyzed_count} media items")

        return analyzed_count

    def get_content_strategy_summary(self):
        """
        Get summary of what's working in meme content

        Returns:
            Dictionary with strategy insights
        """
        session = get_session()

        # Analyze what's successful
        top_media = session.query(MemeMedia).filter(
            MemeMedia.meme_potential_score >= 70
        ).order_by(
            MemeMedia.meme_potential_score.desc()
        ).limit(10).all()

        # Aggregate patterns
        formats = {}
        humor_types = {}
        irony_levels = {}
        topics = {}

        for media in top_media:
            if media.meme_format:
                formats[media.meme_format] = formats.get(media.meme_format, 0) + 1
            if media.humor_type:
                humor_types[media.humor_type] = humor_types.get(media.humor_type, 0) + 1
            if media.irony_level:
                irony_levels[media.irony_level] = irony_levels.get(media.irony_level, 0) + 1
            if media.topics:
                for topic in media.topics:
                    topics[topic] = topics.get(topic, 0) + 1

        session.close()

        # Sort by frequency
        top_formats = sorted(formats.items(), key=lambda x: x[1], reverse=True)[:5]
        top_humor = sorted(humor_types.items(), key=lambda x: x[1], reverse=True)[:5]
        top_irony = sorted(irony_levels.items(), key=lambda x: x[1], reverse=True)[:3]
        top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:10]

        summary = {
            'top_formats': [f[0] for f in top_formats],
            'top_humor_types': [h[0] for h in top_humor],
            'recommended_irony_levels': [i[0] for i in top_irony],
            'trending_topics': [t[0] for t in top_topics]
        }

        logger.info(f"Content strategy summary generated")

        return summary
