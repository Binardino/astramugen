"""
PlanetRenderer — Ursina entity for an orbiting planet.

Belongs to the rendering layer: reads simulation state, never writes it.
sync() must be called every frame to keep the entity at the planet's
current orbital position.

Key Ursina notes:
  - color.Color(r, g, b, a) takes values in 0–1 range (not 0–255)
  - unlit=True disables Ursina's default lighting so the color is applied
    flat, matching the Outer Wilds low-poly look
"""

from __future__ import annotations
from ursina import Entity, Vec3, color as ucolor
from simulation.bodies.planet import Planet


class PlanetRenderer:
    """Creates and manages the Ursina sphere entity for a Planet."""

    def __init__(self, planet: Planet) -> None:
        self.planet = planet
        self.entity = Entity(
            model='sphere',
            color=self._to_color(planet.color),
            scale=planet.radius,
            unlit=True,  # flat color, no lighting wash-out
            position=Vec3(*planet.position),
        )

    def sync(self) -> None:
        """Update entity to match current simulation state. Called each frame."""
        self.entity.position = Vec3(*self.planet.position)
        self.entity.color = self._to_color(self.planet.color)
        self.entity.scale = self.planet.radius

    @staticmethod
    def _to_color(rgb: tuple[float, float, float]) -> ucolor.Color:
        """Convert a 0–1 RGB tuple to a Ursina Color with full opacity."""
        r, g, b = rgb  # already 0–1 from simulation
        return ucolor.Color(r, g, b, 1)
