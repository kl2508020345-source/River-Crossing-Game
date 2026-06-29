from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Timer:
    total_seconds: float
    remaining_seconds: float
    running: bool = False
    paused: bool = False

    @classmethod
    def create(cls, total_seconds: float) -> "Timer":
        total = float(total_seconds)
        return cls(total_seconds=total, remaining_seconds=total, running=False, paused=False)

    def reset(self, total_seconds: float | None = None) -> None:
        if total_seconds is not None:
            self.total_seconds = float(total_seconds)
        self.remaining_seconds = float(self.total_seconds)
        self.running = False
        self.paused = False

    def start(self) -> None:
        self.running = True
        self.paused = False

    def set_paused(self, paused: bool) -> None:
        self.paused = paused

    def update(self, dt: float) -> None:
        if not self.running or self.paused:
            return
        self.remaining_seconds = max(0.0, self.remaining_seconds - float(dt))

    def is_expired(self) -> bool:
        return self.remaining_seconds <= 0.0

    def format_mm_ss(self) -> str:
        total = int(self.remaining_seconds + 0.999)
        mm = total // 60
        ss = total % 60
        return f"{mm:02d}:{ss:02d}"

