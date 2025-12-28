import sys
import os
import asyncio

# 添加项目根目录到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.bilibili_service import bilibili_service

def test_fetch_comments():
    # 使用刚刚抓取到的第一个 BVID，或者一个非常火的视频
    bvid = "BV1hzqrBtEMP" 
    print(f"\n💬 开始测试 B 站评论抓取 (BVID: {bvid})...")
    print("注意：如果该视频是新发的或者评论较少，可能抓不到热门评论。")
    
    comments = bilibili_service.get_video_comments(bvid, limit=5)
    
    if comments:
        print(f"✅ 成功抓取到 {len(comments)} 条热门评论：\n")
        for i, c in enumerate(comments):
            print(f"【{i+1}】 {c['user']}:")
            print(f"      内容: {c['content'][:100]}...")
            print(f"      点赞数: {c['likes']}")
            print(f"      时间: {c['published_at']}")
            print("-" * 20)
    else:
        print("❌ 未能抓取到评论（可能是视频无评论或触发风控）。")

if __name__ == "__main__":
    test_fetch_comments()
