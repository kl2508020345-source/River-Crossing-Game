from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Level:
    level_id: int
    name_key: str
    timer_seconds: int
    boat_cross_seconds: float
    time_score_multiplier: int
    move_penalty: int

