import anthropic
from anthropic import Anthropic
from openai import OpenAI
import requests
import base64
import os
import tempfile
import logging
from pathlib import Path
from config import Config
import cv2
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultimodalAnalyzer:
    """
    Analyzes images, videos, and audio to understand meme content
    Uses Claude Vision, OpenAI GPT-4V, and audio transcription
    """

    def __init__(self, provider='claude'):
        """
        Initialize multimodal analyzer

        Args:
            provider: 'claude' or 'openai'
        """
        self.provider = provider

        if provider == 'claude':
            if not Config.CLAUDE_API_KEY:
                raise ValueError("CLAUDE_API_KEY not set")
            self.client = Anthropic(api_key=Config.CLAUDE_API_KEY)
            self.model = "claude-3-5-sonnet-20241022"
        elif provider == 'openai':
            if not Config.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set")
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
            self.model = "gpt-4-vision-preview"
        else:
            raise ValueError(f"Unknown provider: {provider}")

        logger.info(f"Multimodal Analyzer initialized with provider: {provider}")

    def analyze_image(self, image_source, context=""):
        """
        Analyze an image to understand its meme content

        Args:
            image_source: URL or local file path to image
            context: Additional context about the image

        Returns:
            Dictionary with analysis results
        """
        try:
            # Get image data
            if image_source.startswith('http'):
                image_data = self._download_image(image_source)
            else:
                image_data = self._load_local_image(image_source)

            # Analyze with vision model
            analysis = self._analyze_image_with_llm(image_data, context)

            logger.info(f"Image analysis complete")
            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze image: {e}")
            return None

    def _download_image(self, url):
        """Download image from URL"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Failed to download image: {e}")
            raise

    def _load_local_image(self, path):
        """Load image from local file"""
        try:
            with open(path, 'rb') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load local image: {e}")
            raise

    def _analyze_image_with_llm(self, image_data, context):
        """Analyze image using vision-enabled LLM"""

        prompt = f"""Analyze this meme image and provide detailed insights.

{f"CONTEXT: {context}" if context else ""}

Analyze:
1. Visual content: What's depicted in the image?
2. Meme format: What meme format/template is this? (e.g., Drake format, distracted boyfriend, etc.)
3. Text content: What text is overlaid on the image?
4. Humor type: What kind of humor is this? (ironic, post-ironic, absurdist, relatable, etc.)
5. Cultural references: What cultural moments, trends, or references does this use?
6. Emotional tone: What emotion or vibe does this convey?
7. Meme potential: How memeable/shareable is this? (0-100 score)
8. Topics/themes: What topics does this relate to?

