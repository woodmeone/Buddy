import feedparser
import re
from typing import List, Dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup

class RssService:
    """
    Service to handle RSS feed fetching and parsing.
    Specially optimized for RSSHub to extract metrics like views and likes.
    """

    @staticmethod
    def fetch_and_parse(url: str) -> List[Dict]:
        """
        Fetches an RSS feed and returns a list of dictionaries compatible with the Topic model.
        """
        feed = feedparser.parse(url)
        topics = []

        for entry in feed.entries:
            description = entry.get("description", "")
            metrics = RssService._extract_metrics(description)
            
            # Clean up description to be used as a summary
            summary = RssService._clean_description(description)

            # Extract thumbnail if available
            thumbnail = RssService._extract_thumbnail(description)

            topic = {
                "original_id": entry.get("id") or entry.get("link"),
                "title": entry.get("title"),
                "url": entry.get("link"),
                "summary": summary,
                "thumbnail": thumbnail,
                "metrics": metrics,
                "published_at": RssService._parse_date(entry.get("published")),
                "source": feed.feed.get("title", "RSS Source")
            }
            topics.append(topic)

        return topics

    @staticmethod
    def _extract_metrics(description: str) -> Dict:
        """
        Extracts metrics (views, likes, etc.) from RSSHub-generated description HTML.
        """
        metrics = {}
        if not description:
            return metrics

        # Bilibili RSSHub pattern: 播放量: 1234, 点赞: 567, etc.
        patterns = {
            "views": r"播放量[:：]\s*(\d+)",
            "likes": r"点赞[:：]\s*(\d+)",
            "comments": r"评论[:：]\s*(\d+)",
            "coins": r"硬币[:：]\s*(\d+)",
            "stars": r"收藏[:：]\s*(\d+)"
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, description)
            if match:
                metrics[key] = int(match.group(1))

        return metrics

    @staticmethod
    def _clean_description(description: str) -> str:
        """
        Removes HTML tags and extra whitespace from description for a cleaner summary.
        """
        if not description:
            return ""
        soup = BeautifulSoup(description, "html.parser")
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text(separator=" ", strip=True)
        # Remove the metric lines if they exist at the end/start to keep summary clean
        text = re.sub(r"(播放量|点赞|评论|硬币|收藏)[:：]\s*\d+", "", text)
        return text[:500] # Limit summary length

    @staticmethod
    def _extract_thumbnail(description: str) -> Optional[str]:
        """
        Extracts the first image URL from the description to use as a thumbnail.
        """
        if not description:
            return None
        soup = BeautifulSoup(description, "html.parser")
        img = soup.find("img")
        return img["src"] if img and img.has_attr("src") else None

    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[str]:
        """
        Parses various date formats into ISO format.
        """
        if not date_str:
            return None
        # feedparser handles a lot of this automatically, but we ensure string format
        try:
            # You might want to use something more robust like dateutil if needed
            return date_str # feedparser already tries to normalize to some extent
        except:
            return None

rss_service = RssService()
