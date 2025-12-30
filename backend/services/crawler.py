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
    
    def sync_all_sources(self, session: Session):
        """
        Background task: Fetch all enabled sources and save to DB.
        """
        from ..models import SourceConfig
        configs = session.exec(select(SourceConfig).where(SourceConfig.enabled == True)).all()
        
        # We process one by one to avoid overwhelming memory/network
        for config in configs:
            print(f"Syncing source: {config.name} ({config.type})...")
            
            # Clear existing "new" topics for this config before fetching fresh ones
            # This ensures only the latest data is shown in Discovery Feed
            from sqlmodel import delete
            session.exec(
                delete(Topic)
                .where(Topic.source_config_id == config.id)
                .where(Topic.status == "new")
            )
            # Zombie/Orphan cleanup
            session.exec(
                delete(Topic)
                .where(Topic.source_config_id == None)
                .where(Topic.status == "new")
            )
            session.commit()

            items = self.fetch_feed([config])
            
            for item in items:
                # Check duplication
                existing = session.exec(
                    select(Topic).where(Topic.original_id == item["original_id"])
                ).first()
                
                if existing:
                    # Update source_config_id if missing or changed (orphan fix)
                    if existing.source_config_id != item["source_config_id"]:
                        existing.source_config_id = item["source_config_id"]
                    
                    # Update author (Remark might have changed) and metrics
                    existing.author = item.get("author")
                    existing.metrics = item.get("metrics", {})
                    existing.thumbnail = item.get("thumbnail")
                    
                    session.add(existing)
                    session.commit()
                    continue
                
                # New Topic
                db_topic = Topic(
                    source_config_id=item["source_config_id"],
                    original_id=item["original_id"],
                    title=item["title"],
                    url=item["url"],
                    summary=item["summary"],
                    thumbnail=item["thumbnail"],
                    author=item.get("author"),
                    metrics=item.get("metrics", {}),
                    analysis_result=item.get("analysis_result", {}),
                    status="new",
                    published_at=datetime.fromisoformat(item["published_at"]) if item.get("published_at") else None
                )
                session.add(db_topic)
                session.commit()
                session.refresh(db_topic)
                
                # Add Tags/Labels
                labels = item.get("labels", [])
                for label_name in labels:
                    tag = TopicTag(topic_id=db_topic.id, tag_name=label_name)
                    session.add(tag)
                
                session.commit()

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
