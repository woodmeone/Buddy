import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from .rss_service import rss_service
from .bilibili_service import bilibili_service

class CrawlerService:
    """
    Service to fetch data from external platforms.
    """
    
    def fetch_feed(self, source_configs: List) -> List[Dict]:
        """
        Main entry point. Aggregates data from all enabled source configs.
        """
        feed_items = []
        
        for config in source_configs:
            if not config.enabled:
                continue
                
            items = []
            # NEW: Priority for Bilibili SDK
            if config.type == "bilibili_user":
                uid = config.config_data.get("uid")
                if uid:
                    try:
                        # Convert to int if it's a string from JSON
                        items = bilibili_service.fetch_user_videos(int(uid))
                    except Exception as e:
                        print(f"Error fetching real Bilibili data for {uid}: {e}")
                        # Fallback to RSSHub if SDK fails
                        url = f"https://rsshub.app/bilibili/user/video/{uid}"
                        try:
                            items = rss_service.fetch_and_parse(url)
                        except: pass
            
            elif config.type == "rss_feed":
                url = config.config_data.get("url")
                if url:
                    try:
                        items = rss_service.fetch_and_parse(url)
                    except Exception as e:
                        print(f"Error fetching RSS {url}: {e}")
            
            # Tag items and polish
            for item in items:
                item["source_config_id"] = config.id
                
                # Enrich Bilibili data if it's a Bilibili item
                if item.get("source") == "Bilibili" and item.get("original_id"):
                    details = bilibili_service.get_video_details(item["original_id"])
                    if details:
                        # Update metrics
                        if "metrics" in details:
                            item["metrics"].update(details["metrics"])
                        
                        # Set tags (frontend uses 'labels' mapping)
                        item["labels"] = details.get("tags", [])
                        
                        # Update title/summary if necessary (ensure high quality)
                        if details.get("title"):
                            item["title"] = details["title"]
                        if details.get("summary"):
                            item["summary"] = details["summary"]
                
                item["analysis_result"] = self._random_analysis()
                item["score"] = round(random.uniform(70, 99), 1)
                item["status"] = "new"
            
            feed_items.extend(items)
            
        # Sort by freshness
        feed_items.sort(key=lambda x: x.get("published_at") or "", reverse=True)
        return feed_items

    def _random_time(self):
        """Returns ISO format time within last 24 hours"""
        dt = datetime.utcnow() - timedelta(hours=random.randint(0, 24), minutes=random.randint(0, 59))
        return dt.isoformat()

    def _random_analysis(self):
        return {
            "difficulty": random.choice(["Low", "Medium", "High"]),
            "personaMatch": random.choice(["High", "Very High", "Medium"]),
            "commercialValue": random.choice(["Low", "Medium", "High"])
        }

crawler_service = CrawlerService()
