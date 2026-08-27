"""
Tests for Moon — a body orbiting its parent Planet, not the star.

Contract under test:
  - Moon.update(dt) computes a LOCAL position (relative to the origin, as
    if its parent were at (0,0,0)) — same math as Planet, different frame.
  - Planet.update(dt) is responsible for translating each attached moon's
    local position into world space by adding its own position, right
    after updating itself.
  - A planet with no moons must keep updating without error.
"""

import math
from simulation.bodies.moon import Moon
from simulation.bodies.planet import Planet
from simulation.physics.kepler import KeplerOrbit


def test_moon_position_is_local_after_update():
    """A lone moon orbits the origin exactly like a planet orbits the star.

    Distance to the center must equal semi_major_axis (a circular orbit
    here, eccentricity=0 by default) — same invariant as the Kepler tests.
    """
    orbit = KeplerOrbit(semi_major_axis=1.5, speed=2.0)
    moon = Moon(name="Luna", radius=0.3, color=(0.7, 0.7, 0.7), orbit=orbit)
    moon.update(1.0)
    x, y, z = moon.position
    r = math.sqrt(x ** 2 + z ** 2)
    assert abs(r - 1.5) < 1e-6
