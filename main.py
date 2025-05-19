from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import random
from typing import List, Dict, Set
from pydantic import BaseModel

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files at /static path
app.mount("/static", StaticFiles(directory="static"), name="static")

class TeamRegistration(BaseModel):
    team_name: str

# Global state
MAX_TEAMS = 4
registered_teams: Set[str] = set()
players = [f"Player {i}" for i in range(1, 21)]  # Example player pool
rounds = 5

# Draft state
draft_order: List[str] = []
reverse_order: List[str] = []
draft_results: Dict[str, List[str]] = {}
current_round = 1
current_pick = 0
ws_connections: List[WebSocket] = []  # Store WebSocket connections
draft_started = False

def reset_state():
    """Reset all global state variables to their initial values."""
    global registered_teams, players, draft_order, reverse_order, draft_results
    global current_round, current_pick, ws_connections, draft_started
    
    registered_teams.clear()
    players = [f"Player {i}" for i in range(1, 21)]
    draft_order = []
    reverse_order = []
    draft_results = {}
    current_round = 1
    current_pick = 0
    ws_connections = []
    draft_started = False

@app.get("/")
async def root():
    """Serve the demo page at the root URL"""
    return FileResponse("static/index.html")

@app.post("/register_team")
async def register_team(team: TeamRegistration):
    """Register a new team"""
    if draft_started:
        raise HTTPException(status_code=400, detail="Draft has already started")
    
    if len(registered_teams) >= MAX_TEAMS:
        raise HTTPException(status_code=400, detail="Maximum number of teams reached")
    
    if team.team_name in registered_teams:
        raise HTTPException(status_code=400, detail="Team name already taken")
    
    registered_teams.add(team.team_name)
    await notify_clients()
    return {"message": f"Team {team.team_name} registered successfully"}

@app.get("/get_status")
async def get_status():
    """Get current draft status"""
    return {
        "round": current_round,
        "pick": current_pick,
        "next_team": get_next_team() if draft_started else None,
        "registered_teams": list(registered_teams),
        "draft_started": draft_started,
        "can_start_draft": len(registered_teams) == MAX_TEAMS and not draft_started
    }

@app.post("/start_draft")
async def start_draft():
    """Start the draft"""
    global draft_started, draft_order, reverse_order, draft_results, current_round, current_pick
    
    if len(registered_teams) != MAX_TEAMS:
        raise HTTPException(status_code=400, detail="Need exactly 4 teams to start")
    
    if draft_started:
        raise HTTPException(status_code=400, detail="Draft has already started")
    
    draft_started = True
    draft_order = random.sample(list(registered_teams), len(registered_teams))
    reverse_order = draft_order[::-1]
    draft_results = {team: [] for team in registered_teams}
    current_round = 1
    current_pick = 0
    
    await notify_clients()
    return {"message": "Draft started", "order": draft_order}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    ws_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        ws_connections.remove(websocket)

def get_next_team():
    """Returns the next team to pick."""
    if not draft_started:
        return None
    draft_sequence = draft_order if current_round % 2 != 0 else reverse_order
    return draft_sequence[current_pick % len(registered_teams)]

@app.post("/pick_player/{team}/{player}")
async def pick_player(team: str, player: str):
    """Make a player pick"""
    global current_round, current_pick

    if not draft_started:
        raise HTTPException(status_code=400, detail="Draft has not started")
    
    if team != get_next_team():
        raise HTTPException(status_code=400, detail="Not your turn!")

    if player not in players:
        raise HTTPException(status_code=400, detail="Player not available!")

    # Assign player to team
    draft_results[team].append(player)
    players.remove(player)

    # Move to next pick
    current_pick += 1
    if current_pick % len(registered_teams) == 0:
        current_round += 1

    # Notify all clients about the new pick
    await notify_clients()

    return {"message": f"{team} picked {player}", "next_team": get_next_team()}

async def notify_clients():
    """Sends draft updates to all connected clients."""
    for ws in ws_connections:
        await ws.send_json({
            "round": current_round,
            "pick": current_pick,
            "next_team": get_next_team(),
            "remaining_players": players,
            "draft_results": draft_results,
            "registered_teams": list(registered_teams),
            "draft_started": draft_started,
            "can_start_draft": len(registered_teams) == MAX_TEAMS and not draft_started
        })
