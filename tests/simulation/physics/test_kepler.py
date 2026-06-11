"""
Tests for KeplerOrbit — circular orbit math.

Contract under test: given a semi_major_axis (orbital radius) and a speed,
KeplerOrbit must:
  - return a (x, y, z) position on a circle of exactly that radius
  - advance an internal time counter proportionally to speed when advance(dt) is called
"""

import math
import pytest
from simulation.physics.kepler import KeplerOrbit


def test_position_at_zero_angle():
    """At angle=0, the body sits on the positive X axis at distance radius."""
    orbit = KeplerOrbit(semi_major_axis=5.0, speed=1.0)
    x, y, z = orbit.position_at(0.0)
    # cos(0)=1, sin(0)=0  →  expected: (5, 0, 0)
    # 1e-9 tolerance because floating-point trig is never exactly 0
    assert abs(x - 5.0) < 1e-9
    assert abs(y) < 1e-9
    assert abs(z) < 1e-9


def test_position_at_quarter_turn():
    """At angle=π/2 (90°), the body moves from X onto the Z axis."""
    orbit = KeplerOrbit(semi_major_axis=5.0, speed=1.0)
    x, y, z = orbit.position_at(math.pi / 2)
    # cos(π/2)≈0, sin(π/2)=1  →  expected: (0, 0, 5)
    # Catches a common mistake: swapping x and z in the formula
    assert abs(x) < 1e-9
    assert abs(z - 5.0) < 1e-9


def test_radius_preserved_at_any_angle():
    """The distance from origin must equal semi_major_axis at every angle.

    This is the defining property of a circle: r = sqrt(x² + z²) = constant.
    Tested on 5 spread-out angles to avoid hitting a lucky coincidence.
    """
    orbit = KeplerOrbit(semi_major_axis=5.0, speed=1.0)
    for angle in [0.0, 0.5, 1.2, math.pi, 2 * math.pi - 0.1]:
        x, y, z = orbit.position_at(angle)
        r = math.sqrt(x ** 2 + z ** 2)  # Pythagorean distance on the horizontal plane
        assert abs(r - 5.0) < 1e-9, f"radius wrong at angle={angle}: got {r}"


def test_advance_increments_time():
    """advance(dt) must increase the internal time counter by dt * speed."""
    orbit = KeplerOrbit(semi_major_axis=5.0, speed=2.0)
    orbit.advance(1.0)
    # speed=2, dt=1  →  time should be 2.0
    assert abs(orbit.time - 2.0) < 1e-9


def test_advance_speed_scales_time():
    """Higher speed means the orbit time advances faster for the same dt."""
    orbit = KeplerOrbit(semi_major_axis=5.0, speed=3.0)
    orbit.advance(0.5)
    # speed=3, dt=0.5  →  time should be 1.5
    # This is what the time-speed slider in the dashboard will control
    assert abs(orbit.time - 1.5) < 1e-9
