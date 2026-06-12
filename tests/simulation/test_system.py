"""
Tests for SolarSystem — registry and tick.

Contract under test:
  - bodies can be added and removed
  - tick(dt) calls update(dt) on every registered body
  - a Star does not move after tick (its update is a no-op)
  - a Planet advances its orbit time proportionally to dt
"""

from simulation.system import SolarSystem
from simulation.bodies.star import Star
from simulation.bodies.planet import Planet
from simulation.physics.kepler import KeplerOrbit


def _make_star() -> Star:
    return Star(name="Sol", radius=2.0, color=(1.0, 0.85, 0.2))


def _make_planet(orbital_radius=5.0) -> Planet:
    orbit = KeplerOrbit(semi_major_axis=orbital_radius, speed=1.0)
    return Planet(name="Earth", radius=1.0, color=(0.2, 0.5, 1.0), orbit=orbit)


def test_add_body():
    """A body added to the system appears in system.bodies."""
    system = SolarSystem()
    system.add(_make_star())
    assert len(system.bodies) == 1


def test_remove_body():
    """A body removed from the system disappears from system.bodies."""
    system = SolarSystem()
    star = _make_star()
    system.add(star)
    system.remove(star)
    assert len(system.bodies) == 0


def test_tick_advances_planet_time():
    """tick(dt) calls Planet.update(), which advances orbit.time."""
    system = SolarSystem()
    planet = _make_planet()
    system.add(planet)
    system.tick(0.5)
    assert planet.orbit.time > 0.0


def test_tick_does_not_move_star():
    """tick(dt) calls Star.update(), which is a no-op — star stays at origin."""
    system = SolarSystem()
    star = _make_star()
    system.add(star)
    system.tick(10.0)
    assert star.position == (0.0, 0.0, 0.0)


def test_tick_updates_all_bodies():
    """tick(dt) must call update() on every body, not just the first one."""
    system = SolarSystem()
    p1 = _make_planet(orbital_radius=5.0)
    p2 = _make_planet(orbital_radius=9.0)
    system.add(p1)
    system.add(p2)
    system.tick(1.0)
    # Both planets must have advanced, not just p1
    assert p1.orbit.time == 1.0
    assert p2.orbit.time == 1.0
