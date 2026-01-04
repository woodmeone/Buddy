from sqlmodel import Session, select
from backend.database import engine, create_db_and_tables
from backend.models import Persona, SourceConfig

def check_and_seed():
    # Ensure tables exist
    create_db_and_tables()
    
    with Session(engine) as session:
        # Check Personas
        personas = session.exec(select(Persona)).all()
        print(f"Found {len(personas)} personas.")
        
        if len(personas) == 0:
            print("Seeding default persona...")
            # Seed based on mock data
            default_persona = Persona(
                name='Default (通用)',
                description='系统默认人设',
                custom_prompt='你是一个充满热情的技术博主，擅长用通俗易懂的语言解释复杂的技术概念。',
                depth=7,
                interests=['Python', 'AI', 'Vue3']
            )
            session.add(default_persona)
            session.commit()
            session.refresh(default_persona)
            
            # Seed inputs
            s1 = SourceConfig(
                persona=default_persona,
                type="bilibili_user",
                name="竞品监控",
                enabled=True,
                config_data={"uid": "12345678"}
            )
            s2 = SourceConfig(
                persona=default_persona,
                type="hot_list",
                name="知乎热榜",
                enabled=True
            )
            session.add(s1)
            session.add(s2)
            session.commit()
            print("Seeding complete.")
        else:
            for p in personas:
                print(f" - {p.name} (ID: {p.id})")

if __name__ == "__main__":
    check_and_seed()
