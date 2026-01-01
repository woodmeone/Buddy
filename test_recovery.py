import requests

base_url = "http://127.0.0.1:8321/api/v1"

def test_script_recovery(topic_id):
    url = f"{base_url}/scripts/topic/{topic_id}"
    print(f"Testing Script Recovery for Topic {topic_id}: {url}")
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Script Found! Title: {data['title']}")
            print(f"Content Length: {len(data['content'])}")
        else:
            print(f"Script Not Found. Detail: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_script_recovery(27)
