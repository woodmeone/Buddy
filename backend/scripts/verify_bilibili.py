import sys
import os

# Add the project root to sys.path to allow absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.bilibili_service import bilibili_service

def test_bilibili():
    # 示例 UID: 2267573 (老番茄)
    uid = 2267573
    print(f"\n--- Testing Bilibili SDK ---")
    
    # 1. Test User Videos (Listing)
    vids = bilibili_service.fetch_user_videos(uid, limit=3)
    if not vids:
        print("Could not fetch user videos (likely blocked). Testing single video info instead...")
        # Use a known BVID
        bvid = "BV1ar4y1b7U4"
    else:
        print(f"Successfully fetched {len(vids)} videos via SDK.")
        bvid = vids[0]['original_id']
    
    # 2. Test Video Details (Metrics)
    print(f"\n--- Fetching details for {bvid} ---")
    details = bilibili_service.get_video_details(bvid)
    if details:
        print(f"Real Metrics for {bvid}:")
        for k, v in details.items():
            print(f"    {k}: {v}")
    else:
        print(f"Failed to fetch details for {bvid}.")

if __name__ == "__main__":
    test_bilibili()
