"""
AtmosphereEffect — a single translucent halo sphere around a body.

Same fake-bloom technique as StarRenderer's glow, but one layer only —
planets need a subtle rim, not a dramatic corona. Ursina has no built-in
glow/bloom shader for unlit primitives, so this fakes it with a slightly
larger, translucent sphere behind the body's own.

Key Ursina notes:
  - color.Color(r, g, b, a) takes 0–1 values (not 0–255) — the star's halo
    bug earlier this session came from getting this wrong
  - unlit=True required for correct tinted color without lighting wash-out
"""

from __future__ import annotations
from ursina import Entity, Vec3, color as ucolor


class AtmosphereEffect:
    """A single translucent sphere slightly larger than the body it wraps."""

    def __init__(self, body_color: tuple[float, float, float], body_radius: float) -> None:
        r, g, b = body_color
        self.entity = Entity(
            model='sphere',
            color=ucolor.Color(r, g, b, 0.25),
            scale=body_radius * 1.3,
            position=Vec3(0, 0, 0),
            unlit=True,
        )

    def sync(self, position: tuple[float, float, float], radius: float) -> None:
        """Follow the body's current position and size. Called each frame."""
        self.entity.position = Vec3(*position)
        self.entity.scale = radius * 1.3
