from __future__ import annotations

import csv
import json
import logging
import os
import shutil
from collections import deque
from pathlib import Path
from threading import Lock
from typing import Any

from .models import Session, utc_now

LOGGER = logging.getLogger("tecnohead.capture.store")


class CaptureStore:
    """Persist raw bytes on the HAOS data volume, never on ESP flash.

    Each frame is appended to capture.bin in arrival order. JSONL and CSV keep
    the same bytes as hexadecimal plus the UART metadata. Sequence gaps,
    storage limits and malformed records are marked incomplete explicitly.
    """

    def __init__(
        self,
        root: str | Path = "/data/sessions",
        *,
        max_session_bytes: int = 64 * 1024 * 1024,
        max_total_bytes: int = 256 * 1024 * 1024,
        recent_limit: int = 200,
    ) -> None:
        self.root = Path(root)
        self.max_session_bytes = max_session_bytes
        self.max_total_bytes = max_total_bytes
        self.recent: deque[dict[str, Any]] = deque(maxlen=recent_limit)
        self.sessions: dict[str, Session] = {}
        self.lock = Lock()
        self.last_error: str | None = None
        self.last_received_at: str | None = None
        self.messages = 0
        self.dropped_messages = 0
        self.root.mkdir(parents=True, exist_ok=True)

    def _session_key(self, message: dict[str, Any]) -> str:
        device = str(message.get("device", "unknown-device"))
        boot_id = str(message.get("boot_id", "unknown-boot"))
        session = int(message.get("session", 0))
        safe = "".join(character if character.isalnum() or character in "-_" else "_" for character in device)
        return f"{safe}__{boot_id}__{session}"

    def _session_dir(self, key: str) -> Path:
        return self.root / key

    def _load_or_create_session(self, message: dict[str, Any]) -> Session:
        key = self._session_key(message)
        session = self.sessions.get(key)
        if session is not None:
            return session
        directory = self._session_dir(key)
        directory.mkdir(parents=True, exist_ok=True)
        session = Session(
            key=key,
            device=str(message.get("device", "unknown-device")),
            boot_id=str(message.get("boot_id", "unknown-boot")),
            session=int(message.get("session", 0)),
            started_at=str(message.get("received_at", utc_now())),
            path=directory,
        )
        self.sessions[key] = session
        self._write_manifest(session)
        bin_path = directory / "capture.bin"
        jsonl_path = directory / "capture.jsonl"
        csv_path = directory / "capture.csv"
        bin_path.touch(exist_ok=True)
        if not jsonl_path.exists():
            jsonl_path.write_text("", encoding="utf-8")
        if not csv_path.exists():
            with csv_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "received_at",
                        "type",
                        "sequence",
                        "timestamp_ms",
                        "direction",
                        "length",
                        "offset",
                        "baud",
                        "parity",
                        "data_bits",
                        "stop_bits",
                        "hex",
                        "complete",
                    ],
                )
                writer.writeheader()
        return session

    def _total_size(self) -> int:
        total = 0
        for path in self.root.glob("**/*"):
            if path.is_file():
                try:
                    total += path.stat().st_size
                except OSError:
                    continue
        return total

    def _write_manifest(self, session: Session) -> None:
        assert session.path is not None
        (session.path / "manifest.json").write_text(
            json.dumps(session.as_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    def _append_jsonl(self, session: Session, record: dict[str, Any]) -> None:
        assert session.path is not None
        with (session.path / "capture.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")

    def _append_csv(self, session: Session, record: dict[str, Any]) -> None:
        assert session.path is not None
        row = {key: record.get(key, "") for key in [
            "received_at", "type", "sequence", "timestamp_ms", "direction", "length", "offset",
            "baud", "parity", "data_bits", "stop_bits", "hex", "complete",
        ]}
        with (session.path / "capture.csv").open("a", newline="", encoding="utf-8") as handle:
            csv.DictWriter(handle, fieldnames=list(row)).writerow(row)

    def ingest(self, message: dict[str, Any]) -> dict[str, Any]:
        with self.lock:
            self.messages += 1
            received_at = utc_now()
            record = dict(message)
            record["received_at"] = received_at
            message_type = str(record.get("type", "unknown"))
            session = self._load_or_create_session(record)
            if message_type == "session_start":
                session.started_at = received_at
            if message_type == "session_stop":
                session.ended_at = received_at
                self._append_jsonl(session, record)
                self._append_csv(session, record)
                self._write_manifest(session)
                self.recent.appendleft(record)
                self.last_received_at = received_at
                return {"accepted": True, "session": session.as_dict()}

            if message_type == "frame":
                try:
                    sequence = int(record["sequence"])
                    raw = bytes.fromhex(str(record.get("hex", "")))
                except (KeyError, TypeError, ValueError) as exc:
                    self.last_error = f"frame inválido: {exc}"
                    self.dropped_messages += 1
                    session.dropped_records += 1
                    session.incomplete = True
                    self._write_manifest(session)
                    return {"accepted": False, "error": self.last_error}

                if session.last_sequence is not None and sequence != session.last_sequence + 1:
                    gap = max(1, sequence - session.last_sequence - 1)
                    session.dropped_records += gap
                    session.incomplete = True
                    record["sequence_gap"] = gap
                session.last_sequence = sequence
                current_size = session.bytes_written
                if current_size + len(raw) > self.max_session_bytes or self._total_size() + len(raw) > self.max_total_bytes:
                    session.dropped_records += 1
                    session.incomplete = True
                    self.dropped_messages += 1
                    record["complete"] = False
                    record["storage_error"] = "limite de armazenamento atingido"
                    self._append_jsonl(session, record)
                    self._append_csv(session, record)
                    self._write_manifest(session)
                    self.recent.appendleft(record)
                    return {"accepted": False, "error": record["storage_error"]}

                assert session.path is not None
                with (session.path / "capture.bin").open("ab") as handle:
                    handle.write(raw)
                session.bytes_written += len(raw)
                session.frames += 1
                session.last_received_at = received_at
                record["complete"] = True
                record["server_offset"] = current_size
                self._append_jsonl(session, record)
                self._append_csv(session, record)
                self._write_manifest(session)
                self.recent.appendleft(record)
                self.last_received_at = received_at
                return {"accepted": True, "session": session.as_dict(), "record": record}

            self._append_jsonl(session, record)
            self._append_csv(session, record)
            self._write_manifest(session)
            self.recent.appendleft(record)
            self.last_received_at = received_at
            return {"accepted": True, "session": session.as_dict(), "record": record}

    def list_sessions(self) -> list[dict[str, Any]]:
        with self.lock:
            return [session.as_dict() for session in sorted(self.sessions.values(), key=lambda item: item.started_at, reverse=True)]

    def get_session(self, key: str) -> Session | None:
        with self.lock:
            return self.sessions.get(key)

    def recent_records(self) -> list[dict[str, Any]]:
        with self.lock:
            return list(self.recent)

    def status(self) -> dict[str, Any]:
        with self.lock:
            return {
                "messages": self.messages,
                "dropped_messages": self.dropped_messages,
                "last_error": self.last_error,
                "last_received_at": self.last_received_at,
                "sessions": len(self.sessions),
                "storage_bytes": self._total_size(),
                "max_session_bytes": self.max_session_bytes,
                "max_total_bytes": self.max_total_bytes,
                "recent": list(self.recent)[:20],
            }

    def export_path(self, key: str, extension: str) -> Path:
        with self.lock:
            session = self.sessions.get(key)
            if session is None or session.path is None:
                raise FileNotFoundError(key)
            filename = {"bin": "capture.bin", "jsonl": "capture.jsonl", "csv": "capture.csv"}.get(extension)
            if filename is None:
                raise ValueError(extension)
            path = session.path / filename
            if not path.exists():
                raise FileNotFoundError(str(path))
            return path

    def load_existing(self) -> None:
        with self.lock:
            for manifest in self.root.glob("*/manifest.json"):
                try:
                    data = json.loads(manifest.read_text(encoding="utf-8"))
                    session = Session(
                        key=str(data["key"]),
                        device=str(data["device"]),
                        boot_id=str(data["boot_id"]),
                        session=int(data["session"]),
                        started_at=str(data["started_at"]),
                        ended_at=data.get("ended_at"),
                        bytes_written=int(data.get("bytes_written", 0)),
                        frames=int(data.get("frames", 0)),
                        dropped_records=int(data.get("dropped_records", 0)),
                        incomplete=bool(data.get("incomplete", False)),
                        last_sequence=data.get("last_sequence"),
                        last_received_at=data.get("last_received_at"),
                        path=manifest.parent,
                    )
                    self.sessions[session.key] = session
                except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                    LOGGER.warning("manifest inválido ignorado %s: %s", manifest, exc)

    def delete_session(self, key: str) -> None:
        """Delete only through an explicit API call; UI does not expose it in V1."""
        with self.lock:
            session = self.sessions.pop(key, None)
            if session and session.path:
                shutil.rmtree(session.path, ignore_errors=False)
