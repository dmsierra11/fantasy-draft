from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import random
from typing import List, Dict

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

# Sample league setup
teams = ["Team A", "Team B", "Team C", "Team D"]
players = [f"Player {i}" for i in range(1, 21)]  # Example player pool
rounds = 5

# Draft state
draft_order = random.sample(teams, len(teams))  # Randomize order
reverse_order = draft_order[::-1]
draft_results: Dict[str, List[str]] = {team: [] for team in teams}
current_round = 1
current_pick = 0
ws_connections = []  # Store WebSocket connections

@app.get("/")
async def root():
    """Serve the demo page at the root URL"""
    return FileResponse("static/index.html")

@app.get("/start_draft")
async def start_draft():
    global current_round, current_pick, draft_order, reverse_order, draft_results, players
    current_round = 1
    current_pick = 0
    draft_order = random.sample(teams, len(teams))
    reverse_order = draft_order[::-1]
    draft_results = {team: [] for team in teams}
    players = [f"Player {i}" for i in range(1, 21)]
    return {"message": "Draft started", "order": draft_order}

@app.get("/get_status")
async def get_status():
    return {
        "round": current_round,
        "pick": current_pick,
        "next_team": get_next_team()
    }

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
    current_round, current_pick
    draft_sequence = draft_order if current_round % 2 != 0 else reverse_order
    return draft_sequence[current_pick % len(teams)]

@app.post("/pick_player/{team}/{player}")
async def pick_player(team: str, player: str):
    global current_round, current_pick

    if team != get_next_team():
        return {"error": "Not your turn!"}

    if player not in players:
        return {"error": "Player not available!"}

    # Assign player to team
    draft_results[team].append(player)
    players.remove(player)

    # Move to next pick
    current_pick += 1
    if current_pick % len(teams) == 0:
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
            "draft_order": draft_order
        })
