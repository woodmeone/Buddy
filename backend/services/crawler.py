from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlmodel import Session, select
from ..models import Topic, TopicTag, SourceConfig
from .rss_service import rss_service
from .bilibili_service import bilibili_service

import random

class CrawlerService:
    """
    Service to fetch data from external platforms.
    """
    def __init__(self):
        self.is_syncing = False
        self.total_count = 0
        self.current_count = 0
        self.last_message = ""
    
    def sync_all_sources(self, session: Session):
        """
        Background task: Fetch all enabled sources and save to Redis cache (TopHub style).
        """
        from .cache_service import cache_service
        from ..models import Persona
        
        # 1. Get all personas to group configs
        personas = session.exec(select(Persona)).all()
        
        # Reset progress
        self.is_syncing = True
        self.total_count = sum(len([c for c in p.source_configs if c.enabled]) for p in personas)
        self.current_count = 0
        self.last_message = "开始同步..."

        for persona in personas:
            print(f"Syncing all sources for persona: {persona.name}...")
            
            # 2. Aggregated feed for this persona
            persona_items = []
            
            configs = [c for c in persona.source_configs if c.enabled]
            if not configs:
                continue
                
            # 3. Fetch data for each config
            for config in configs:
                self.current_count += 1
                self.last_message = f"正在同步 {persona.name} 的 {config.name}..."
                print(f"  Fetching: {config.name} ({config.type})...")
                items = self.fetch_feed([config])
                
                for item in items:
                    # Enrich with source info for frontend
                    source_str = "Unknown"
                    if config.type == "bilibili_user": source_str = "Bilibili"
                    elif config.type == "rss_feed": source_str = "RSS"
                    elif config.type == "hot_list": source_str = "HotList"
                    
                    item["source"] = source_str
                    persona_items.append(item)
            
            # 4. Save to Redis (Key: discovery:persona:{id}, TTL: 12 Hours)
            # Sort by date before saving
            persona_items.sort(key=lambda x: x.get("published_at") or "", reverse=True)
            cache_key = f"discovery:persona:{persona.id}"
            cache_service.set(cache_key, persona_items, expire=43200)
            
            print(f"  ✓ Saved {len(persona_items)} items to Redis cache for {persona.name}")

        self.is_syncing = False
        self.last_message = "同步完成"
        self.current_count = self.total_count

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
                # Prioritize config.name (Remark) as author
                if config.name:
                    item["author"] = config.name
                elif not item.get("author"):
                    item["author"] = "采集UP主"
                
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
                
                # Filter by views_threshold
                views = item.get("metrics", {}).get("views", 0)
                if views < config.views_threshold:
                    print(f"Skipping video '{item['title']}' due to views threshold ({views} < {config.views_threshold})")
                    continue
                
                item["analysis_result"] = self._random_analysis()
                item["score"] = round(random.uniform(70, 99), 1)
                item["status"] = "new"
                
                # Only add to results if it passed all processing (including filter)
                feed_items.append(item)
            
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
