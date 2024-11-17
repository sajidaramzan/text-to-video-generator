import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import VideoFileClip, ImageSequenceClip, CompositeVideoClip, ColorClip, TextClip
import tempfile
import os
from pathlib import Path
import time
import random
from typing import List, Tuple, Dict
import json
import base64
from dataclasses import dataclass
import io

@dataclass
class AnimationStyle:
    name: str
    font_size: int
    colors: List[str]
    background: str
    animation_type: str
    duration: float

class TextAnimator:
    def __init__(self):
        self.styles = {
            'neon': AnimationStyle(
                'Neon Glow',
                72,
                ['#FF1493', '#00FF00', '#FF4500'],
                '#000000',
                'glow',
                0.5
            ),
            'typewriter': AnimationStyle(
                'Typewriter',
                64,
                ['#FFFFFF'],
                '#000000',
                'type',
                0.3
            ),
            'bounce': AnimationStyle(
                'Bouncing Text',
                80,
                ['#FFD700'],
                '#000033',
                'bounce',
                0.4
            ),
            'matrix': AnimationStyle(
                'Matrix Rain',
                56,
                ['#00FF00'],
                '#000000',
                'matrix',
                0.6
            ),
            'rainbow': AnimationStyle(
                'Rainbow Wave',
                70,
                ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF', '#4B0082', '#9400D3'],
                '#FFFFFF',
                'rainbow',
                0.4
            )
        }
        
    def create_base_frame(self, text: str, width: int, height: int, style: AnimationStyle) -> Image.Image:
        """Create a base frame with the given text and style"""
        img = Image.new('RGB', (width, height), style.background)
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype('arial.ttf', style.font_size)
        except:
            font = ImageFont.load_default()
            
        # Calculate text position to center it
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        return img, draw, font, (x, y)

    def create_frames(self, text: str, style: str, fps: int = 30, duration: float = 3.0) -> List[np.ndarray]:
        """Create animation frames based on the selected style"""
        width, height = 800, 400
        frames = []
        style_config = self.styles[style]
        
        if style == 'typewriter':
            frames.extend(self.create_typewriter_effect(text, width, height, style_config, fps, duration))
        elif style == 'bounce':
            frames.extend(self.create_bounce_effect(text, width, height, style_config, fps, duration))
        elif style == 'matrix':
            frames.extend(self.create_matrix_effect(text, width, height, style_config, fps, duration))
        elif style == 'rainbow':
            frames.extend(self.create_rainbow_effect(text, width, height, style_config, fps, duration))
        elif style == 'neon':
            frames.extend(self.create_neon_effect(text, width, height, style_config, fps, duration))
            
        return frames

    def create_typewriter_effect(self, text: str, width: int, height: int, 
                               style: AnimationStyle, fps: int, duration: float) -> List[np.ndarray]:
        frames = []
        total_frames = int(fps * duration)
        chars_per_frame = max(1, len(text) // total_frames)
        
        for i in range(total_frames):
            img, draw, font, (x, y) = self.create_base_frame(text, width, height, style)
            visible_chars = text[:int(i * chars_per_frame)]
            draw.text((x, y), visible_chars, font=font, fill=style.colors[0])
            frames.append(np.array(img))
            
        return frames

    def create_bounce_effect(self, text: str, width: int, height: int, 
                           style: AnimationStyle, fps: int, duration: float) -> List[np.ndarray]:
        frames = []
        total_frames = int(fps * duration)
        
        for i in range(total_frames):
            img, draw, font, (x, y) = self.create_base_frame(text, width, height, style)
            offset = int(20 * np.sin(2 * np.pi * i / fps))
            draw.text((x, y + offset), text, font=font, fill=style.colors[0])
            frames.append(np.array(img))
            
        return frames

    def create_matrix_effect(self, text: str, width: int, height: int, 
                           style: AnimationStyle, fps: int, duration: float) -> List[np.ndarray]:
        frames = []
        total_frames = int(fps * duration)
        matrix_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*"
        
        for i in range(total_frames):
            img, draw, font, (x, y) = self.create_base_frame(text, width, height, style)
            
            # Create matrix rain effect
            for col in range(0, width, 20):
                for row in range(0, height, 30):
                    if random.random() < 0.1:
                        char = random.choice(matrix_chars)
                        opacity = int(255 * (1 - row/height))
                        color = f"#{0:02x}{opacity:02x}{0:02x}"
                        draw.text((col, row), char, font=font, fill=color)
                        
            # Draw main text
            draw.text((x, y), text, font=font, fill=style.colors[0])
            frames.append(np.array(img))
            
        return frames

    def create_rainbow_effect(self, text: str, width: int, height: int, 
                            style: AnimationStyle, fps: int, duration: float) -> List[np.ndarray]:
        frames = []
        total_frames = int(fps * duration)
        
        for i in range(total_frames):
            img, draw, font, (x, y) = self.create_base_frame(text, width, height, style)
            
            # Create rainbow wave effect
            for j, char in enumerate(text):
                color_idx = (i + j) % len(style.colors)
                char_width = draw.textlength(text[:j], font=font)
                draw.text((x + char_width, y), char, font=font, fill=style.colors[color_idx])
                
            frames.append(np.array(img))
            
        return frames

    def create_neon_effect(self, text: str, width: int, height: int, 
                          style: AnimationStyle, fps: int, duration: float) -> List[np.ndarray]:
        frames = []
        total_frames = int(fps * duration)
        
        for i in range(total_frames):
            img, draw, font, (x, y) = self.create_base_frame(text, width, height, style)
            
            # Create glow effect
            glow_color = style.colors[i % len(style.colors)]
            for offset in range(3, 0, -1):
                draw.text((x-offset, y), text, font=font, fill=glow_color)
                draw.text((x+offset, y), text, font=font, fill=glow_color)
                draw.text((x, y-offset), text, font=font, fill=glow_color)
                draw.text((x, y+offset), text, font=font, fill=glow_color)
                
            # Draw main text
            draw.text((x, y), text, font=font, fill='#FFFFFF')
            frames.append(np.array(img))
            
        return frames

def add_audio_background(video_path: str, audio_style: str) -> str:
    """Add background audio to the video"""
    # This is a placeholder - you would need to implement actual audio handling
    return video_path

@st.cache_data
def get_font_list() -> List[str]:
    """Get list of available fonts"""
    return ['Arial', 'Times New Roman', 'Courier New']

def main():
    st.set_page_config(
        page_title="Text to Video Generator",
        page_icon="🎬",
        layout="wide"
    )

    st.title("🎬 Advanced Text to Video Generator")
    st.markdown("Transform your text into stunning animated videos!")

    # Initialize session state
    if 'history' not in st.session_state:
        st.session_state.history = []

    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Create Video", "History", "Settings"])

    with tab1:
        col1, col2 = st.columns([1, 2])

        with col1:
            # Text input and style selection
            text_input = st.text_area(
                "Enter your text",
                height=100,
                placeholder="Type something creative..."
            )

            style = st.selectbox(
                "Animation Style",
                ['typewriter', 'bounce', 'matrix', 'rainbow', 'neon']
            )

            # Advanced settings
            with st.expander("Advanced Settings"):
                col_left, col_right = st.columns(2)

                with col_left:
                    fps = st.slider("Frames per second", 15, 60, 30)
                    duration = st.slider("Duration (seconds)", 1, 10, 3)

                with col_right:
                    resolution = st.selectbox(
                        "Resolution",
                        ['720p', '1080p'],
                        index=0
                    )
                    
                    quality = st.select_slider(
                        "Quality",
                        options=['Low', 'Medium', 'High'],
                        value='Medium'
                    )

            # Audio settings
            with st.expander("Audio Settings"):
                add_audio = st.checkbox("Add Background Audio")
                if add_audio:
                    audio_style = st.selectbox(
                        "Audio Style",
                        ['None', 'Upbeat', 'Calm', 'Corporate', 'Dramatic']
                    )

        with col2:
            # Preview and Generation
            if text_input:
                if st.button("Generate Video", type="primary"):
                    with st.spinner("Creating your video..."):
                        try:
                            # Initialize animator
                            animator = TextAnimator()
                            
                            # Generate frames
                            frames = animator.create_frames(
                                text_input,
                                style,
                                fps=fps,
                                duration=duration
                            )
                            
                            # Create video
                            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
                                clip = ImageSequenceClip(frames, fps=fps)
                                clip.write_videofile(
                                    tmp_file.name,
                                    fps=fps,
                                    codec='libx264',
                                    audio=False,
                                    verbose=False,
                                    logger=None
                                )
                                
                                # Add audio if selected
                                if add_audio and audio_style != 'None':
                                    tmp_file.name = add_audio_background(tmp_file.name, audio_style)
                                
                                # Read the video file
                                with open(tmp_file.name, 'rb') as f:
                                    video_bytes = f.read()
                                
                                # Clean up
                                os.unlink(tmp_file.name)
                            
                            # Add to history
                            st.session_state.history.append({
                                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                                'text': text_input,
                                'style': style,
                                'video': video_bytes
                            })
                            
                            # Display video and download button
                            st.video(video_bytes)
                            st.download_button(
                                "Download Video",
                                video_bytes,
                                f"text_animation_{style}.mp4",
                                "video/mp4"
                            )
                            
                        except Exception as e:
                            st.error(f"An error occurred: {str(e)}")
            else:
                st.info("Enter some text to generate a video!")

    with tab2:
        # Display history
        if st.session_state.history:
            for idx, item in enumerate(reversed(st.session_state.history)):
                with st.expander(
                    f"Video {len(st.session_state.history)-idx}: {item['style']} "
                    f"({item['timestamp']})"
                ):
                    st.text(f"Text: {item['text']}")
                    st.video(item['video'])
                    st.download_button(
                        f"Download Video {len(st.session_state.history)-idx}",
                        item['video'],
                        f"video_{item['style']}_{idx}.mp4",
                        "video/mp4"
                    )
        else:
            st.info("No videos generated yet. Create your first video in the 'Create Video' tab!")

    with tab3:
        st.header("⚙️ Settings")
        
        # Cache settings
        cache_size = st.slider(
            "History Size (number of videos to keep)",
            1, 20, 10
        )
        
        # Export/Import settings
        if st.button("Export Settings"):
            settings = {
                'cache_size': cache_size,
                'default_fps': fps,
                'default_duration': duration
            }
            settings_str = json.dumps(settings)
            b64 = base64.b64encode(settings_str.encode()).decode()
            st.download_button(
                "Download Settings",
                b64,
                "settings.json",
                "application/json"
            )
        
        uploaded_settings = st.file_uploader(
            "Import Settings",
            type=['json']
        )
        if uploaded_settings:
            try:
                settings = json.load(uploaded_settings)
                st.success("Settings imported successfully!")
            except Exception as e:
                st.error(f"Error importing settings: {str(e)}")

    # Instructions
    with st.expander("How to Use"):
        st.markdown("""
        ### Instructions
        1. Enter your text in the text area
        2. Choose an animation style
        3. Adjust advanced settings if desired
        4. Click 'Generate Video' to create your animation
        5. Download the result or browse your video history
        
        ### Available Styles
        - **Typewriter**: Classic typewriter effect
        - **Bounce**: Bouncing text animation
        - **Matrix**: Matrix-style digital rain effect
        - **Rainbow**: Colorful rainbow wave
        - **Neon**: Glowing neon text effect
        
       ### Tips
        - Keep text relatively short for best results
        - Higher FPS creates smoother animations but takes longer to process
        - Experiment with different styles and settings to find what works best
        - Use the preview feature to test before generating final videos
        - Consider the background audio style that best matches your text's mood
        """)

    # Footer
    st.markdown("""
    ---
    Made with ❤️ by Your App Name | [Report Bug](mailto:support@yourapp.com) | [Feature Request](mailto:features@yourapp.com)
    """)

def create_error_message(error_type: str, details: str = "") -> str:
    """Create standardized error messages"""
    error_messages = {
        "text_too_long": "Text is too long. Please keep it under 100 characters for optimal performance.",
        "invalid_style": "Selected animation style is not supported.",
        "processing_error": "An error occurred while processing your video.",
        "file_error": "Error handling video file.",
        "memory_error": "Not enough memory to process video."
    }
    return f"Error: {error_messages.get(error_type, 'Unknown error occurred.')} {details}"

class VideoProcessor:
    """Handle video processing and optimization"""
    
    def __init__(self, quality: str = 'Medium'):
        self.quality_settings = {
            'Low': {'bitrate': '1000k', 'resolution': (640, 360)},
            'Medium': {'bitrate': '2000k', 'resolution': (1280, 720)},
            'High': {'bitrate': '4000k', 'resolution': (1920, 1080)}
        }
        self.quality = quality

    def optimize_video(self, video_path: str) -> str:
        """Optimize video based on quality settings"""
        settings = self.quality_settings[self.quality]
        output_path = f"{video_path}_optimized.mp4"
        
        clip = VideoFileClip(video_path)
        clip = clip.resize(settings['resolution'])
        
        clip.write_videofile(
            output_path,
            bitrate=settings['bitrate'],
            codec='libx264',
            audio=False,
            verbose=False,
            logger=None
        )
        
        return output_path

class AudioManager:
    """Handle background audio processing"""
    
    def __init__(self):
        self.audio_tracks = {
            'Upbeat': 'assets/audio/upbeat.mp3',
            'Calm': 'assets/audio/calm.mp3',
            'Corporate': 'assets/audio/corporate.mp3',
            'Dramatic': 'assets/audio/dramatic.mp3'
        }

    def add_background_music(self, video_path: str, audio_style: str) -> str:
        """Add background music to video"""
        if audio_style not in self.audio_tracks:
            return video_path
            
        output_path = f"{video_path}_with_audio.mp4"
        video = VideoFileClip(video_path)
        
        # Load audio and loop it to match video duration
        audio = VideoFileClip(self.audio_tracks[audio_style]).audio
        audio = audio.loop(duration=video.duration)
        
        # Reduce audio volume
        audio = audio.volumex(0.3)
        
        # Combine video and audio
        final_video = video.set_audio(audio)
        final_video.write_videofile(output_path)
        
        return output_path

class CacheManager:
    """Handle caching and history management"""
    
    def __init__(self, max_size: int = 10):
        self.max_size = max_size
        
    def cleanup_old_entries(self):
        """Remove oldest entries when cache is full"""
        if len(st.session_state.history) > self.max_size:
            st.session_state.history = st.session_state.history[-self.max_size:]
            
    def clear_cache(self):
        """Clear all cached videos"""
        st.session_state.history = []
        
    def export_history(self) -> str:
        """Export history as JSON"""
        history_data = []
        for item in st.session_state.history:
            history_data.append({
                'timestamp': item['timestamp'],
                'text': item['text'],
                'style': item['style']
            })
        return json.dumps(history_data)

class SettingsManager:
    """Handle application settings"""
    
    @staticmethod
    def save_settings(settings: Dict) -> str:
        """Save settings to JSON string"""
        return json.dumps(settings)
        
    @staticmethod
    def load_settings(settings_str: str) -> Dict:
        """Load settings from JSON string"""
        return json.loads(settings_str)
        
    @staticmethod
    def validate_settings(settings: Dict) -> Tuple[bool, str]:
        """Validate settings dictionary"""
        required_keys = {'cache_size', 'default_fps', 'default_duration'}
        
        if not all(key in settings for key in required_keys):
            return False, "Missing required settings"
            
        if not (1 <= settings['cache_size'] <= 20):
            return False, "Cache size must be between 1 and 20"
            
        if not (15 <= settings['default_fps'] <= 60):
            return False, "FPS must be between 15 and 60"
            
        if not (1 <= settings['default_duration'] <= 10):
            return False, "Duration must be between 1 and 10 seconds"
            
        return True, "Settings valid"

if __name__ == "__main__":
    main()
