from backend.database import engine, SessionLocal
from backend.services.crawler import crawler_service
from backend.models import Topic
from sqlmodel import Session, select

def test_sync_offline():
    print("Testing sync_all_sources offline...")
    try:
        with SessionLocal() as session:
            # We only sync if there's a config, let's check
            from backend.models import SourceConfig
            configs = session.exec(select(SourceConfig)).all()
            print(f"Found {len(configs)} configs.")
            
            # Run sync
            crawler_service.sync_all_sources(session)
            
            # Check topics
            topics = session.exec(select(Topic)).all()
            print(f"Total topics after sync: {len(topics)}")
            for t in topics[:3]:
                print(f"- {t.title} (Status: {t.status})")
                
    except Exception as e:
        print(f"Sync failed: {e}")

if __name__ == "__main__":
    test_sync_offline()
