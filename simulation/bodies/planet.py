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


@dataclass
class Planet(CelestialBody):
    """An orbiting body. Its position is recomputed every tick from its KeplerOrbit."""

    # default_factory so each Planet gets its own KeplerOrbit instance, not a shared one
    orbit: KeplerOrbit = field(
        default_factory=lambda: KeplerOrbit(semi_major_axis=5.0, speed=1.0)
    )

    def update(self, dt: float) -> None:
        """Advance the orbit by dt seconds, then update position accordingly."""
        self.orbit.advance(dt)
        self.position = self.orbit.position_at(self.orbit.time)
