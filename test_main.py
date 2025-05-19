import pytest
from fastapi.testclient import TestClient
from main import app, reset_state
import json

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_app_state():
    """Reset the application state before each test"""
    reset_state()
    yield

def test_root_endpoint():
    """Test the root endpoint returns the index.html file"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"

def test_register_team():
    """Test team registration functionality"""
    # Test successful registration
    response = client.post("/register_team", json={"team_name": "Team A"})
    assert response.status_code == 200
    assert response.json() == {"message": "Team Team A registered successfully"}

    # Test duplicate team name
    response = client.post("/register_team", json={"team_name": "Team A"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Team name already taken"

    # Test maximum teams limit
    for i in range(2, 5):
        response = client.post("/register_team", json={"team_name": f"Team {i}"})
        assert response.status_code == 200

    response = client.post("/register_team", json={"team_name": "Team 5"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Maximum number of teams reached"

def test_get_status():
    """Test the status endpoint"""
    # Test initial status
    response = client.get("/get_status")
    assert response.status_code == 200
    data = response.json()
    assert data["round"] == 1
    assert data["pick"] == 0
    assert data["next_team"] is None
    assert data["registered_teams"] == []
    assert data["draft_started"] is False
    assert data["can_start_draft"] is False

    # Test status after registering teams
    client.post("/register_team", json={"team_name": "Team A"})
    response = client.get("/get_status")
    data = response.json()
    assert "Team A" in data["registered_teams"]
    assert data["can_start_draft"] is False

def test_start_draft():
    """Test starting the draft"""
    # Test starting draft without enough teams
    response = client.post("/start_draft")
    assert response.status_code == 400
    assert response.json()["detail"] == "Need exactly 4 teams to start"

    # Register required teams
    for i in range(4):
        client.post("/register_team", json={"team_name": f"Team {i}"})

    # Test successful draft start
    response = client.post("/start_draft")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "order" in data
    assert len(data["order"]) == 4

    # Test starting draft when already started
    response = client.post("/start_draft")
    assert response.status_code == 400
    assert response.json()["detail"] == "Draft has already started"

def test_pick_player():
    """Test making player picks"""
    # Register teams and start draft
    for i in range(4):
        client.post("/register_team", json={"team_name": f"Team {i}"})
    client.post("/start_draft")

    # Get the first team in draft order
    status = client.get("/get_status").json()
    first_team = status["next_team"]

    # Test successful pick
    response = client.post(f"/pick_player/{first_team}/Player 1")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "next_team" in data

    # Get updated status after first pick
    status = client.get("/get_status").json()
    next_team = status["next_team"]

    # Test picking out of turn
    wrong_team = next(team for team in status["registered_teams"] if team != next_team)
    response = client.post(f"/pick_player/{wrong_team}/Player 2")
    assert response.status_code == 400
    assert response.json()["detail"] == "Not your turn!"

    # Test picking same player again with the correct team
    response = client.post(f"/pick_player/{next_team}/Player 1")
    assert response.status_code == 400
    assert response.json()["detail"] == "Player not available!"

def test_register_team_after_draft_start():
    """Test registering team after draft has started"""
    # Register teams and start draft
    for i in range(4):
        client.post("/register_team", json={"team_name": f"Team {i}"})
    client.post("/start_draft")

    # Try to register another team
    response = client.post("/register_team", json={"team_name": "Team 5"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Draft has already started"

def test_register_team_duplicate_and_after_start():
    # Register a team
    client.post("/register_team", json={"team_name": "Team X"})
    # Try to register the same team again
    resp = client.post("/register_team", json={"team_name": "Team X"})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Team name already taken"
    # Fill up teams and start draft
    for i in range(1, 4):
        client.post("/register_team", json={"team_name": f"Team {i}"})
    client.post("/start_draft")
    # Try to register after draft started
    resp = client.post("/register_team", json={"team_name": "Team Y"})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Draft has already started"

def test_pick_player_errors():
    # Not started
    resp = client.post("/pick_player/Team 0/Player 1")
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Draft has not started"
    # Start draft
    for i in range(4):
        client.post("/register_team", json={"team_name": f"Team {i}"})
    client.post("/start_draft")
    # Not your turn
    status = client.get("/get_status").json()
    next_team = status["next_team"]
    wrong_team = next(team for team in status["registered_teams"] if team != next_team)
    resp = client.post(f"/pick_player/{wrong_team}/Player 2")
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Not your turn!"
    # Player not available
    client.post(f"/pick_player/{next_team}/Player 1")
    status = client.get("/get_status").json()
    next_team2 = status["next_team"]
    resp = client.post(f"/pick_player/{next_team2}/Nonexistent Player")
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Player not available!"

def test_start_draft_wrong_team_count():
    # Too few teams
    for i in range(3):
        client.post("/register_team", json={"team_name": f"Team {i}"})
    resp = client.post("/start_draft")
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Need exactly 4 teams to start"
    reset_state()
    # Too many teams
    for i in range(5):
        client.post("/register_team", json={"team_name": f"Team {i}"})
    resp = client.post("/start_draft")
    assert resp.status_code == 400
    # Should still say need exactly 4 teams
    assert "Need exactly 4 teams" in resp.json()["detail"] or "Maximum number of teams" in resp.json()["detail"]

def test_reset_state():
    # Register teams and start draft
    for i in range(4):
        client.post("/register_team", json={"team_name": f"Team {i}"})
    client.post("/start_draft")
    reset_state()
    # After reset, should be able to register again
    resp = client.post("/register_team", json={"team_name": "Team X"})
    assert resp.status_code == 200
    # State should be clean
    status = client.get("/get_status").json()
    assert status["registered_teams"] == ["Team X"]
    assert status["draft_started"] is False
    assert status["can_start_draft"] is False

def test_draft_order_and_rounds():
    # Register and start
    for i in range(4):
        client.post("/register_team", json={"team_name": f"Team {i}"})
    client.post("/start_draft")
    # Simulate a full round of picks
    for _ in range(4):
        status = client.get("/get_status").json()
        team = status["next_team"]
        player = f"Player {_+1}"
        resp = client.post(f"/pick_player/{team}/{player}")
        assert resp.status_code == 200
    # After 4 picks, round should increment
    status = client.get("/get_status").json()
    assert status["round"] == 2

# def test_websocket_connection():
#     """Test WebSocket connection and message handling"""
#     with client.websocket_connect("/ws") as websocket:
#         # Test that we can connect
#         assert websocket is not None
        
#         # Test receiving initial state
#         data = json.loads(websocket.receive_text())
#         assert "registered_teams" in data
#         assert "draft_started" in data
#         assert "next_team" in data
#         assert "can_start_draft" in data
        
#         # Close the connection
#         websocket.close() 