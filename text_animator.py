# text_animator.py

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import ImageSequenceClip
import tempfile
import os

def create_frame(text, color, background, font_size, width=800, height=400):
    """Create a single frame with text"""
    img = Image.new('RGB', (width, height), background)
    draw = ImageDraw.Draw(img)
    
    # Use default font since custom fonts might cause issues
    font = ImageFont.load_default()
    
    # Center the text
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    draw.text((x, y), text, fill=color, font=font)
    return np.array(img)

def create_animation(text, style, fps=20, duration=3):
    """Create animation frames"""
    frames = []
    n_frames = int(fps * duration)
    
    if style == "simple":
        # Simple fade-in effect
        for i in range(n_frames):
            opacity = min(255, int(255 * i / (n_frames/2)))
            color = f"rgb({opacity},{opacity},{opacity})"
            frame = create_frame(text, color, "black", 64)
            frames.append(frame)
            
    return frames

def main():
    st.title("Text Animator")
    
    # User inputs
    text_input = st.text_input("Enter your text", "Hello World!")
    
    if st.button("Generate Animation"):
        if text_input:
            with st.spinner("Creating animation..."):
                try:
                    # Generate frames
                    frames = create_animation(text_input, "simple")
                    
                    # Create video
                    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmpfile:
                        clip = ImageSequenceClip(frames, fps=20)
                        clip.write_videofile(
                            tmpfile.name,
                            fps=20,
                            codec='libx264',
                            audio=False,
                            verbose=False,
                            logger=None
                        )
                        
                        # Read video file
                        with open(tmpfile.name, 'rb') as f:
                            video_bytes = f.read()
                        
                        # Cleanup
                        clip.close()
                    
                    if os.path.exists(tmpfile.name):
                        os.unlink(tmpfile.name)
                    
                    # Display video
                    st.video(video_bytes)
                    
                    # Download button
                    st.download_button(
                        "Download Video",
                        video_bytes,
                        "animation.mp4",
                        "video/mp4"
                    )
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please enter some text!")

if __name__ == "__main__":
    main()
