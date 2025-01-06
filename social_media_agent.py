"""Social media content generation agent that creates platform-specific posts from website content.

Run with:
    uv run -m examples.social_media_agent
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Literal, Dict, Any, Optional
from urllib.parse import urlparse

from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field, HttpUrl
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from pydantic_ai import Agent, RunContext
import logfire
from dotenv import load_dotenv

load_dotenv()
logfire.configure(send_to_logfire='if-token-present')

# Platform-specific constraints
PLATFORM_LIMITS = {
    'twitter': 280,
    'linkedin': 3000,
    'facebook': 63206,
    'instagram': 2200,
}

# Default content settings
DEFAULT_AUDIENCE = "general professional audience"
DEFAULT_TONE = "informative and engaging"

# Output directory for saved posts
OUTPUTS_DIR = Path("outputs")


def save_posts_to_markdown(url: str, preferences: ContentPreferences, posts: List[SocialMediaPost]) -> Path:
    """Save generated posts to a markdown file.

    Args:
        url: The source URL
        preferences: Content generation preferences
        posts: List of generated social media posts

    Returns:
        Path to the saved markdown file
    """
    # Create outputs directory if it doesn't exist
    OUTPUTS_DIR.mkdir(exist_ok=True)

    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"social_media_posts_{timestamp}.md"
    filepath = OUTPUTS_DIR / filename

    # Generate markdown content
    content = [
        "# Generated Social Media Posts\n",
        f"**Source URL:** {url}\n",
        f"**Generated at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        f"**Target Audience:** {preferences.audience}",
        f"**Content Tone:** {preferences.tone}\n",
        "## Generated Posts\n"
    ]

    # Add each platform's posts
    for post in posts:
        content.extend([
            f"### {post.platform.title()}",
            "```",
            post.content,
            "```\n",
            "**Hashtags:**",
            " ".join(f"#{tag}" for tag in post.hashtags),
            "\n"
        ])

    # Write to file
    filepath.write_text("\n".join(content))
    return filepath


class ContentPreferences(BaseModel):
    """User preferences for content generation."""
    audience: str = Field(description="Target audience for the content")
    tone: str = Field(description="Desired tone of voice for the content")


class WebsiteContent(BaseModel):
    """Extracted content from a website."""
    title: str = Field(description="The title of the webpage")
    description: str = Field(
        description="Meta description or summary of the webpage")
    main_content: str = Field(
        description="Main content extracted from the webpage")
    url: HttpUrl = Field(description="The original URL of the webpage")


class SocialMediaPost(BaseModel):
    """A social media post optimized for a specific platform."""
    platform: Literal['twitter', 'linkedin', 'facebook', 'instagram']
    content: str = Field(description="The main content of the post")
    hashtags: List[str] = Field(
        description="Relevant hashtags for the post", max_items=5)


class FirecrawlMetadata(BaseModel):
    """Metadata from FireCrawl response."""
    url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    language: Optional[str] = None
    author: Optional[str] = None
    sourceURL: Optional[str] = None
    statusCode: Optional[int] = None
    publishedTime: Optional[str] = None
    modifiedTime: Optional[str] = None
    ogImage: Optional[str] = None
    ogDescription: Optional[str] = None


class FirecrawlResponse(BaseModel):
    """FireCrawl API response structure based on actual response."""
    markdown: str
    metadata: FirecrawlMetadata


@dataclass
class Deps:
    firecrawl: FirecrawlApp
    website_content: WebsiteContent | None = None
    preferences: ContentPreferences | None = None


content_extraction_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=Deps,
    result_type=WebsiteContent,
    system_prompt="""
    You are a content extraction specialist. Your job is to analyze webpage content and extract the most important information.
    Focus on the main message, value proposition, and key details that would be interesting for social media audiences.
    
    When you receive a URL, you should:
    1. Use the fetch_webpage tool to get the content
    2. Create a WebsiteContent object with the extracted information
    3. Make sure to include a title, description, and main content
    4. The URL should be the original URL provided
    """
)

post_generation_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=Deps,
    result_type=List[SocialMediaPost],
    system_prompt="""
    You are a social media content expert. Your job is to create engaging, platform-optimized posts from website content.
    Follow these guidelines:
    1. Each post should be tailored to the platform's style and character limits
    2. Include relevant hashtags (max 5) that will increase visibility
    3. Add a compelling call-to-action with the website URL
    4. Maintain the brand's voice while adapting to each platform's unique style
    5. If available, reference the author or publication date to add credibility
    6. Adapt the content to match the specified target audience and tone
    7. If no audience or tone is specified, use a general professional audience and informative tone
    """
)


@content_extraction_agent.tool
async def fetch_webpage(ctx: RunContext[Deps], url: str) -> WebsiteContent:
    """Fetch and extract content from a webpage using FireCrawl.

    Args:
        ctx: The context containing the FireCrawl client
        url: The URL to fetch content from
    Returns:
        WebsiteContent object containing the extracted information
    """
    # Use FireCrawl to scrape the URL and get clean content
    response = ctx.deps.firecrawl.scrape_url(url)

    # Parse the response using our Pydantic model
    firecrawl_response = FirecrawlResponse(**response)

    # Extract relevant information from the response
    metadata = firecrawl_response.metadata

    return WebsiteContent(
        title=metadata.title or "Untitled",
        description=metadata.description or metadata.ogDescription or "",
        main_content=firecrawl_response.markdown,
        url=metadata.sourceURL or url
    )


def get_content_preferences(console: Console) -> ContentPreferences:
    """Get content preferences from user input with defaults."""
    console.print(
        "\n[cyan]Content Preferences (press Enter to use defaults)[/cyan]")

    audience = Prompt.ask(
        "Target audience",
        default=DEFAULT_AUDIENCE,
        show_default=True
    )

    tone = Prompt.ask(
        "Content tone",
        default=DEFAULT_TONE,
        show_default=True
    )

    return ContentPreferences(audience=audience, tone=tone)


async def generate_social_posts(url: str, preferences: ContentPreferences) -> List[SocialMediaPost]:
    """Generate social media posts from a website URL."""
    # Initialize FireCrawl with API key
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY environment variable is required")

    firecrawl_app = FirecrawlApp(api_key=api_key)
    deps = Deps(firecrawl=firecrawl_app, preferences=preferences)

    # Extract content from website
    content_result = await content_extraction_agent.run(
        f"Please extract content from {url} and create a WebsiteContent object with the information.",
        deps=deps
    )
    deps.website_content = content_result.data

    # Generate posts for each platform
    posts_result = await post_generation_agent.run(
        f"""Create social media posts for all platforms using this content:
        Title: {deps.website_content.title}
        Description: {deps.website_content.description}
        Content: {deps.website_content.main_content}
        URL: {deps.website_content.url}
        
        Target Audience: {preferences.audience}
        Tone of Voice: {preferences.tone}
        
        Make sure the posts are tailored to the specified audience and maintain the desired tone.""",
        deps=deps
    )
    return posts_result.data


async def main():
    console = Console()

    # Check for API key
    if not os.getenv("FIRECRAWL_API_KEY"):
        console.print(
            "[red]Error: FIRECRAWL_API_KEY environment variable is required[/red]")
        console.print("Get your API key at: https://docs.firecrawl.dev")
        return

    # Get URL from user
    url = console.input("[cyan]Enter website URL:[/cyan] ")

    try:
        # Validate URL
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            raise ValueError("Invalid URL")

        # Get content preferences
        preferences = get_content_preferences(console)

        console.print("\n[yellow]Generating social media posts...[/yellow]")
        posts = await generate_social_posts(url, preferences)

        # Save posts to markdown file
        output_file = save_posts_to_markdown(url, preferences, posts)

        # Display results
        console.print("\n[green]Generated Posts:[/green]")
        console.print(f"[dim]Audience: {preferences.audience}[/dim]")
        console.print(f"[dim]Tone: {preferences.tone}[/dim]")
        console.print(f"[dim]Saved to: {output_file}[/dim]\n")

        for post in posts:
            console.print(Panel(
                f"{post.content}\n\n[blue]Hashtags:[/blue] {' '.join(f'#{tag}' for tag in post.hashtags)}",
                title=f"[bold]{post.platform.title()}[/bold]",
                border_style="green"
            ))

    except Exception as e:
        console.print(f"\n[red]Error:[/red] {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
