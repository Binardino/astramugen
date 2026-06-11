import math
import pytest
from simulation.physics.kepler import KeplerOrbit

def test_position_at_zero_angle():
    orbit = KeplerOrbit(semi_major_axis=5.0, speed=1.0)
    x, y, z = orbit.position_at(0.0)
    assert abs(x - 5.0) < 1e-9
    assert abs(y) < 1e-9
    assert abs(z) < 1e-9

def test_position_at_quarter_turn():
    orbit = KeplerOrbit(semi_major_axis=5.0, speed=1.0)
    x, y, z = orbit.position_at(math.pi / 2)
    assert abs(x) < 1e-9
    assert abs(z - 5.0)  < 1e-9

def test_radius_preserved_at_any_angle():
    orbit = KeplerOrbit(semi_major_axis=5.0, speed=1.0)
    for angle in [0.0, 0.5, 1.2, math.pi, 2 * math.pi - 0.1]:
        x, y, z = orbit.position_at(angle)
        r = math.sqrt(x ** 2 + z ** 2)
        assert abs(r - 5.0) < 1e-9, f"radius wrong at angle={angle}: got {r}"

def test_advance_increments_time():
    orbit = KeplerOrbit(semi_major_axis=5.0, speed=2.0)
    orbit.advance(1.0)
    assert abs(orbit.time - 2.0) < 1e-9


def test_advance_speed_scales_time():
    orbit = KeplerOrbit(semi_major_axis=5.0, speed=3.0)
    orbit.advance(0.5)
    assert abs(orbit.time - 1.5) < 1e-9        
