"""
OrbitLine — wireframe circle showing a planet's orbital path.

Belongs to the rendering layer: purely visual, reads orbital radius from
the simulation but never writes back.

How the circle mesh is built:
  Evenly spaced points are sampled around a circle at angles 0 → 2π
  (math.tau) using cos/sin. One extra point at the end closes the loop
  back to the start. Mesh mode='line' draws segments between consecutive
  vertex pairs.

Key Ursina notes:
  - color.Color(r, g, b, a) takes 0–1 values (not 0–255)
  - unlit=True required for correct tinted color without lighting wash-out
"""

from __future__ import annotations
import math
from ursina import Entity, Mesh, color as ucolor


def _circle_mesh(radius: float, segments: int = 64) -> Mesh:
    """Build a flat XZ-plane circle mesh of line segments.

    Args:
        radius: radius of the circle (matches the planet's orbital radius)
        segments: number of line segments — higher gives a smoother circle
    """
    vertices = [
        (math.cos(i / segments * math.tau) * radius,
         0,
         math.sin(i / segments * math.tau) * radius)
        for i in range(segments + 1)  # +1 closes the loop back to the start
    ]
    return Mesh(vertices=vertices, mode='line')


class OrbitLine:
    """Static wireframe circle representing a planet's orbital path on the XZ plane."""

    def __init__(self, radius: float) -> None:
        self._radius = radius
        self.entity = Entity(
            model=_circle_mesh(radius),
            color=ucolor.Color(200/255, 200/255, 200/255, 80/255),  # faint grey
            unlit=True,
        )

    def update_radius(self, radius: float) -> None:
        """Rebuild the circle mesh if the orbital radius has changed.

        Called by Scene.sync() when a UI slider moves the planet's orbit.
        The 1e-4 threshold avoids rebuilding the mesh on every frame for
        floating-point noise.
        """
        if abs(radius - self._radius) > 1e-4:
            self._radius = radius
            self.entity.model = _circle_mesh(radius)
