#!/usr/bin/env python3
"""Gerador seguro de tráfego UART TTL para a bancada.

O modo padrão não abre nenhuma porta e apenas imprime o vetor esperado. Para
transmitir, use explicitamente --send --interface ttl-3v3 --port COMx. O
programa não aceita um modo RS232 e não deve ser ligado ao Nansen.
"""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass


DEFAULT_FRAMES = (
    bytes([0x55, 0xAA, 0x00, 0x7E, 0x01, 0x03, 0x0D, 0x0A]),
    b"TECNOHEAD UART LAB\r\n",
    bytes([0x00, 0x01, 0x02, 0x7E, 0x81, 0x00, 0xFF]),
)


@dataclass(frozen=True)
class SimulatorConfig:
    baud: int
    parity: str
    data_bits: int
    stop_bits: int
    gap_ms: int
    repeat: int


def build_frames(hex_payload: str | None) -> list[bytes]:
    if not hex_payload:
        return list(DEFAULT_FRAMES)
    cleaned = "".join(hex_payload.split())
    if len(cleaned) % 2:
        raise ValueError("hex deve conter número par de dígitos")
    try:
        return [bytes.fromhex(cleaned)]
    except ValueError as exc:
        raise ValueError(f"hex inválido: {exc}") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", help="porta serial TTL da bancada, por exemplo COM7")
    parser.add_argument("--send", action="store_true", help="transmite pela porta; sem isso é dry-run")
    parser.add_argument("--interface", choices=["ttl-3v3"], help="confirma somente interface TTL 3,3 V")
    parser.add_argument("--baud", type=int, default=9600)
    parser.add_argument("--parity", choices=["N", "E", "O"], default="N")
    parser.add_argument("--data-bits", type=int, choices=[7, 8], default=8)
    parser.add_argument("--stop-bits", type=int, choices=[1, 2], default=1)
    parser.add_argument("--gap-ms", type=int, default=350, help="intervalo entre grupos")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--hex", dest="hex_payload", help="vetor HEX único, sem prefixos")
    return parser.parse_args()


def send_frames(args: argparse.Namespace, frames: list[bytes], config: SimulatorConfig) -> None:
    if not args.send:
        return
    if not args.port:
        raise SystemExit("--send exige --port COMx")
    if args.interface != "ttl-3v3":
        raise SystemExit("transmissão bloqueada: confirme --interface ttl-3v3")
    try:
        import serial  # type: ignore
    except ImportError as exc:
        raise SystemExit("instale pyserial somente no computador de bancada: python -m pip install pyserial") from exc
    parity = {"N": serial.PARITY_NONE, "E": serial.PARITY_EVEN, "O": serial.PARITY_ODD}[config.parity]
    with serial.Serial(
        args.port,
        baudrate=config.baud,
        bytesize=config.data_bits,
        parity=parity,
        stopbits=config.stop_bits,
        timeout=1,
        write_timeout=1,
    ) as port:
        for _ in range(config.repeat):
            for frame in frames:
                port.write(frame)
                port.flush()
                time.sleep(config.gap_ms / 1000)


def main() -> int:
    args = parse_args()
    if args.gap_ms < 100 or args.repeat < 1:
        raise SystemExit("gap mínimo é 100 ms e repeat deve ser positivo")
    frames = build_frames(args.hex_payload)
    config = SimulatorConfig(args.baud, args.parity, args.data_bits, args.stop_bits, args.gap_ms, args.repeat)
    expected = b"".join(frames * config.repeat)
    print(json.dumps({"mode": "send" if args.send else "dry-run", "config": asdict(config), "frames": [frame.hex(" ").upper() for frame in frames], "expected_hex": expected.hex().upper(), "expected_bytes": len(expected)}, ensure_ascii=False))
    send_frames(args, frames, config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
