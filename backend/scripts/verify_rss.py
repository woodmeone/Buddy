import sys
import os

# Add the project root to sys.path to allow absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.rss_service import rss_service

def test_real_rss():
    # Test with a known Bilibili RSSHub link if possible, or a standard tech blog
    urls = [
        "https://feeds.feedburner.com/PythonInsider", # Python official blog
        "https://rsshub.app/bilibili/user/video/2267573", # 示例：老番茄 (B站UP主)
    ]
    
    for url in urls:
        print(f"\n--- Testing URL: {url} ---")
        try:
            topics = rss_service.fetch_and_parse(url)
            print(f"Found {len(topics)} items.")
            for i, topic in enumerate(topics[:3]): # Show first 3
                print(f"[{i+1}] Title: {topic['title']}")
                print(f"    Source: {topic['source']}")
                print(f"    Metrics: {topic['metrics']}")
                if topic['thumbnail']:
                    print(f"    Thumbnail: Found")
                print(f"    Summary: {topic['summary'][:100]}...")
        except Exception as e:
            print(f"Error testing {url}: {e}")

if __name__ == "__main__":
    test_real_rss()
