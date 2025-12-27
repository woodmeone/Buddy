import pytest
from backend.services.crawler import crawler_service
from backend.models import SourceConfig
from datetime import datetime

def test_crawler_bilibili():
    # Mock config
    config = SourceConfig(id=1, type="bilibili_user", name="TestUP", config_data={"uid": "123"}, enabled=True)
    items = crawler_service.generate_feed([config])
    
    assert len(items) > 0
    assert items[0]["source"] == "Bilibili"
    assert "TestUP" in items[0]["title"] or "123" in items[0]["title"] or "TestUP" in items[0]["summary"]
    # Relaxed check: Logic uses random templates, some include name, some don't.
    # The template is: f"【{name}】..."
    # So name should be in title.
    assert "TestUP" in items[0]["title"]

def test_crawler_rss_github():
    config = SourceConfig(id=2, type="rss_feed", name="GH", config_data={"url": "https://github.com/trending"}, enabled=True)
    items = crawler_service.generate_feed([config])
    
    assert len(items) > 0
    assert items[0]["source"] == "GitHub"
    assert "stars" in items[0]["metrics"]

def test_crawler_mixed():
    c1 = SourceConfig(type="bilibili_user", name="B", enabled=True)
    c2 = SourceConfig(type="hot_list", name="Weibo", enabled=True)
    c3 = SourceConfig(type="bilibili_user", name="Disabled", enabled=False)
    
    items = crawler_service.generate_feed([c1, c2, c3])
    # Expect items from B and Weibo, none from Disabled
    sources = set(i["source"] for i in items)
    assert "Bilibili" in sources
    assert "Weibo" in sources
    
    # Verify sorting (descending time)
    t1 = datetime.fromisoformat(items[0]["published_at"])
    t2 = datetime.fromisoformat(items[-1]["published_at"])
    assert t1 >= t2
