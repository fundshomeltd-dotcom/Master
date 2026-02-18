from src.analytics.engine import is_volume_spike, moving_average


def test_moving_average():
    assert moving_average([1, 2, 3, 4, 5], 3) == 4


def test_volume_spike_detection():
    assert is_volume_spike(1600, 1000) == 1.0
    assert is_volume_spike(1400, 1000) == 0.0
