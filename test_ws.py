import asyncio
import websockets

async def listen():
    async with websockets.connect("ws://127.0.0.1:8000/ws") as websocket:
        print("Connected to WebSocket server")
        while True:
            try:
                message = await websocket.recv()
                print(f"Received: {message}")
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed")
                break

asyncio.run(listen())