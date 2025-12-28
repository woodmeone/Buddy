import requests
import json
import time

BASE_URL = "http://127.0.0.1:8321/api/v1"

def test_persistence():
    # 1. Get Topic Library
    print("Fetching Topics...")
    res = requests.get(f"{BASE_URL}/topics/")
    topics = res.json()
    
    if not topics:
        print("No topics found in library. Please save a topic first.")
        return
    
    topic = topics[0]
    topic_id = topic['id']
    print(f"Targeting Topic ID: {topic_id} ('{topic['title']}')")
    
    # 2. Generate Metadata
    print("\nGenerating AI Metadata...")
    res = requests.post(f"{BASE_URL}/topics/{topic_id}/generate-metadata")
    updated_topic = res.json()
    print(f"AI Title: {updated_topic.get('ai_title')}")
    print(f"AI Summary: {updated_topic.get('ai_summary')[:50]}...")
    
    # 3. Verify Persistence (Fetch again)
    print("\nVerifying Persistence...")
    res = requests.get(f"{BASE_URL}/topics/{topic_id}")
    fresh_topic = res.json()
    if fresh_topic.get('ai_title') == updated_topic.get('ai_title'):
        print("✅ Metadata Persisted!")
    else:
        print("❌ Metadata Persistence Failed!")

    # 4. Generate Script
    print("\nGenerating Script...")
    res = requests.post(f"{BASE_URL}/scripts/generate", json={"topic_id": topic_id, "template_id": 1})
    script = res.json()
    print(f"Script title: {script.get('title')}")
    
    # 5. Verify Script Persistence (Call again, should be instant/cached)
    start_time = time.time()
    res = requests.post(f"{BASE_URL}/scripts/generate", json={"topic_id": topic_id, "template_id": 1})
    duration = time.time() - start_time
    print(f"Second call duration: {duration:.4f}s")
    if duration < 0.5:
        print("✅ Script Persistence/Caching verified!")
    else:
        print("⚠️ Script generation was slow, check if cached.")

if __name__ == "__main__":
    test_persistence()
