"""
Enhanced meme scraper with better sources for current meme context
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
import re
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedMemeScraper:
    """Enhanced scraping for current meme trends with better context"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def scrape_know_your_meme_trending(self):
        """Scrape detailed trending memes from Know Your Meme"""
        try:
            url = "https://knowyourmeme.com/memes/trending"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            trends = []

            # Find trending meme entries
            entries = soup.find_all('td', class_='entry_info')

            for entry in entries[:20]:  # Top 20
                try:
                    # Get meme name and link
                    link_elem = entry.find('a')
                    if not link_elem:
                        continue

                    name = link_elem.get_text(strip=True)
                    meme_url = "https://knowyourmeme.com" + link_elem.get('href', '')

                    # Try to get description
                    desc_elem = entry.find('p')
                    description = desc_elem.get_text(strip=True) if desc_elem else ''

                    # Scrape individual meme page for more context
                    meme_context = self._scrape_individual_meme(meme_url)

                    trends.append({
                        'name': name,
                        'description': description,
                        'url': meme_url,
                        'source': 'knowyourmeme',
                        'context': meme_context,
                        'popularity_score': 70  # KYM trending is high quality
                    })

                    logger.info(f"Scraped KYM meme: {name}")

                except Exception as e:
                    logger.debug(f"Error parsing KYM entry: {e}")
                    continue

            logger.info(f"Scraped {len(trends)} trends from Know Your Meme")
            return trends

        except Exception as e:
            logger.error(f"Failed to scrape Know Your Meme: {e}")
            return []

    def _scrape_individual_meme(self, url):
        """Scrape individual meme page for detailed context"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Get "About" section
            about_section = soup.find('section', id='about')
            about_text = about_section.get_text(strip=True)[:500] if about_section else ''

            # Get origin info
            origin_section = soup.find('section', id='origin')
            origin_text = origin_section.get_text(strip=True)[:300] if origin_section else ''

            # Get tags
            tags = []
            tag_elements = soup.find_all('a', href=re.compile(r'/memes/tags/'))
            for tag in tag_elements[:10]:
                tags.append(tag.get_text(strip=True))

            return {
                'about': about_text,
                'origin': origin_text,
                'tags': tags,
                'scraped_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.debug(f"Failed to scrape individual meme page: {e}")
            return {}

    def scrape_urban_dictionary_trending(self):
        """Scrape trending slang from Urban Dictionary for current language"""
        try:
            url = "https://www.urbandictionary.com"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            trends = []

            # Find trending words
            trending_words = soup.find_all('a', class_='word')

            for word_elem in trending_words[:15]:
                try:
                    word = word_elem.get_text(strip=True)

                    # Get definition
                    definition_elem = word_elem.find_next('div', class_='meaning')
                    definition = definition_elem.get_text(strip=True)[:200] if definition_elem else ''

                    trends.append({
                        'word': word,
                        'definition': definition,
                        'source': 'urban_dictionary',
                        'context_type': 'slang'
                    })

                except Exception as e:
                    logger.debug(f"Error parsing UD entry: {e}")
                    continue

            logger.info(f"Scraped {len(trends)} slang terms from Urban Dictionary")
            return trends

        except Exception as e:
            logger.error(f"Failed to scrape Urban Dictionary: {e}")
            return []

    def scrape_google_trends(self, region='US'):
        """Get current Google Trends data for meme-worthy topics"""
        try:
            # Google Trends RSS feed for daily trends
            url = f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={region}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'xml')
            trends = []

            items = soup.find_all('item')

            for item in items[:20]:
                try:
                    title = item.find('title').get_text(strip=True)
                    traffic = item.find('ht:approx_traffic')
                    traffic_num = traffic.get_text(strip=True) if traffic else '0'

                    # Get news title for context
                    news_item = item.find('ht:news_item')
                    news_title = ''
                    if news_item:
                        news_title_elem = news_item.find('ht:news_item_title')
                        news_title = news_title_elem.get_text(strip=True) if news_title_elem else ''

                    trends.append({
                        'topic': title,
                        'traffic': traffic_num,
                        'news_context': news_title,
                        'source': 'google_trends',
                        'popularity_score': self._estimate_score_from_traffic(traffic_num)
                    })

                except Exception as e:
                    logger.debug(f"Error parsing Google Trends item: {e}")
                    continue

            logger.info(f"Scraped {len(trends)} trends from Google Trends")
            return trends

        except Exception as e:
            logger.error(f"Failed to scrape Google Trends: {e}")
            return []

    def _estimate_score_from_traffic(self, traffic_str):
        """Estimate popularity score from traffic string"""
        try:
            # Extract number from strings like "500K+", "2M+"
            traffic_str = traffic_str.replace(',', '').replace('+', '')

            if 'M' in traffic_str:
                num = float(traffic_str.replace('M', ''))
                return min(num * 20, 100)  # 1M = 20 points
            elif 'K' in traffic_str:
                num = float(traffic_str.replace('K', ''))
                return min(num / 10, 100)  # 100K = 10 points
            else:
                num = float(traffic_str)
                return min(num / 10000, 100)

        except:
            return 50  # Default

    def scrape_twitter_moments(self):
        """Scrape Twitter Moments for trending cultural moments"""
        try:
            # Note: This would require Twitter API or web scraping
            # For now, return empty - can be enhanced with proper Twitter scraping
            logger.info("Twitter Moments scraping not yet implemented (requires API)")
            return []

        except Exception as e:
            logger.error(f"Failed to scrape Twitter Moments: {e}")
            return []

    def get_comprehensive_meme_context(self):
        """
        Get comprehensive current meme context from all sources

        Returns:
            Dictionary with categorized context
        """
        logger.info("Gathering comprehensive meme context...")

        context = {
            'memes': [],
            'slang': [],
            'trending_topics': [],
            'cultural_moments': [],
            'scraped_at': datetime.utcnow().isoformat()
        }

        # Gather from all sources
        try:
            # Know Your Meme
            kym_trends = self.scrape_know_your_meme_trending()
            context['memes'].extend(kym_trends)

            # Urban Dictionary
            ud_slang = self.scrape_urban_dictionary_trending()
            context['slang'].extend(ud_slang)

            # Google Trends
            google_trends = self.scrape_google_trends()
            context['trending_topics'].extend(google_trends)

            logger.info("Comprehensive meme context gathered successfully")
            logger.info(f"Total: {len(context['memes'])} memes, {len(context['slang'])} slang, {len(context['trending_topics'])} topics")

        except Exception as e:
            logger.error(f"Error gathering comprehensive context: {e}")

        return context

    def get_meme_context_summary(self):
        """
        Get a text summary of current meme context for LLM

        Returns:
            String summary suitable for LLM context
        """
        context = self.get_comprehensive_meme_context()

        summary_parts = []

        # Add trending memes
        if context['memes']:
            summary_parts.append("TRENDING MEMES:")
            for meme in context['memes'][:10]:
                summary_parts.append(f"- {meme['name']}: {meme['description'][:100]}")

        # Add current slang
        if context['slang']:
            summary_parts.append("\nCURRENT SLANG:")
            for slang in context['slang'][:10]:
                summary_parts.append(f"- {slang['word']}: {slang['definition'][:80]}")

        # Add trending topics
        if context['trending_topics']:
            summary_parts.append("\nTRENDING TOPICS:")
            for topic in context['trending_topics'][:10]:
                summary_parts.append(f"- {topic['topic']} ({topic['traffic']})")

        summary = "\n".join(summary_parts)

        logger.info(f"Generated meme context summary ({len(summary)} chars)")

        return summary
