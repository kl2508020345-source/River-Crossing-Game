from pathlib import Path

from game.river_system import RiverSystem


def test_river_system_updates_metrics_and_history(tmp_path: Path) -> None:
    river = RiverSystem(tmp_path / "river.json")
    river.update(1.1)

    assert river.metrics.water_level > 0
    assert river.metrics.flow_rate > 0
    assert len(river.history) >= 2


def test_flood_mode_raises_anomaly_score(tmp_path: Path) -> None:
    river = RiverSystem(tmp_path / "river.json")
    river.toggle_flood_mode()
    river.update(0.5)

    assert river.preferences.flood_mode is True
    assert river.metrics.water_level >= 70.0
    assert river.metrics.anomaly_score > 0.0


def test_flow_adjustment_is_clamped(tmp_path: Path) -> None:
    river = RiverSystem(tmp_path / "river.json")
    for _ in range(30):
        river.adjust_flow(1.0)

    assert river.preferences.flow_adjustment == 10.0

    for _ in range(40):
        river.adjust_flow(-1.0)

    assert river.preferences.flow_adjustment == -10.0


def test_preferences_persist(tmp_path: Path) -> None:
    path = tmp_path / "river.json"
    river = RiverSystem(path)
    river.cycle_season()
    river.toggle_mist()
    river.toggle_history()
    river.toggle_sync()

    loaded = RiverSystem(path)
    assert loaded.preferences.season == "summer"
    assert loaded.preferences.show_mist is False
    assert loaded.preferences.show_history is False
    assert loaded.preferences.sync_enabled is False

