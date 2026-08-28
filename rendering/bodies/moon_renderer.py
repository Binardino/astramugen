"""
MoonRenderer — Ursina entity for a moon orbiting a planet.

Belongs to the rendering layer: reads simulation state, never writes it.
sync() must be called every frame to keep the entity at the moon's
current world position (already translated by Planet.update()).
"""

from __future__ import annotations
from ursina import Entity, Vec3, color as ucolor
from simulation.bodies.moon import Moon


class MoonRenderer:
    """Creates and manages the Ursina sphere entity for a Moon."""

    def __init__(self, moon: Moon) -> None:
        self.moon = moon
        self.entity = Entity(
            model='sphere',
            color=self._to_color(moon.color),
            scale=moon.radius,
            unlit=True,
            position=Vec3(*moon.position),
        )

    def sync(self) -> None:
        """Update entity to match current simulation state. Called each frame."""
        self.entity.position = Vec3(*self.moon.position)
        self.entity.color = self._to_color(self.moon.color)
        self.entity.scale = self.moon.radius

    @staticmethod
    def _to_color(rgb: tuple[float, float, float]) -> ucolor.Color:
        """Convert a 0–1 RGB tuple to a Ursina Color with full opacity."""
        r, g, b = rgb
        return ucolor.Color(r, g, b, 1)
