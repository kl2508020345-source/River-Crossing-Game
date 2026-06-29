from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
from typing import Deque, Dict, List, Optional


@dataclass
class Ripple:
    x: float
    y: float
    radius: float
    max_radius: float
    alpha: float
    growth: float

    def update(self, dt: float) -> None:
        self.radius = min(self.max_radius, self.radius + self.growth * dt)
        self.alpha = max(0.0, self.alpha - 95.0 * dt)

    def alive(self) -> bool:
        return self.alpha > 1.0 and self.radius < self.max_radius


@dataclass
class RiverMetrics:
    water_level: float
    flow_rate: float
    temperature: float
    quality_index: float
    anomaly_score: float
    synced: bool


@dataclass
class RiverPreferences:
    season: str = "spring"
    show_mist: bool = True
    show_history: bool = True
    flood_mode: bool = False
    sync_enabled: bool = True
    flow_adjustment: float = 0.0
    show_panel: bool = True


class RiverSystem:
    SEASONS: List[str] = ["spring", "summer", "autumn", "winter"]

    def __init__(self, save_path: Path) -> None:
        self.save_path = save_path
        self.preferences = self._load_preferences()
        self.visual_time = 0.0
        self.sync_clock = 0.0
        self.metrics = RiverMetrics(
            water_level=55.0,
            flow_rate=18.0,
            temperature=21.0,
            quality_index=88.0,
            anomaly_score=0.0,
            synced=True,
        )
        self.history: Deque[RiverMetrics] = deque(maxlen=180)
        self.alert_key: Optional[str] = None
        self.alert_text: str = ""
        self.ripples: List[Ripple] = []
        self._push_history()

    def _load_preferences(self) -> RiverPreferences:
        if not self.save_path.exists():
            return RiverPreferences()
        try:
            data = json.loads(self.save_path.read_text(encoding="utf-8"))
            return RiverPreferences(**data)
        except Exception:
            return RiverPreferences()

    def save_preferences(self) -> None:
        self.save_path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(asdict(self.preferences), indent=2)
        temp = self.save_path.with_suffix(".tmp")
        temp.write_text(payload, encoding="utf-8")
        temp.replace(self.save_path)

    def current_season_index(self) -> int:
        return self.SEASONS.index(self.preferences.season)

    def cycle_season(self) -> None:
        idx = (self.current_season_index() + 1) % len(self.SEASONS)
        self.preferences.season = self.SEASONS[idx]
        self.save_preferences()

    def toggle_mist(self) -> None:
        self.preferences.show_mist = not self.preferences.show_mist
        self.save_preferences()

    def toggle_history(self) -> None:
        self.preferences.show_history = not self.preferences.show_history
        self.save_preferences()

    def toggle_flood_mode(self) -> None:
        self.preferences.flood_mode = not self.preferences.flood_mode
        self.save_preferences()

    def toggle_sync(self) -> None:
        self.preferences.sync_enabled = not self.preferences.sync_enabled
        self.metrics.synced = self.preferences.sync_enabled
        self.save_preferences()

    def toggle_panel(self) -> None:
        self.preferences.show_panel = not self.preferences.show_panel
        self.save_preferences()

    def adjust_flow(self, delta: float) -> None:
        self.preferences.flow_adjustment = max(-10.0, min(10.0, self.preferences.flow_adjustment + delta))
        self.save_preferences()

    def add_ripple(self, x: float, y: float, strength: float = 1.0) -> None:
        self.ripples.append(
            Ripple(
                x=x,
                y=y,
                radius=12.0,
                max_radius=40.0 + 30.0 * strength,
                alpha=165.0,
                growth=55.0 + 20.0 * strength,
            )
        )

    def _seasonal_offsets(self) -> Dict[str, float]:
        return {
            "spring": 6.0,
            "summer": -3.0,
            "autumn": 2.0,
            "winter": 9.0,
        }

    def _seasonal_temp(self) -> Dict[str, float]:
        return {
            "spring": 20.0,
            "summer": 27.0,
            "autumn": 18.0,
            "winter": 11.0,
        }

    def _push_history(self) -> None:
        self.history.append(
            RiverMetrics(
                water_level=self.metrics.water_level,
                flow_rate=self.metrics.flow_rate,
                temperature=self.metrics.temperature,
                quality_index=self.metrics.quality_index,
                anomaly_score=self.metrics.anomaly_score,
                synced=self.metrics.synced,
            )
        )

    def update(self, dt: float) -> None:
        self.visual_time += dt
        self.sync_clock += dt

        season_level = self._seasonal_offsets()[self.preferences.season]
        season_temp = self._seasonal_temp()[self.preferences.season]
        wave = math.sin(self.visual_time * 0.7) * 4.0 + math.sin(self.visual_time * 1.9) * 1.5
        micro = math.sin(self.visual_time * 0.23) * 1.3
        flood_bonus = 24.0 if self.preferences.flood_mode else 0.0
        flow_bias = self.preferences.flow_adjustment * 2.0

        self.metrics.water_level = max(18.0, min(98.0, 52.0 + season_level + wave + flood_bonus + flow_bias))
        self.metrics.flow_rate = max(4.0, min(60.0, 18.0 + self.preferences.flow_adjustment * 2.4 + wave * 0.8 + flood_bonus * 0.65))
        self.metrics.temperature = max(2.0, min(35.0, season_temp + micro + self.preferences.flow_adjustment * 0.15))

        quality_drop = max(0.0, self.metrics.flow_rate - 26.0) * 0.85 + flood_bonus * 0.55
        self.metrics.quality_index = max(20.0, min(98.0, 91.0 - quality_drop + math.sin(self.visual_time * 0.45) * 2.8))

        anomaly = 0.0
        if self.metrics.water_level >= 82.0:
            anomaly += (self.metrics.water_level - 82.0) * 1.8
        if self.metrics.flow_rate >= 36.0:
            anomaly += (self.metrics.flow_rate - 36.0) * 1.5
        if self.metrics.quality_index <= 58.0:
            anomaly += (58.0 - self.metrics.quality_index) * 1.7
        self.metrics.anomaly_score = max(0.0, min(100.0, anomaly))

        if self.metrics.anomaly_score >= 35.0:
            if self.metrics.water_level >= 82.0:
                self.alert_key = "flood"
                self.alert_text = "Flood risk rising: water level exceeds safe threshold."
            elif self.metrics.quality_index <= 58.0:
                self.alert_key = "quality"
                self.alert_text = "Water quality anomaly detected: investigate contamination sources."
            else:
                self.alert_key = "flow"
                self.alert_text = "Flow surge anomaly detected: downstream caution advised."
        else:
            self.alert_key = None
            self.alert_text = ""

        if self.preferences.sync_enabled:
            self.metrics.synced = True
        else:
            self.metrics.synced = False

        if self.sync_clock >= 1.0:
            self.sync_clock = 0.0
            self._push_history()

        for ripple in self.ripples:
            ripple.update(dt)
        self.ripples = [r for r in self.ripples if r.alive()]

    def latest_history(self, points: int = 60) -> List[RiverMetrics]:
        if points <= 0:
            return []
        return list(self.history)[-points:]
