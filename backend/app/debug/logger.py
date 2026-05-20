"""Debug logger: in-memory circular buffer for runtime diagnostics."""

from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import ClassVar


@dataclass
class LogEntry:
    timestamp: float
    seq: int
    method: str
    path: str
    status: int
    duration_ms: float
    error: str | None = None


class DebugLog:
    """Thread-safe circular buffer storing the last N request records."""

    _lock: ClassVar[threading.Lock] = threading.Lock()
    _seq: ClassVar[int] = 0
    entries: ClassVar[deque[LogEntry]] = deque(maxlen=5000)

    @classmethod
    def add(
        cls,
        method: str,
        path: str,
        status: int,
        duration_ms: float,
        error: str | None = None,
    ) -> LogEntry:
        with cls._lock:
            cls._seq += 1
            entry = LogEntry(
                timestamp=time.time(),
                seq=cls._seq,
                method=method,
                path=path,
                status=status,
                duration_ms=round(duration_ms, 1),
                error=error,
            )
            cls.entries.append(entry)
            return entry

    @classmethod
    def get_all(cls) -> list[LogEntry]:
        with cls._lock:
            return list(cls.entries)

    @classmethod
    def tail(cls, n: int = 20) -> list[LogEntry]:
        with cls._lock:
            return list(cls.entries)[-n:]

    @classmethod
    def clear(cls) -> None:
        with cls._lock:
            cls.entries.clear()
            cls._seq = 0
