import requests
import time

base_url = "http://127.0.0.1:8321"

def test_metadata(topic_id, persona_id):
    url = f"{base_url}/api/v1/topics/{topic_id}/generate-metadata?persona_id={persona_id}"
    print(f"Testing URL: {url}")
    start = time.time()
    try:
        response = requests.post(url, json={}, timeout=60)
        end = time.time()
        print(f"Status Code: {response.status_code}")
        print(f"Time Taken: {end - start:.2f}s")
        # print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_metadata(27, 2)
