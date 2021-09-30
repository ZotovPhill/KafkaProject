from re import I
from typing import Dict, List
from fastapi import FastAPI
from starlette.websockets import WebSocket, WebSocketDisconnect
from starlette.responses import HTMLResponse
import socketio
from src.worker.main import Producer


app = FastAPI()
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
asgi_app = socketio.ASGIApp(
    socketio_server=sio, socketio_path="socket.io"
)
app.mount("/sio", asgi_app)

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <label>Item ID: <input type="text" id="itemId" autocomplete="off" value="1"/></label>
            <hr>
            <label>Message: <input type="text" id="messageText" autocomplete="off"/></label>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var user_id = Date.now()
            document.querySelector("#ws-id").textContent = user_id;
            var room_id = document.getElementById("itemId")
            var ws = new WebSocket(`ws://localhost:8000/ws/${room_id.value}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[WebSocket] = {}

    async def connect(self, room_id: str, websocket: WebSocket):
        await websocket.accept()
        if not self.active_connections.get(room_id):
            self.active_connections[room_id] = []    
        self.active_connections[room_id].append(websocket)

    def disconnect(self, room_id: str,  websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            # send info to show it to the client later
            
    async def broadcast(self, room_id: str, message: str):
        for connection in self.active_connections[room_id]:
            await self.send_personal_message(message, connection)

manager = ConnectionManager()

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int):
    print(room_id)
    await manager.connect(room_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(room_id, f"Client # says: {data}")
            producer = Producer("stock_parser", {"room_id": room_id})
            producer.start()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{room_id} left the chat")


@sio.on('packet')
async def chat_message(sid, msg):
    """Receive a chat message and send to all clients"""
    info = msg["data"]["info"]
    await manager.broadcast(msg["data"]["room_id"], f"Client #{sid} says: {info}")

