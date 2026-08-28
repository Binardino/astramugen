"""
Moon — a celestial body that orbits its parent Planet, not the star.

update(dt) computes a position relative to the parent's origin. It is the
owning Planet's responsibility (see Planet.update()) to translate that local
position into world space — this keeps CelestialBody.update(dt)'s single-
argument signature the same for every body type.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from core.body_base import CelestialBody
from simulation.physics.kepler import KeplerOrbit


@dataclass
class Moon(CelestialBody):
    """A body orbiting a Planet. self.position is LOCAL until the parent offsets it."""

    orbit: KeplerOrbit = field(
        default_factory=lambda: KeplerOrbit(semi_major_axis=1.5, speed=2.0)
    )

    def update(self, dt: float) -> None:
        """Advance the local orbit. Position remains relative to the parent planet."""
        self.orbit.advance(dt)
        self.position = self.orbit.position_at(self.orbit.time)
