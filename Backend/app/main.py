from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json

from app.database import initialize_database
from app.routers import ai, credits, products, stock
from wake import wake_word_service


app = FastAPI(
    title="Kadakaran Basic ERP",
    description="A basic product, stock, and credit management API.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    initialize_database()
    wake_word_service.start()


@app.on_event("shutdown")
def shutdown() -> None:
    wake_word_service.stop()


# The server sends a heartbeat when idle so proxies and the browser can tell a
# quiet connection from a dead one.
WS_HEARTBEAT_SECONDS = 10


@app.websocket("/ws/wake")
async def wake_socket(websocket: WebSocket):
    await websocket.accept()
    queue: asyncio.Queue = asyncio.Queue()
    loop = asyncio.get_running_loop()

    def broadcast(payload):
        loop.call_soon_threadsafe(queue.put_nowait, payload)

    wake_word_service.add_callback(broadcast)

    async def receive_loop():
        while True:
            message = await websocket.receive()
            if message["type"] == "websocket.disconnect":
                return
            audio = message.get("bytes")
            if audio:
                # Model inference runs in a worker thread so it can never block
                # the event loop (which would stall pings and heartbeats).
                await asyncio.to_thread(wake_word_service.process_external_audio, audio)
                continue
            text = message.get("text")
            if text:
                try:
                    command = json.loads(text)
                except ValueError:
                    continue
                if command.get("type") == "start_recording":
                    wake_word_service.start_manual_recording()

    async def send_loop():
        while True:
            try:
                payload = await asyncio.wait_for(queue.get(), timeout=WS_HEARTBEAT_SECONDS)
            except asyncio.TimeoutError:
                payload = {"type": "heartbeat"}
            await websocket.send_json(payload)

    receiver = asyncio.create_task(receive_loop())
    sender = asyncio.create_task(send_loop())
    try:
        await websocket.send_json({
            "type": "status",
            "status": "listening" if wake_word_service.ready else "loading",
        })
        # Whichever side ends first (client left, send failed) ends the session.
        await asyncio.wait({receiver, sender}, return_when=asyncio.FIRST_COMPLETED)
    finally:
        for task in (receiver, sender):
            task.cancel()
        await asyncio.gather(receiver, sender, return_exceptions=True)
        wake_word_service.remove_callback(broadcast)


app.include_router(products.router)
app.include_router(stock.router)
app.include_router(credits.router)
app.include_router(ai.router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "Kadakaran Basic ERP"}
