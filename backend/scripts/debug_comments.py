from bilibili_api import comment, sync, video
import asyncio

async def debug():
    bvid = "BV1hzqrBtEMP"
    print(f"Testing BVID: {bvid}")
    v = video.Video(bvid=bvid)
    info = await v.get_info()
    aid = info.get('aid')
    print(f"AID found: {aid} (type: {type(aid)})")
    
    if not aid:
        print("No AID found!")
        return

    try:
        print("Fetching comments...")
        res = await comment.get_comments(oid=aid, type_=comment.CommentResourceType.VIDEO)
        print("Response keys:", res.keys() if res else "None")
        print("Response structure:", {k: type(v) for k, v in res.items()} if res else "None")
        replies = res.get('replies')
        if replies is None:
            print("Replies is None! Checking if there are other keys like 'top' or 'hots'...")
            print("Hots count:", len(res.get('hots', [])) if res.get('hots') else 0)
        else:
            print(f"Number of replies: {len(replies)}")
        for r in replies[:2]:
            print(f" - {r.get('member', {}).get('uname')}: {r.get('content', {}).get('message')[:50]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    sync(debug())
