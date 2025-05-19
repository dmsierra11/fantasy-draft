import pytest
from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

def test_start_draft():
    response = client.get("/start_draft")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "order" in data
    assert len(data["order"]) == 4  # We have 4 teams

def test_get_status():
    response = client.get("/get_status")
    assert response.status_code == 200
    data = response.json()
    assert "round" in data
    assert "pick" in data
    assert "next_team" in data

def test_pick_player_valid():
    # First get the next team
    status = client.get("/get_status").json()
    next_team = status["next_team"]
    
    # Make a valid pick
    response = client.post(f"/pick_player/{next_team}/Player 1")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "next_team" in data

def test_pick_player_invalid_team():
    # Try to pick with wrong team
    response = client.post("/pick_player/Wrong Team/Player 2")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert data["error"] == "Not your turn!"

def test_pick_player_invalid_player():
    # Get the next team
    status = client.get("/get_status").json()
    next_team = status["next_team"]
    
    # Try to pick non-existent player
    response = client.post(f"/pick_player/{next_team}/Invalid Player")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert data["error"] == "Player not available!"

@pytest.mark.asyncio
async def test_websocket_connection():
    with client.websocket_connect("/ws") as websocket:
        # Test that we can connect
        assert websocket is not None 