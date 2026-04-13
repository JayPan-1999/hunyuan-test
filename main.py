import asyncio
import json
from contextlib import suppress
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse


app = FastAPI(title="Realtime Message Viewer")
BASE_DIR = Path(__file__).resolve().parent


class MessageBroker:
    def __init__(self) -> None:
        self.subscribers: list[asyncio.Queue[dict[str, Any]]] = []
        self.latest_message: dict[str, Any] | None = None

    def subscribe(self) -> asyncio.Queue[dict[str, Any]]:
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self.subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[dict[str, Any]]) -> None:
        if queue in self.subscribers:
            self.subscribers.remove(queue)

    async def publish(self, message: dict[str, Any]) -> None:
        self.latest_message = message

        for subscriber in self.subscribers:
            subscriber.put_nowait(message)


broker = MessageBroker()


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.get("/events")
async def event_stream(request: Request) -> StreamingResponse:
    subscriber = broker.subscribe()

    async def stream() -> Any:
        try:
            if broker.latest_message is not None:
                yield f"data: {json.dumps(broker.latest_message, ensure_ascii=False)}\n\n"

            while True:
                if await request.is_disconnected():
                    break

                message = await subscriber.get()
                yield f"data: {json.dumps(message, ensure_ascii=False)}\n\n"
        finally:
            broker.unsubscribe(subscriber)

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@app.post("/publish")
async def publish_message(request: Request) -> JSONResponse:
    payload = await request.json()
    raw_message = str(payload.get("message", "")).strip()

    if not raw_message:
        return JSONResponse({"detail": "message is required"}, status_code=400)

    client = request.client.host if request.client else "unknown"
    message = {"message": raw_message, "client": client}
    await broker.publish(message)

    return JSONResponse({"status": "ok", "data": message})
