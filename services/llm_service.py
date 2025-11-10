from anthropic import Anthropic
from openai import OpenAI
from config import Config
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMService:
    """
    Handles LLM interactions for meme generation and understanding
    Supports both Claude (Anthropic) and GPT (OpenAI)
    """

    def __init__(self, provider='claude'):
        """
        Initialize LLM service

        Args:
            provider: 'claude' or 'openai'
        """
        self.provider = provider

        if provider == 'claude':
            if not Config.CLAUDE_API_KEY:
                raise ValueError("CLAUDE_API_KEY not set")
            self.client = Anthropic(api_key=Config.CLAUDE_API_KEY)
            self.model = "claude-3-sonnet-20240229"
        elif provider == 'openai':
            if not Config.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set")
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
            self.model = "gpt-4-turbo-preview"
        else:
            raise ValueError(f"Unknown provider: {provider}")

        logger.info(f"LLM Service initialized with provider: {provider}")

    def generate_meme_content(self, context, meme_format=None, irony_level='post-ironic'):
        """
        Generate meme content based on context and parameters

        Args:
            context: Current trend/topic context
            meme_format: Specific meme format to use (optional)
            irony_level: Level of irony (literal, ironic, post-ironic, meta-ironic, absurdist)

        Returns:
            Dictionary with meme text and metadata
        """

        system_prompt = self._get_meme_generation_system_prompt()
        user_prompt = self._build_generation_prompt(context, meme_format, irony_level)

        try:
            if self.provider == 'claude':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ]
                )
                content = response.content[0].text
            else:  # openai
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                content = response.choices[0].message.content

            # Parse the response
            result = self._parse_meme_response(content)
            logger.info(f"Generated meme content: {result['text'][:50]}...")

            return result

        except Exception as e:
            logger.error(f"Failed to generate meme content: {e}")
            raise

    def _get_meme_generation_system_prompt(self):
        """System prompt that teaches the LLM about meme culture"""
        return """You are an expert in internet meme culture, specifically focused on Gen Z and post-ironic humor.

Key principles of modern meme culture:

1. POST-IRONY: Sincerity and irony blend together. Something can be simultaneously genuine and mocking.

2. ABSURDISM: Random, nonsensical elements that create humor through unexpectedness.

3. META-HUMOR: Self-aware jokes about memes themselves, internet culture, or the act of memeing.

4. LAYERED REFERENCES: Memes that reference other memes, creating inside jokes for chronically online users.

5. FORMAT SUBVERSION: Taking established meme formats and using them in unexpected ways.

6. BREVITY & IMPACT: Short, punchy text. Often lowercase. Sometimes no punctuation. Maximum impact.

7. CULTURAL AWARENESS: References to:
   - Current events and trending topics
   - Internet micro-cultures (Discord, Twitter, Reddit, TikTok)
   - Gaming culture
   - Relatability (anxiety, being broke, procrastination)
   - Existential dread presented humorously

8. AUTHENTICITY: Don't try too hard. Forced memes die quickly. Natural, flowing humor works best.

Examples of post-ironic approaches:
- "me when [absurd relatable situation]"
- Intentional misspellings for comedic effect
- Overly specific scenarios that are somehow universal
- Self-deprecating but with confidence
- Combining high and low culture

Your task is to generate meme content that feels native to internet culture, not like a corporate brand trying to be relatable."""

    def _build_generation_prompt(self, context, meme_format, irony_level):
        """Build the user prompt for meme generation"""
        prompt = f"""Generate a meme tweet for the following context:

CONTEXT: {context}

REQUIREMENTS:
- Irony level: {irony_level}
- Maximum length: 280 characters
- Must be funny and engaging
- Should feel authentic to internet culture
- Avoid corporate/brand voice"""

        if meme_format:
            prompt += f"\n- Use meme format: {meme_format}"

        prompt += """

Return your response as JSON with this structure:
{
    "text": "the meme tweet text",
    "format": "meme format used (if any)",
    "irony_level": "the irony level",
    "topics": ["topic1", "topic2"],
    "explanation": "brief explanation of why this is funny/effective"
}"""

        return prompt

    def _parse_meme_response(self, content):
        """Parse LLM response into structured format"""
        try:
            # Try to extract JSON from response
            start = content.find('{')
            end = content.rfind('}') + 1

            if start != -1 and end != 0:
                json_str = content[start:end]
                result = json.loads(json_str)
                return result
            else:
                # Fallback if no JSON found
                return {
                    'text': content.strip(),
                    'format': None,
                    'irony_level': 'unknown',
                    'topics': [],
                    'explanation': 'Generated without structured format'
                }
        except Exception as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            return {
                'text': content.strip(),
                'format': None,
                'irony_level': 'unknown',
                'topics': [],
                'explanation': 'Parse error'
            }

    def analyze_meme_trend(self, trend_data):
        """
        Analyze whether a trend has meme potential

        Args:
            trend_data: Information about a trending topic

        Returns:
            Dictionary with analysis and meme_worthy score
        """

        prompt = f"""Analyze this trending topic for meme potential:

TREND: {trend_data.get('name', '')}
CONTEXT: {trend_data.get('description', 'No description')}
VOLUME: {trend_data.get('volume', 'Unknown')} tweets

Evaluate:
1. Is this meme-worthy? (yes/no and why)
2. What irony level would work best?
3. What meme formats could work?
4. What angle/take would be funniest?
5. Meme potential score (0-100)

Return as JSON:
{{
    "meme_worthy": true/false,
    "score": 0-100,
    "recommended_irony": "level",
    "suggested_formats": ["format1", "format2"],
    "angle": "what approach to take",
    "reasoning": "brief explanation"
}}"""

        try:
            if self.provider == 'claude':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=512,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                content = response.content[0].text
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                content = response.choices[0].message.content

            # Parse JSON response
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != 0:
                return json.loads(content[start:end])
            else:
                return {'meme_worthy': False, 'score': 0}

        except Exception as e:
            logger.error(f"Failed to analyze meme trend: {e}")
            return {'meme_worthy': False, 'score': 0}

    def evaluate_generated_meme(self, meme_text):
        """
        Self-evaluation of generated meme before posting

        Args:
            meme_text: The generated meme text

        Returns:
            Dictionary with quality score and feedback
        """

        prompt = f"""Evaluate this meme tweet for quality:

MEME: "{meme_text}"

Rate on:
1. Humor (0-10)
2. Authenticity (feels native to internet culture?) (0-10)
3. Potential engagement (0-10)
4. Risks (anything potentially offensive/problematic?)

Return as JSON:
{{
    "humor_score": 0-10,
    "authenticity_score": 0-10,
    "engagement_score": 0-10,
    "overall_score": 0-10,
    "should_post": true/false,
    "risks": "any concerns",
    "feedback": "brief feedback"
}}"""

        try:
            if self.provider == 'claude':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=512,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                content = response.content[0].text
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                content = response.choices[0].message.content

            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != 0:
                return json.loads(content[start:end])
            else:
                return {'should_post': True, 'overall_score': 5}

        except Exception as e:
            logger.error(f"Failed to evaluate meme: {e}")
            return {'should_post': True, 'overall_score': 5}
