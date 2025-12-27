import random
from datetime import datetime, timedelta
from typing import List, Dict

class MockCrawlerService:
    """
    Simulates fetching data from external platforms (Bilibili, GitHub, RSS).
    Generates realistic looking mock data based on input configuration.
    """
    
    def generate_feed(self, source_configs: List) -> List[Dict]:
        """
        Main entry point. Aggregates data from all enabled source configs.
        """
        feed_items = []
        
        for config in source_configs:
            if not config.enabled:
                continue
                
            items = []
            if config.type == "bilibili_user":
                items = self._mock_bilibili(config)
            elif config.type == "rss_feed":
                # Treat RSS as GitHub for now if url contains github, else generic
                if "github" in (config.config_data.get("url") or ""):
                    items = self._mock_github(config)
                else:
                    items = self._mock_rss(config)
            elif config.type == "hot_list":
                items = self._mock_hot_list(config)
            
            feed_items.extend(items)
            
        # Sort by freshness (randomized slightly)
        feed_items.sort(key=lambda x: x["published_at"], reverse=True)
        return feed_items

    def _mock_bilibili(self, config) -> List[Dict]:
        """Generates mock Bilibili videos for a specific UP owner"""
        uid = config.config_data.get("uid", "000")
        name = config.name or f"UP主{uid}"
        
        templates = [
            f"【{name}】DeepSeek vs ChatGPT 深度测评，谁才是最强AI？",
            f"还在手写代码？这个 {name} 推荐的 AI 工具太强了！",
            f"耗时30天，我用 AI 做了一个 {name} 风格的视频",
            f"突发！OpenAI 发布 Sora 2.0，{name} 带你首发体验",
            f"前端已死？{name} 聊聊 2024 年程序员的出路"
        ]
        
        items = []
        count = random.randint(1, 4) # 1-4 new videos per source
        for _ in range(count):
            title = random.choice(templates)
            views = random.randint(5000, 1000000)
            items.append({
                "id": random.randint(1000000, 9999999),
                "original_id": f"BV{random.randint(100000, 999999)}",
                "title": title,
                "source": "Bilibili",
                "url": f"https://www.bilibili.com/video/BV{random.randint(100000, 999999)}",
                "summary": f"{title} - 视频详细解读。播放量 {views}，评论区热议中。",
                "metrics": {"views": views, "likes": int(views * 0.1)},
                "analysis_result": self._random_analysis(),
                "status": "new",
                "published_at": self._random_time(),
                "score": round(random.uniform(70, 99), 1),
                "thumbnail": f"https://api.dicebear.com/7.x/shapes/svg?seed={title}"
            })
        return items

    def _mock_github(self, config) -> List[Dict]:
        """Generates mock GitHub Trending repos"""
        topics = ["Agent", "RAG", "LLM", "Vue3", "Rust", "FastAPI"]
        
        items = []
        count = random.randint(2, 5)
        for _ in range(count):
            topic = random.choice(topics)
            name = f"{topic}-{random.choice(['Next', 'Pro', 'Lite', 'Zero', 'Copilot'])}"
            stars = random.randint(1000, 50000)
            
            items.append({
                "id": random.randint(1000000, 9999999),
                "original_id": f"gh-{name}",
                "title": f"{name}: The Ultimate {topic} Framework",
                "source": "GitHub",
                "url": f"https://github.com/example/{name}",
                "summary": f"A lightweight, high-performance {topic} library. Gained {random.randint(100, 2000)} stars today.",
                "metrics": {"stars": stars, "forks": int(stars * 0.2)},
                "analysis_result": self._random_analysis(),
                "status": "new",
                "published_at": self._random_time(),
                "score": round(random.uniform(80, 99), 1),
                "thumbnail": None
            })
        return items

    def _mock_rss(self, config) -> List[Dict]:
        """Generates mock generic RSS articles"""
        site_name = config.name or "TechBlog"
        
        templates = [
            f"{site_name}: Why Python is still king in 2024",
            f"Understanding RAG Architecture - {site_name}",
            f"10 Tips for Senior Engineers from {site_name}",
            f"The future of Web Development: {site_name} predictions"
        ]
        
        items = []
        count = random.randint(1, 3)
        for _ in range(count):
            title = random.choice(templates)
            items.append({
                "id": random.randint(1000000, 9999999),
                "original_id": f"rss-{random.randint(1000, 9999)}",
                "title": title,
                "source": "RSS",
                "url": "https://example.com/blog/article",
                "summary": f"Latest article from {site_name}. Discusses deep technical concepts.",
                "metrics": {},
                "analysis_result": self._random_analysis(),
                "status": "new",
                "published_at": self._random_time(),
                "score": round(random.uniform(60, 90), 1),
                "thumbnail": None
            })
        return items
        
    def _mock_hot_list(self, config) -> List[Dict]:
        """Generates mock Hot List items"""
        platform = config.name
        
        items = []
        count = random.randint(3, 6)
        for i in range(count):
            heat = random.randint(500000, 5000000)
            items.append({
                "id": random.randint(1000000, 9999999),
                "original_id": f"hot-{platform}-{i}",
                "title": f"【{platform}热搜】全民讨论 AI 替代人工 Issue #{i}",
                "source": platform,
                "url": "https://weibo.com/hot/1",
                "summary": f"当前热度 {heat}。社会影响巨大。",
                "metrics": {"heat": heat},
                "analysis_result": self._random_analysis(),
                "status": "new",
                "published_at": self._random_time(),
                "score": round(random.uniform(70, 95), 1),
                "thumbnail": None
            })
        return items

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

crawler_service = MockCrawlerService()