Return as JSON:
{{
    "visual_description": "detailed description",
    "meme_format": "format name or 'custom'",
    "text_content": ["text line 1", "text line 2"],
    "humor_type": "type of humor",
    "irony_level": "literal/ironic/post-ironic/meta-ironic/absurdist",
    "cultural_references": ["ref1", "ref2"],
    "emotional_tone": "tone description",
    "meme_potential_score": 0-100,
    "topics": ["topic1", "topic2"],
    "why_funny": "explanation of what makes this funny",
    "generation_ideas": "ideas for similar content"
}}"""

        try:
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')

            if self.provider == 'claude':
                # Claude vision API
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/jpeg",
                                        "data": image_base64,
                                    },
                                },
                                {
                                    "type": "text",
                                    "text": prompt
                                }
                            ],
                        }
                    ],
                )
                content = message.content[0].text

            else:  # openai
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_base64}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=1024
                )
                content = response.choices[0].message.content

            # Parse JSON response
            import json
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != 0:
                return json.loads(content[start:end])
            else:
                return {'error': 'Failed to parse response'}

        except Exception as e:
            logger.error(f"Failed to analyze image with LLM: {e}")
            return {'error': str(e)}

    def analyze_video(self, video_source, sample_frames=5):
        """
        Analyze a video by extracting and analyzing key frames

        Args:
            video_source: URL or local path to video
            sample_frames: Number of frames to sample and analyze

        Returns:
            Dictionary with video analysis
        """
        try:
            # Download video if URL
            if video_source.startswith('http'):
                video_path = self._download_video(video_source)
            else:
                video_path = video_source

            # Extract key frames
            frames = self._extract_video_frames(video_path, sample_frames)

            # Analyze each frame
            frame_analyses = []
            for i, frame_data in enumerate(frames):
                analysis = self._analyze_image_with_llm(
                    frame_data,
                    context=f"Frame {i+1}/{len(frames)} from a meme video"
                )
                frame_analyses.append(analysis)

            # Synthesize overall video analysis
            video_analysis = self._synthesize_video_analysis(frame_analyses)

            # Clean up temp file if downloaded
            if video_source.startswith('http'):
                os.remove(video_path)

            logger.info("Video analysis complete")
            return video_analysis

        except Exception as e:
            logger.error(f"Failed to analyze video: {e}")
            return None

    def _download_video(self, url):
        """Download video to temp file"""
        try:
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()

            # Save to temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            temp_file.close()

            return temp_file.name

        except Exception as e:
            logger.error(f"Failed to download video: {e}")
            raise

    def _extract_video_frames(self, video_path, num_frames=5):
        """Extract evenly spaced frames from video"""
        try:
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            if total_frames == 0:
                raise ValueError("Video has no frames")

            # Calculate frame indices to extract
            frame_indices = [int(i * total_frames / num_frames) for i in range(num_frames)]

            frames = []
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()

                if ret:
                    # Convert frame to JPEG bytes
                    _, buffer = cv2.imencode('.jpg', frame)
                    frames.append(buffer.tobytes())

            cap.release()

            logger.info(f"Extracted {len(frames)} frames from video")
            return frames

        except Exception as e:
            logger.error(f"Failed to extract video frames: {e}")
            return []

    def _synthesize_video_analysis(self, frame_analyses):
        """Synthesize analysis from multiple frames into overall video analysis"""
        if not frame_analyses:
            return {'error': 'No frame analyses available'}

        # Aggregate common themes
        all_topics = []
        all_references = []
        humor_types = []
        irony_levels = []

        for analysis in frame_analyses:
            if isinstance(analysis, dict):
                all_topics.extend(analysis.get('topics', []))
                all_references.extend(analysis.get('cultural_references', []))
                if 'humor_type' in analysis:
                    humor_types.append(analysis['humor_type'])
                if 'irony_level' in analysis:
                    irony_levels.append(analysis['irony_level'])

        # Get most common values
        from collections import Counter
        topic_counts = Counter(all_topics)
        ref_counts = Counter(all_references)

        return {
            'type': 'video',
            'num_frames_analyzed': len(frame_analyses),
            'primary_topics': [topic for topic, _ in topic_counts.most_common(5)],
            'cultural_references': [ref for ref, _ in ref_counts.most_common(5)],
            'dominant_humor_type': Counter(humor_types).most_common(1)[0][0] if humor_types else 'unknown',
            'dominant_irony_level': Counter(irony_levels).most_common(1)[0][0] if irony_levels else 'unknown',
            'frame_analyses': frame_analyses
        }

    def analyze_audio(self, audio_source):
        """
        Analyze audio content (transcribe and analyze)

        Args:
            audio_source: URL or local path to audio file

        Returns:
            Dictionary with audio analysis
        """
        try:
            # Download audio if URL
            if audio_source.startswith('http'):
                audio_path = self._download_audio(audio_source)
            else:
                audio_path = audio_source

            # Transcribe audio
            transcription = self._transcribe_audio(audio_path)

            # Analyze transcription for meme content
            analysis = self._analyze_audio_content(transcription)

            # Clean up temp file if downloaded
            if audio_source.startswith('http'):
                os.remove(audio_path)

            logger.info("Audio analysis complete")
            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze audio: {e}")
            return None

    def _download_audio(self, url):
        """Download audio to temp file"""
        try:
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()

            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            temp_file.close()

            return temp_file.name

        except Exception as e:
            logger.error(f"Failed to download audio: {e}")
            raise

    def _transcribe_audio(self, audio_path):
        """Transcribe audio using OpenAI Whisper"""
        try:
            if self.provider == 'openai':
                # Use OpenAI Whisper
                with open(audio_path, 'rb') as audio_file:
                    transcription = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                return transcription.text
            else:
                # For Claude, we'd need to use a separate Whisper API or service
                # For now, return placeholder
                logger.warning("Audio transcription not available with Claude provider")
                return ""

        except Exception as e:
            logger.error(f"Failed to transcribe audio: {e}")
            return ""

    def _analyze_audio_content(self, transcription):
        """Analyze transcribed audio content for meme potential"""
        if not transcription:
            return {'error': 'No transcription available'}

        prompt = f"""Analyze this audio transcription from a potential meme:

TRANSCRIPTION: "{transcription}"

Analyze:
1. Is this from a known meme sound/audio trend?
2. What's the tone/vibe of this audio?
3. What topics/themes does it relate to?
4. Meme potential score (0-100)
5. How could this be used in meme content?

Return as JSON:
{{
    "is_known_meme": true/false,
    "meme_name": "name if known",
    "tone": "tone description",
    "topics": ["topic1", "topic2"],
    "meme_potential_score": 0-100,
    "usage_ideas": "how to use this in memes",
    "transcription": "the transcription"
}}"""

        try:
            if self.provider == 'claude':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=512,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
            else:
                response = self.client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.choices[0].message.content

            # Parse JSON
            import json
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != 0:
                return json.loads(content[start:end])
            else:
                return {'error': 'Failed to parse response', 'transcription': transcription}

        except Exception as e:
            logger.error(f"Failed to analyze audio content: {e}")
            return {'error': str(e), 'transcription': transcription}
