"""
Tests for Star — a fixed body that never moves.

Contract under test: a Star must always sit at the origin (0, 0, 0)
regardless of how many times update() is called.
"""

from simulation.bodies.star import Star


def test_star_default_position_is_origin():
    """A newly created Star must be at (0, 0, 0) without any update call.

    This position is inherited from CelestialBody's default_factory.
    Using == (not 1e-9 tolerance) because no floating-point math is involved.
    """
    star = Star(name="Sol", radius=2.0, color=(1.0, 0.85, 0.2))
    assert star.position == (0.0, 0.0, 0.0)


def test_star_does_not_move_after_update():
    """update() must be a no-op for a Star — it never moves.

    SolarSystem.tick() calls update() on every body each frame.
    This test ensures the star stays fixed no matter how many ticks occur.
    """
    star = Star(name="Sol", radius=2.0, color=(1.0, 0.85, 0.2))
    star.update(1.0)
    star.update(10.0)
    assert star.position == (0.0, 0.0, 0.0)
