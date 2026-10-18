from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

from .models import utc_now
from .mqtt_bridge import SupervisorMqttBridge
from .store import CaptureStore

app = FastAPI(title="TecnoHead Meter Reader — Console", docs_url="/api/docs", redoc_url=None)
store = CaptureStore(Path(os.getenv("CAPTURE_ROOT", "/data/sessions")))


async def ingest_message(message: dict[str, object]) -> None:
    store.ingest(message)


bridge = SupervisorMqttBridge(os.getenv("SUPERVISOR_TOKEN"), ingest_message)
web_root = Path(__file__).resolve().parent.parent / "web"


@app.on_event("startup")
async def startup() -> None:
    store.load_existing()
    await bridge.start()


@app.on_event("shutdown")
async def shutdown() -> None:
    await bridge.stop()


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return (web_root / "index.html").read_text(encoding="utf-8")


@app.get("/static/{asset:path}")
async def static_asset(asset: str) -> FileResponse:
    path = (web_root / "static" / asset).resolve()
    if not str(path).startswith(str((web_root / "static").resolve())) or not path.is_file():
        raise HTTPException(status_code=404, detail="arquivo não encontrado")
    return FileResponse(path)


@app.get("/api/health")
async def health() -> dict[str, object]:
    return {"ok": True, "service": "tecnohead-meter-reader-console", "time": utc_now()}


@app.get("/api/status")
async def status() -> dict[str, object]:
    return {"mqtt": bridge.status(), "capture": store.status()}


@app.get("/api/sessions")
async def sessions() -> list[dict[str, object]]:
    return store.list_sessions()


@app.get("/api/recent")
async def recent() -> list[dict[str, object]]:
    return store.recent_records()


@app.get("/api/sessions/{key}/{extension}")
async def export_session(key: str, extension: str) -> FileResponse:
    if extension not in {"bin", "jsonl", "csv"}:
        raise HTTPException(status_code=400, detail="formato de exportação inválido")
    try:
        path = store.export_path(key, extension)
    except (FileNotFoundError, ValueError):
        raise HTTPException(status_code=404, detail="sessão ou arquivo não encontrado")
    return FileResponse(path, filename=path.name, media_type="application/octet-stream")


async def _publish(command: str, device: str = "tecnohead-meter-reader") -> dict[str, object]:
    published = await bridge.publish_command(device, command)
    if not published:
        raise HTTPException(status_code=503, detail="MQTT local indisponível; comando não enviado")
    return {"ok": True, "command": command}


@app.post("/api/command/{command}")
async def command(command: str) -> dict[str, object]:
    if command not in {"start", "stop", "marker", "clear", "zero"}:
        raise HTTPException(status_code=400, detail="comando não permitido")
    return await _publish(command)
