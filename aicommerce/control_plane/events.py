"""In-process Event Bus — pub/sub so agents react to events instead of polling.

PARTIAL relative to the master context's full event list (order.created,
inventory.low, etc.) — those are just string event types here; nothing yet
publishes real commerce events because no store is connected.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable


@dataclass
class Event:
    type: str
    payload: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[[Event], None]]] = defaultdict(list)
        self._log: list[Event] = []

    def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        self._subscribers[event_type].append(handler)

    def publish(self, event_type: str, payload: dict | None = None) -> Event:
        event = Event(type=event_type, payload=payload or {})
        self._log.append(event)
        for handler in self._subscribers.get(event_type, []):
            handler(event)
        return event

    def history(self, event_type: str | None = None) -> list[Event]:
        if event_type is None:
            return list(self._log)
        return [e for e in self._log if e.type == event_type]
