"""
Tests for Planet — an orbiting body driven by a KeplerOrbit.

Contract under test:
  - calling update(dt) must move the planet along its circular orbit
  - the planet must always stay at exactly orbital_radius from the origin
  - the orbit's internal time counter must advance proportionally to speed
"""

import math
from simulation.bodies.planet import Planet
from simulation.physics.kepler import KeplerOrbit  # was wrongly imported as 'Kepler'


def make_planet(radius=5.0, speed=1.0) -> Planet:
    """Factory helper: creates a Planet with a KeplerOrbit of the given radius and speed."""
    orbit = KeplerOrbit(semi_major_axis=radius, speed=speed)
    return Planet(name="Earth", radius=1.0, color=(0.2, 0.5, 1.0), orbit=orbit)


def test_planet_position_changes_after_update():
    """update() must actually move the planet — position after != position before."""
    planet = make_planet()
    before = planet.position
    planet.update(0.1)
    assert planet.position != before


def test_planet_stays_on_orbital_radius():
    """After any update, the planet must sit exactly on its orbital radius.

    Checks the Pythagorean distance on the XZ plane. Tolerance 1e-6
    (looser than the kepler unit tests) because position_at() is called
    with a time value that has gone through advance() first.
    """
    planet = make_planet(radius=5.0)
    planet.update(1.0)
    x, _, z = planet.position  # y ignored — orbit is on the XZ plane
    r = math.sqrt(x ** 2 + z ** 2)
    assert abs(r - 5.0) < 1e-6


def test_planet_orbit_time_advances():
    """update(dt) must forward the orbit's time counter by dt * speed."""
    planet = make_planet(speed=2.0)
    planet.update(1.0)
    # speed=2, dt=1  →  orbit.time should be 2.0
    assert abs(planet.orbit.time - 2.0) < 1e-9


def test_planet_faster_speed_moves_more():
    """A planet with higher speed must accumulate more orbit time for the same dt."""
    slow = make_planet(speed=1.0)
    fast = make_planet(speed=5.0)
    slow.update(0.5)
    fast.update(0.5)
    assert slow.orbit.time < fast.orbit.time
