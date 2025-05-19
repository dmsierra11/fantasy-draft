import asyncio
import websockets
import json
import pytest

mock_draft_data = {
    "round": 1,
    "pick": 0,
    "next_team": "Team A",
    "remaining_players": [f"Player {i}" for i in range(1, 21)],
    "draft_results": {"Team A": [], "Team B": [], "Team C": [], "Team D": []}
}

async def mock_server(websocket, path):
    await websocket.send(json.dumps(mock_draft_data))
    try:
        for _ in range(3):  # send 3 updates then stop
            await asyncio.sleep(0.5)
            mock_draft_data["pick"] += 1
            if mock_draft_data["pick"] % 4 == 0:
                mock_draft_data["round"] += 1
            await websocket.send(json.dumps(mock_draft_data))
    except websockets.exceptions.ConnectionClosed:
        pass

async def run_test_client():
    async with websockets.connect("ws://localhost:8765") as websocket:
        messages = []
        for _ in range(4):  # receive 1 initial + 3 updates
            message = await websocket.recv()
            data = json.loads(message)
            messages.append(data)
        return messages

@pytest.mark.asyncio
async def test_websocket_draft_flow():
    server = await websockets.serve(mock_server, "localhost", 8765)
    await asyncio.sleep(0.1)  # give server a moment to start

    try:
        messages = await run_test_client()
        assert len(messages) == 4
        assert all("round" in msg for msg in messages)
    finally:
        server.close()
        await server.wait_closed()
