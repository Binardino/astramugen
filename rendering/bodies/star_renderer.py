"""
StarRenderer — Ursina entity for the star.

Belongs to the rendering layer: reads simulation state, never writes it.
The star is fixed at the origin, so sync() just keeps the entity in sync
in case the simulation position ever changes (future-proofing for binary stars).

Key Ursina notes:
  - color.Color(r, g, b, a) takes values in 0–1 range (not 0–255)
  - unlit=True disables Ursina's default lighting so the color is applied flat,
    which gives the warm Outer Wilds look without needing a custom shader
"""

from __future__ import annotations
from ursina import Entity, Vec3, color as ucolor
from simulation.bodies.star import Star


class StarRenderer:
    """Creates and manages the Ursina sphere entity for a Star."""

    def __init__(self, star: Star) -> None:
        self.star = star
        r, g, b = star.color  # already 0–1 from simulation
        self.entity = Entity(
            model    = 'sphere',
            color    = ucolor.Color(r, g, b, 1),
            scale    = star.radius,
            position = Vec3(0, 0, 0),
            unlit    = True,  # flat color, no lighting wash-out
        )
        # Two concentric transparent spheres fake a soft bloom: a brighter
        # tight layer plus a dimmer wide layer, since Ursina has no built-in
        # glow/bloom shader for unlit primitives.
        self._glow_inner = Entity(
            model    = 'sphere',
            color    = ucolor.Color(r, g, b, 0.47),
            scale    = star.radius * 1.6,
            position = Vec3(0, 0, 0),
            unlit    = True,
        )
        self._glow_outer = Entity(
            model    = 'sphere',
            color    = ucolor.Color(r, g, b, 0.18),
            scale    = star.radius * 3.5,
            position = Vec3(0, 0, 0),
            unlit    = True,
        )

    def sync(self) -> None:
        """Update entity position to match simulation state. Called each frame by Scene."""
        self.entity.position      = Vec3(*self.star.position)
        self._glow_inner.position = Vec3(*self.star.position)
        self._glow_outer.position = Vec3(*self.star.position)
