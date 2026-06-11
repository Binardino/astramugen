"""
Star — a fixed celestial body at the center of the solar system.

Inherits name, radius, color, and position from CelestialBody.
Its update() is intentionally empty: the star never moves.
"""

from __future__ import annotations
from dataclasses import dataclass
from core.body_base import CelestialBody


@dataclass
class Star(CelestialBody):
    """A star fixed at the origin. update() is a no-op."""

    def update(self, dt: float) -> None:
        pass
