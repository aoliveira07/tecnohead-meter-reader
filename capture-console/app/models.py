from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Session:
    key: str
    device: str
    boot_id: str
    session: int
    started_at: str
    ended_at: str | None = None
    bytes_written: int = 0
    frames: int = 0
    dropped_records: int = 0
    incomplete: bool = False
    last_sequence: int | None = None
    last_received_at: str | None = None
    path: Path | None = field(default=None, repr=False)

    def as_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "device": self.device,
            "boot_id": self.boot_id,
            "session": self.session,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "bytes_written": self.bytes_written,
            "frames": self.frames,
            "dropped_records": self.dropped_records,
            "incomplete": self.incomplete,
            "last_sequence": self.last_sequence,
            "last_received_at": self.last_received_at,
            "path": str(self.path) if self.path else None,
        }
