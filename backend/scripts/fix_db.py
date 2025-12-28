import sqlite3
import os

db_path = 'buddy.db'

def fix_schema():
    print(f"Connecting to {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Add AI columns to topic
    try:
        cursor.execute("ALTER TABLE topic ADD COLUMN ai_title VARCHAR")
        print("Added ai_title to topic")
    except Exception as e:
        print(f"ai_title already exists or error: {e}")
        
    try:
        cursor.execute("ALTER TABLE topic ADD COLUMN ai_summary VARCHAR")
        print("Added ai_summary to topic")
    except Exception as e:
        print(f"ai_summary already exists or error: {e}")

    # 2. Add outline to script
    try:
        cursor.execute("ALTER TABLE script ADD COLUMN outline JSON")
        print("Added outline to script")
    except Exception as e:
        print(f"outline already exists or error: {e}")

    # 3. Create a test topic if none exists
    cursor.execute("SELECT count(*) FROM topic")
    count = cursor.fetchone()[0]
    if count == 0:
        print("Creating a test topic...")
        cursor.execute("""
            INSERT INTO topic (source_config_id, original_id, title, url, status, saved_at)
            VALUES (1, 'test_bv123', 'B站爆款视频测试', 'https://bilibili.com/video/BV123', 'saved', datetime('now'))
        """)
    
    conn.commit()
    conn.close()
    print("Database maintenance completed.")

if __name__ == "__main__":
    if os.path.exists(db_path):
        fix_schema()
    else:
        print("Database not found. Please run the backend once to create it.")
