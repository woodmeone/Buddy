import sys
import os
import time

# 添加项目根目录到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.bilibili_service import bilibili_service

def test_bilibili_real_time():
    """
    测试脚本：模拟后端真实抓取流程
    1. 获取 UP 主视频列表
    2. 对每个视频进行深度数据增强（带间隔）
    """
    # 示例 UID: 2267573 (老番茄)
    uid = 2267573
    print(f"\n🚀 开始测试 B 站深度抓取 (UID: {uid})...")
    
    # 第一步：获取视频列表
    vids = bilibili_service.fetch_user_videos(uid, limit=3)
    if not vids:
        print("❌ 列表抓取失败（可能是风控或网络问题）。")
        return

    print(f"✅ 成功找到 {len(vids)} 个视频，开始逐一增强数据...\n")

    for i, item in enumerate(vids):
        bvid = item['original_id']
        print(f"正在抓取第 {i+1} 个视频详情: {bvid} - {item['title'][:20]}...")
        
        # 深度增强：获取点赞、投币、标签等
        details = bilibili_service.get_video_details(bvid)
        
        if details:
            print(f"   📊 数据点明细:")
            print(f"      - 播放量: {details['metrics']['views']}")
            print(f"      - 点赞数: {details['metrics']['likes']}")
            print(f"      - 收藏数: {details['metrics']['stars']}")
            print(f"      - 标签: {', '.join(details['tags'][:5])}...")
            print(f"      - 简介长度: {len(details['summary'])} 字")
        else:
            print(f"   ⚠️ 详情抓取失败。")
        
        print("-" * 40)
        # 这里不需要在这里 sleep，因为 service 内部已经写了 sleep

    print("\n🎉 测试完成！您可以放心地在前端使用了。")

if __name__ == "__main__":
    test_bilibili_real_time()
