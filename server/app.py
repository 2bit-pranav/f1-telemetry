from fastapi import FastAPI, WebSocket
from fastapi.websockets import WebSocketDisconnect
from contextlib import asynccontextmanager
import asyncio
from parser import start_telemetry_loop

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"a user was connected. total users = {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"a user was disconnected. total users = {len(self.active_connections)}")

    async def broadcast(self, msg: str):
        for connection in self.active_connections:
            connection.send_text(msg)

manager = ConnectionManager()
telemetry_queue = asyncio.Queue

async def broadcast_from_queue():
    while True:
        json_msg = telemetry_queue.get()
        await manager.broadcast(json_msg)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("### server starting ###")
    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, start_telemetry_loop, telemetry_queue, loop)
    broadcaster_task = asyncio.create_task(broadcast_from_queue())

    yield

    print("### server shutting down ###")
    broadcaster_task.cancel()

app = FastAPI(lifespan=lifespan)

@app.websocket("/ws/race")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)