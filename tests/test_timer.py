from game.timer import Timer


def test_timer_counts_down_and_expires() -> None:
    t = Timer.create(3)
    t.start()
    t.update(1.2)
    assert 1.7 < t.remaining_seconds < 1.9
    t.update(2.0)
    assert t.is_expired()
    assert t.remaining_seconds == 0.0


def test_timer_pause() -> None:
    t = Timer.create(5)
    t.start()
    t.set_paused(True)
    t.update(2.0)
    assert t.remaining_seconds == 5.0
    t.set_paused(False)
    t.update(1.0)
    assert 3.9 < t.remaining_seconds < 4.1

