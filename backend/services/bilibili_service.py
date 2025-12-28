from typing import List, Dict, Optional
from bilibili_api import user, video, sync, comment
import time

class BilibiliService:
    """
    Service to interact with Bilibili APIs.
    """

    @staticmethod
    def get_video_comments(bvid: str, limit: int = 10) -> List[Dict]:
        """
        Fetches top comments for a video.
        """
        try:
            time.sleep(1)
            # Fetch AID
            v = video.Video(bvid=bvid)
            info = sync(v.get_info())
            aid = info.get('aid')
            if not aid:
                return []

            time.sleep(0.5)
            # Use minimal arguments to avoid SDK version conflicts with parameter names
            res = sync(comment.get_comments(oid=aid, type_=comment.CommentResourceType.VIDEO))
            
            # The SDK might return 'replies' as None if empty or blocked
            replies = res.get('replies') or []
            comments = []
            
            for r in replies[:limit]:
                comments.append({
                    "user": r.get('member', {}).get('uname'),
                    "content": r.get('content', {}).get('message'),
                    "likes": r.get('like', 0),
                    "published_at": BilibiliService._timestamp_to_iso(r.get('ctime'))
                })
            return comments
        except Exception as e:
            print(f"Error fetching comments for video {bvid}: {e}")
            return []

    @staticmethod
    def get_video_details(bvid: str) -> Dict:
        """
        Fetches detailed information for a single video including metrics and tags.
        """
        try:
            # 合理安排间隔，避免触发 412
            time.sleep(1) 
            v = video.Video(bvid=bvid)
            info = sync(v.get_info())
            
            # 再等一下拿标签
            time.sleep(0.5)
            tags_list = sync(v.get_tags())
            tags = [tag.get("tag_name") for tag in tags_list] if tags_list else []
            
            stat = info.get("stat", {})
            return {
                "metrics": {
                    "views": stat.get("view", 0),
                    "likes": stat.get("like", 0),
                    "coins": stat.get("coin", 0),
                    "stars": stat.get("favorite", 0),
                    "comments": stat.get("reply", 0)
                },
                "tags": tags,
                "title": info.get("title"),
                "summary": info.get("desc")
            }
        except Exception as e:
            print(f"Error fetching details for video {bvid}: {e}")
            return {}

    @staticmethod
    def fetch_user_videos(uid: int, limit: int = 10) -> List[Dict]:
        """
        Fetches the latest videos uploaded by a user.
        """
        try:
            # 基础请求间隔
            time.sleep(1)
            u = user.User(uid)
            res = sync(u.get_videos(ps=limit))
            video_list = res.get("list", {}).get("vlist", [])
            topics = []
            
            for v in video_list:
                topics.append({
                    "original_id": v.get("bvid"),
                    "title": v.get("title"),
                    "url": f"https://www.bilibili.com/video/{v.get('bvid')}",
                    "summary": v.get("description"),
                    "thumbnail": v.get("pic"),
                    "metrics": {
                        "views": v.get("play"),
                        "comments": v.get("comment"),
                        "likes": 0 
                    },
                    "published_at": BilibiliService._timestamp_to_iso(v.get("created")),
                    "source": "Bilibili"
                })
            return topics
        except Exception as e:
            print(f"Bilibili SDK fetch_user_videos failed for {uid}: {e}")
            return []

    @staticmethod
    def _timestamp_to_iso(timestamp: Optional[int]) -> Optional[str]:
        if not timestamp:
            return None
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).isoformat()

bilibili_service = BilibiliService()
