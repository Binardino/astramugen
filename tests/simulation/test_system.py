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
    system = SolarSystem()
    system.add(_make_star())
    assert len(system.bodies) == 1

def test_remove_body():
    system = SolarSystem()
    star   = _make_star()
    system.add(star)
    system.remove(star)
    assert len(system.bodies) == 0

def test_tick_advances_planet_time():
    system = SolarSystem()
    planet = _make_planet()
    system.add(planet)
    system.tick(0.5)
    assert planet.orbit.time > 0.0

def test_tick_does_not_move_star():
    system = SolarSystem()
    star   = _make_star()
    system.add(star)
    system.tick(10.0)
    assert star.position == (0.0, 0.0, 0.0)

def test_tick_updates_all_bodies():
    system = SolarSystem()
    p1 = _make_planet(orbital_radius=5.0)
    p2 = _make_planet(orbital_radius=9.0)
    system.add(p1)
    system.add(p2)
    system.tick(1.0)
    assert p1.orbit.time == 1.0
    assert p2.orbit.time == 1.0