from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "capture-console"))

from app.store import CaptureStore


def test_capture_store_preserves_raw_bytes_and_metadata(tmp_path: Path) -> None:
    store = CaptureStore(tmp_path / "sessions")
    base = {"device": "tecnohead-meter-reader", "boot_id": "boot-1", "session": 1}
    store.ingest({**base, "type": "session_start"})
    store.ingest({**base, "type": "frame", "sequence": 1, "timestamp_ms": 10, "length": 4, "baud": 9600, "parity": "Nenhuma", "data_bits": 8, "stop_bits": 1, "hex": "00FF7E0A"})
    store.ingest({**base, "type": "marker", "sequence": 2, "timestamp_ms": 20})
    session = store.list_sessions()[0]
    key = str(session["key"])
    assert (store.export_path(key, "bin").read_bytes()) == bytes.fromhex("00FF7E0A")
    jsonl = store.export_path(key, "jsonl").read_text(encoding="utf-8").splitlines()
    assert json.loads(jsonl[1])["hex"] == "00FF7E0A"
    assert store.export_path(key, "csv").read_text(encoding="utf-8").count("\n") >= 3


def test_sequence_gap_is_explicit(tmp_path: Path) -> None:
    store = CaptureStore(tmp_path / "sessions")
    base = {"device": "tecnohead-meter-reader", "boot_id": "boot-2", "session": 3, "type": "frame", "timestamp_ms": 10, "length": 1, "baud": 9600, "parity": "Nenhuma", "data_bits": 8, "stop_bits": 1, "hex": "55"}
    store.ingest({**base, "sequence": 1})
    result = store.ingest({**base, "sequence": 3})
    assert result["accepted"] is True
    assert result["record"]["sequence_gap"] == 1
    assert result["session"]["incomplete"] is True
