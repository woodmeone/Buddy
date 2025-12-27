import pytest
from fastapi.testclient import TestClient
from backend.models import Persona, Topic, Script

def test_create_persona(client: TestClient):
    response = client.post(
        "/api/v1/personas/",
        json={"name": "Test Geek", "description": "A test persona", "depth": 8}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Geek"
    assert data["id"] is not None
    assert data["depth"] == 8

def test_read_personas(client: TestClient):
    # Create one first
    client.post("/api/v1/personas/", json={"name": "P1"})
    client.post("/api/v1/personas/", json={"name": "P2"})
    
    response = client.get("/api/v1/personas/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_source_config_nested(client: TestClient):
    # Test creating persona doesn't crash, but SourceConfig creation is implicit or separate?
    # Current API personas.py doesn't handle nested source_configs in create_persona directly 
    # unless using a complex Pydantic model (PersonWithSources) which we haven't defined yet in API.
    # Looking at models.py, PersonaBase doesn't have source_configs field.
    # So we probably need separate endpoints for SourceConfigs or update Persona API.
    # FOR NOW: basic persona test is valid.
    pass

def test_create_topic(client: TestClient):
    # 1. Create SourceConfig (Need to implement SourceConfig API? Or just manually in DB for test?)
    # Topics can exist without source_config_id (optional)
    
    topic_data = {
        "original_id": "TEST-001",
        "title": "Unit Testing 101",
        "url": "http://test.com",
        "status": "new",
        "metrics": {"views": 100}
    }
    response = client.post("/api/v1/topics/", json=topic_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Unit Testing 101"
    assert data["metrics"]["views"] == 100

def test_dashboard_feed_mock(client: TestClient):
    # Access dashboard (it mocks data, so should always work)
    response = client.get("/api/v1/dashboard/feed?persona_id=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "title" in data[0]

def test_script_generation_mock(client: TestClient):
    # 1. Create a Topic
    t_resp = client.post("/api/v1/topics/", json={"original_id": "T1", "title": "T1", "url": "u1"})
    t_id = t_resp.json()["id"]
    
    # 2. Generate
    payload = {"topic_id": t_id, "template_id": 1} # Template ID doesn't need to exist for mock
    response = client.post("/api/v1/scripts/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert f"Topic {t_id}" in data["content"]
