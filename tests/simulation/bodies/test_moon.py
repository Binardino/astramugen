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


def test_planet_offsets_moon_position_by_its_own_position():
    """Planet.update() must translate its moon's local position by its own.

    This is the core contract: after planet.update(dt), the moon's
    position minus the planet's position (recomputed by hand here) must
    still equal the moon's local orbital distance — regardless of where
    the planet itself ended up in world space.
    """
    planet_orbit = KeplerOrbit(semi_major_axis=10.0, speed=1.0)
    planet       = Planet(name="Earth", radius=1.0, color=(0.2, 0.5, 1.0), orbit=planet_orbit)

    moon_orbit   = KeplerOrbit(semi_major_axis=1.5, speed=2.0)
    planet.moons.append(Moon(name="Luna", radius=0.3, color=(0.7, 0.7, 0.7), orbit=moon_orbit))

    planet.update(1.0)

    px, py, pz = planet.position
    mx, my, mz = planet.moons[0].position
    local_r = math.sqrt((mx - px) ** 2 + (mz - pz) ** 2)
    assert abs(local_r - 1.5) < 1e-6


def test_planet_with_no_moons_still_updates():
    """A planet with an empty moons list (every planet today) must not break.

    Regression guard: the moons-handling loop added to Planet.update()
    must be a no-op when self.moons is [], not raise or change behavior.
    """
    orbit = KeplerOrbit(semi_major_axis=10.0, speed=1.0)
    planet = Planet(name="Earth", radius=1.0, color=(0.2, 0.5, 1.0), orbit=orbit)
    planet.update(1.0)
    assert planet.moons == []
