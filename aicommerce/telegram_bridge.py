"""Telegram bridge — talk to the real AI CEO from anywhere, no shared network
or VPN required. Telegram's servers are the relay: this process only makes
outbound HTTPS calls (long polling `getUpdates`), so nothing needs to be
exposed, port-forwarded, or reachable from outside — it works the same
whether this PC is on home WiFi, a different network, or behind any NAT.

Security model: a bot token alone is not enough to control the real CEO.
Until `TELEGRAM_ALLOWED_CHAT_ID` is set, the bridge runs in "bootstrap mode":
it tells whoever messages it their chat_id and does NOT forward anything to
the CEO. Once that id is set in `.env` (restart required), only messages
from that exact chat_id ever reach `CEOService.chat()` — everyone else is
silently ignored. This is the single-operator model already used by the
CEO Console's token auth, applied to a channel that has no token of its own.
"""
from __future__ import annotations

import logging
import threading
import time
from typing import Optional

import requests

from aicommerce import config

logger = logging.getLogger("telegram_bridge")

_API_BASE = "https://api.telegram.org/bot{token}"
_POLL_TIMEOUT_SECONDS = 30
_REQUEST_TIMEOUT_SECONDS = _POLL_TIMEOUT_SECONDS + 10


class TelegramBridge:
    def __init__(self, system, token: Optional[str] = None, allowed_chat_id: Optional[str] = None) -> None:
        self.system = system
        self.token = token if token is not None else config.TELEGRAM_BOT_TOKEN
        self.allowed_chat_id = allowed_chat_id if allowed_chat_id is not None else config.TELEGRAM_ALLOWED_CHAT_ID
        self._base = _API_BASE.format(token=self.token)
        self._offset = 0
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    @property
    def configured(self) -> bool:
        return bool(self.token)

    @property
    def locked_down(self) -> bool:
        """True once a specific chat_id is the only one allowed through."""
        return bool(self.allowed_chat_id)

    # ------------------------------------------------------------------
    def start(self) -> None:
        if not self.configured:
            logger.info("TELEGRAM_BOT_TOKEN not set — Telegram bridge not starting")
            return
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._poll_loop, name="telegram-bridge", daemon=True)
        self._thread.start()
        logger.info("Telegram bridge started (locked_down=%s)", self.locked_down)

    def stop(self) -> None:
        self._stop.set()

    # ------------------------------------------------------------------
    def _poll_loop(self) -> None:
        while not self._stop.is_set():
            try:
                updates = self._get_updates()
            except Exception as exc:  # noqa: BLE001 — never let a transient network error kill the bridge
                logger.warning("Telegram getUpdates failed: %s", exc)
                time.sleep(5)
                continue
            for update in updates:
                self._offset = max(self._offset, update["update_id"] + 1)
                try:
                    self._handle_update(update)
                except Exception as exc:  # noqa: BLE001 — one bad update must not kill the loop
                    logger.exception("Error handling Telegram update: %s", exc)

    def _get_updates(self) -> list[dict]:
        resp = requests.get(
            f"{self._base}/getUpdates",
            params={"offset": self._offset, "timeout": _POLL_TIMEOUT_SECONDS},
            timeout=_REQUEST_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        data = resp.json()
        if not data.get("ok"):
            raise RuntimeError(f"Telegram API error: {data}")
        return data.get("result", [])

    def _handle_update(self, update: dict) -> None:
        message = update.get("message")
        if not message or "text" not in message:
            return
        chat_id = str(message["chat"]["id"])
        text = message["text"]

        if not self.locked_down:
            self._send(
                chat_id,
                f"Bootstrap: tu chat_id es {chat_id}\n\n"
                "Pon esto en ai-commerce-os/.env y reinicia el servidor para activar el acceso:\n"
                f"TELEGRAM_ALLOWED_CHAT_ID={chat_id}\n\n"
                "Hasta entonces no reenvío mensajes al CEO real, por seguridad.",
            )
            return

        if chat_id != self.allowed_chat_id:
            return  # silently ignore anyone who isn't the locked-down owner

        if text.strip().lower() in ("/start", "/help"):
            self._send(chat_id, "CEO en línea. Escríbeme como le escribirías a un director de operaciones.")
            return

        turn = self.system.ceo.chat(text)
        self._send(chat_id, turn.content or "(sin respuesta)")

    def _send(self, chat_id: str, text: str) -> None:
        # Telegram caps messages at 4096 chars -- split rather than truncate
        # silently, since truncating a CEO report would hide information.
        for i in range(0, len(text), 4000):
            chunk = text[i : i + 4000]
            requests.post(
                f"{self._base}/sendMessage",
                json={"chat_id": chat_id, "text": chunk},
                timeout=15,
            )
