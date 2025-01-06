"""Streamlit web interface for the social media content generation agent."""

import asyncio
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from social_media_agent import (
    ContentPreferences,
    generate_social_posts,
    save_posts_to_markdown,
    DEFAULT_AUDIENCE,
    DEFAULT_TONE,
)

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Social Media Content Generator",
    page_icon="🚀",
    layout="wide",
)

# Platform mapping between display names and internal names
PLATFORM_MAPPING = {
    "Twitter (X)": "twitter",
    "LinkedIn": "linkedin",
    "Facebook": "facebook",
    "Instagram": "instagram"
}

PLATFORM_LIMITS = {
    "Twitter (X)": "280 characters",
    "LinkedIn": "3,000 characters",
    "Facebook": "63,206 characters",
    "Instagram": "2,200 characters"
}


def get_display_name(platform: str) -> str:
    """Get the display name for a platform from its internal name."""
    for display_name, internal_name in PLATFORM_MAPPING.items():
        if internal_name == platform:
            return display_name
    return platform.title()


def get_character_limit(platform: str) -> int:
    """Get the character limit for a platform."""
    limit_str = PLATFORM_LIMITS[get_display_name(platform)]
    return int(limit_str.split()[0].replace(",", ""))


def main():
    # Header
    st.title("🚀 Social Media Content Generator")
    st.markdown("""
    Generate platform-optimized social media posts from any website URL.
    This tool uses AI to create engaging content tailored for different social media platforms.
    """)

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        # URL input
        url = st.text_input(
            "Website URL",
            placeholder="https://example.com",
            help="Enter the URL of the website you want to create posts for"
        )

        # Content preferences
        st.subheader("Content Preferences")
        audience = st.text_input(
            "Target Audience",
            value=DEFAULT_AUDIENCE,
            help="Describe your target audience"
        )
        tone = st.text_input(
            "Content Tone",
            value=DEFAULT_TONE,
            help="Specify the desired tone of voice"
        )

    with col2:
        st.subheader("Platform Selection")
        selected_platforms = {}
        for display_name, limit in PLATFORM_LIMITS.items():
            selected_platforms[PLATFORM_MAPPING[display_name]] = st.checkbox(
                f"{display_name} ({limit})",
                value=True
            )

    # Generate button
    if st.button("Generate Posts", type="primary"):
        if not url:
            st.error("Please enter a website URL")
            return

        if not any(selected_platforms.values()):
            st.error("Please select at least one platform")
            return

        try:
            with st.spinner("Generating social media posts..."):
                # Create preferences object
                preferences = ContentPreferences(
                    audience=audience,
                    tone=tone
                )

                # Generate posts
                posts = asyncio.run(generate_social_posts(url, preferences))

                # Save to markdown
                output_file = save_posts_to_markdown(url, preferences, posts)

                # Display results in tabs
                st.success(
                    f"Generated posts have been saved to: {output_file}")

                # Create tabs using display names
                tabs = st.tabs([get_display_name(p.platform) for p in posts])
                for tab, post in zip(tabs, posts):
                    with tab:
                        st.text_area(
                            "Content",
                            value=post.content,
                            height=150,
                            help="Copy this content to your clipboard",
                            key=f"content_{post.platform}"
                        )
                        st.markdown("**Hashtags:**")
                        st.markdown(
                            " ".join(f"#{tag}" for tag in post.hashtags))

                        # Character count
                        char_count = len(post.content)
                        char_limit = get_character_limit(post.platform)
                        st.progress(min(1.0, char_count / char_limit))
                        st.caption(
                            f"Character count: {char_count} / {char_limit}")

                # Download button for markdown file
                with open(output_file, 'r') as f:
                    st.download_button(
                        label="Download Markdown File",
                        data=f.read(),
                        file_name=output_file.name,
                        mime="text/markdown"
                    )

        except Exception as e:
            st.error(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
