import sys
import os

# Add root to path
sys.path.append(os.getcwd())

from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import get_session

print("Imports OK")

# DB Setup
sqlite_url = "sqlite://" # In memory
engine = create_engine(
    sqlite_url, 
    connect_args={"check_same_thread": False}, 
    poolclass=StaticPool
)

print("Engine Created")

SQLModel.metadata.create_all(engine)
print("Tables Created")

def get_session_override():
    with Session(engine) as session:
        yield session

try:
    print("Attempting to create TestClient...")
    client = TestClient(app)
    print("Client Created")
except TypeError as e:
    print(f"TypeError during TestClient init: {e}")
    # Try alternate init if startlette/httpx changed?
    # client = TestClient(transport=...) 
    client = None
except Exception as e:
    print(f"Error during TestClient init: {e}")
    client = None

try:
    response = client.get("/")
    print(f"Root endpoint: {response.status_code}")
    print(response.json())
    
    # Test Create
    resp = client.post("/api/v1/personas/", json={"name": "Debug", "depth": 1})
    print(f"Create Persona: {resp.status_code}")
    print(resp.json())
    
except Exception as e:
    import traceback
    traceback.print_exc()

print("Debug Finished")
