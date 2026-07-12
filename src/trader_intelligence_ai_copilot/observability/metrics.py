"""Dependency-free in-process counters and duration metrics."""

from collections import defaultdict
from contextlib import contextmanager
from threading import Lock
from time import perf_counter
from collections.abc import Iterator


class MetricsRegistry:
    def __init__(self) -> None:
        self._counters: defaultdict[str, float] = defaultdict(float)
        self._durations: defaultdict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def increment(self, name: str, value: float = 1) -> None:
        with self._lock:
            self._counters[name] += value

    def observe(self, name: str, duration_ms: float) -> None:
        with self._lock:
            self._durations[name].append(duration_ms)

    @contextmanager
    def timer(self, name: str) -> Iterator[None]:
        started = perf_counter()
        try:
            yield
        finally:
            self.observe(name, (perf_counter() - started) * 1000)

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            durations = {
                name: {
                    "count": len(values),
                    "average_ms": sum(values) / len(values),
                    "maximum_ms": max(values),
                }
                for name, values in self._durations.items()
                if values
            }
            return {"counters": dict(self._counters), "durations": durations}

    def reset(self) -> None:
        with self._lock:
            self._counters.clear()
            self._durations.clear()


metrics = MetricsRegistry()
