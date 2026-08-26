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


def test_eccentric_orbit_periapsis_at_zero_mean_anomaly():
    """At mean anomaly M=0, the body sits at periapsis: distance = a(1-e).

    Periapsis is the closest point to the focus (the star) on an ellipse —
    this is where a real planet moves fastest.
    """
    orbit = KeplerOrbit(semi_major_axis=10.0, eccentricity=0.5, speed=1.0)
    x, y, z = orbit.position_at(0.0)
    r = math.sqrt(x ** 2 + z ** 2)
    # a=10, e=0.5  →  expected periapsis distance = 10 * (1 - 0.5) = 5.0
    assert abs(r - 10.0 * (1 - 0.5)) < 1e-6


def test_eccentric_orbit_apoapsis_at_half_turn_mean_anomaly():
    """At mean anomaly M=π, the body sits at apoapsis: distance = a(1+e).

    Apoapsis is the farthest point from the focus on an ellipse — this is
    where a real planet moves slowest.
    """
    orbit = KeplerOrbit(semi_major_axis=10.0, eccentricity=0.5, speed=1.0)
    x, y, z = orbit.position_at(math.pi)
    r = math.sqrt(x ** 2 + z ** 2)
    # a=10, e=0.5  →  expected apoapsis distance = 10 * (1 + 0.5) = 15.0
    assert abs(r - 10.0 * (1 + 0.5)) < 1e-6


def test_eccentric_orbit_radius_stays_within_periapsis_and_apoapsis():
    """At any mean anomaly, the distance to the focus must stay within
    [periapsis, apoapsis] — an ellipse never gets closer or farther than that.

    Unlike the periapsis/apoapsis tests, these angles have no hand-computable
    expected position — this is what actually exercises the Newton-Raphson
    solver on arbitrary inputs, checked against a geometric invariant instead
    of an exact value.
    """
    orbit = KeplerOrbit(semi_major_axis=10.0, eccentricity=0.7, speed=1.0)
    periapsis, apoapsis = 10.0 * (1 - 0.7), 10.0 * (1 + 0.7)
    for angle in [0.1, 1.0, 2.0, 3.0, 4.5, 6.0]:
        x, y, z = orbit.position_at(angle)
        r = math.sqrt(x ** 2 + z ** 2)
        assert periapsis - 1e-6 <= r <= apoapsis + 1e-6


def test_solver_converges_for_high_eccentricity():
    """The Newton-Raphson solver must converge even for a strongly elongated
    ellipse (e=0.9) instead of hanging or returning NaN/inf.

    This is a numerical robustness check, not a physics check — high
    eccentricity is where an under-tuned iteration count or tolerance would
    fail first.
    """
    orbit = KeplerOrbit(semi_major_axis=5.0, eccentricity=0.9, speed=1.0)
    x, y, z = orbit.position_at(1.3)  # arbitrary mean anomaly, just must resolve
    assert math.isfinite(x) and math.isfinite(z)
