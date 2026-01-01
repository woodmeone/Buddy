import requests
import json

base_url = "http://127.0.0.1:8321" # Call backend directly

def test_metadata(topic_id, persona_id):
    url = f"{base_url}/api/v1/topics/{topic_id}/generate-metadata?persona_id={persona_id}"
    print(f"Testing URL: {url}")
    try:
        response = requests.post(url, json={})
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Use topic 27 as mentioned by user
    test_metadata(27, 2)
