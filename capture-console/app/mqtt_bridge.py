from __future__ import annotations

import asyncio
import json
import logging
import ssl
from collections.abc import Awaitable, Callable
from typing import Any

import aiohttp
import aiomqtt

LOGGER = logging.getLogger("tecnohead.capture.mqtt")


class SupervisorMqttBridge:
    def __init__(self, supervisor_token: str | None, callback: Callable[[dict[str, Any]], Awaitable[None]]) -> None:
        self.supervisor_token = supervisor_token
        self.callback = callback
        self.connected = False
        self.last_error: str | None = None
        self.messages = 0
        self._stop = asyncio.Event()
        self._task: asyncio.Task[None] | None = None
        self._client: aiomqtt.Client | None = None

    async def start(self) -> None:
        self._task = asyncio.create_task(self._run(), name="tecnohead-meter-reader-mqtt")

    async def stop(self) -> None:
        self._stop.set()
        task = self._task
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        self.connected = False
        self._client = None

    async def _get_service(self) -> dict[str, Any] | None:
        if not self.supervisor_token:
            self.last_error = "SUPERVISOR_TOKEN indisponível"
            return None
        timeout = aiohttp.ClientTimeout(total=10)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(
                    "http://supervisor/services/mqtt",
                    headers={"Authorization": f"Bearer {self.supervisor_token}"},
                ) as response:
                    if response.status >= 400:
                        self.last_error = f"Supervisor MQTT HTTP {response.status}"
                        return None
                    payload = await response.json()
        except (aiohttp.ClientError, TimeoutError, json.JSONDecodeError) as exc:
            self.last_error = f"Supervisor MQTT indisponível: {exc}"
            return None
        if isinstance(payload, dict) and isinstance(payload.get("data"), dict):
            payload = payload["data"]
        return payload if isinstance(payload, dict) and payload.get("host") else None

    async def _run(self) -> None:
        delay = 2.0
        while not self._stop.is_set():
            service = await self._get_service()
            if not service:
                self.connected = False
                try:
                    await asyncio.wait_for(self._stop.wait(), timeout=30.0)
                except TimeoutError:
                    continue
                return
            try:
                client_kwargs: dict[str, Any] = {
                    "hostname": str(service["host"]),
                    "port": int(service.get("port", 1883)),
                    "username": service.get("username"),
                    "password": service.get("password"),
                    "identifier": "tecnohead-meter-reader-console",
                }
                if service.get("ssl"):
                    client_kwargs["tls_context"] = ssl.create_default_context()
                client = aiomqtt.Client(**client_kwargs)
                async with client:
                    self._client = client
                    self.connected = True
                    self.last_error = None
                    await client.subscribe("tecnohead/meter-reader/+/capture", qos=1)
                    async for message in client.messages:
                        if self._stop.is_set():
                            return
                        try:
                            payload = bytes(message.payload).decode("utf-8")
                            data = json.loads(payload)
                            if isinstance(data, dict):
                                self.messages += 1
                                await self.callback(data)
                        except (UnicodeDecodeError, json.JSONDecodeError, TypeError) as exc:
                            self.last_error = f"mensagem MQTT inválida: {exc}"
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self.connected = False
                self._client = None
                self.last_error = "broker MQTT indisponível"
                LOGGER.warning("MQTT desconectado: %s", exc)
                try:
                    await asyncio.wait_for(self._stop.wait(), timeout=delay)
                except TimeoutError:
                    delay = min(delay * 2, 60.0)
        self.connected = False
        self._client = None

    async def publish_command(self, device: str, command: str) -> bool:
        client = self._client
        if not self.connected or client is None:
            return False
        topic = f"tecnohead/meter-reader/{device}/command"
        try:
            await client.publish(topic, payload=command, qos=1, retain=False)
            return True
        except Exception as exc:
            self.last_error = f"comando MQTT não publicado: {exc}"
            return False

    def status(self) -> dict[str, Any]:
        return {"connected": self.connected, "last_error": self.last_error, "messages": self.messages}
