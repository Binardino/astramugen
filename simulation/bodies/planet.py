"""
Planet — a celestial body that orbits the star along a KeplerOrbit.

Each frame, update(dt) advances the orbit's internal time counter and
recomputes the planet's (x, y, z) position from the orbit math.
The rendering layer reads planet.position each frame via Scene.sync().
"""

from __future__ import annotations
from dataclasses import dataclass, field
from core.body_base import CelestialBody
from simulation.physics.kepler import KeplerOrbit
from simulation.bodies.moon import Moon


@dataclass
class Planet(CelestialBody):
    """An orbiting body. Its position is recomputed every tick from its KeplerOrbit."""

    # default_factory so each Planet gets its own KeplerOrbit instance, not a shared one
    orbit: KeplerOrbit = field(
        default_factory=lambda: KeplerOrbit(semi_major_axis=5.0, speed=1.0)
    )
    # Same default_factory reasoning as orbit: each Planet needs its own empty
    # list, not one mutable list shared across every Planet instance.
    moons: list[Moon] = field(default_factory=list)

    def update(self, dt: float) -> None:
        """Advance the orbit, then advance and world-position every attached moon."""
        self.orbit.advance(dt)
        self.position = self.orbit.position_at(self.orbit.time)
        for moon in self.moons:
            # moon.update() only computes a LOCAL position (see Moon.update);
            # this planet is the one that knows where it is in world space,
            # so it does the translation rather than the moon translating itself.
            moon.update(dt)
            moon.position = tuple(p + m for p, m in zip(self.position, moon.position))
