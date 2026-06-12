from __future__ import annotations
import math
from ursina import Entity, Mesh, color as ucolor


def _circle_mesh(radius: float, segments: int = 64) -> Mesh:
    vertices = [
        (math.cos(i / segments * math.tau) * radius,
         0,
         math.sin(i / segments * math.tau) * radius)
        for i in range(segments + 1)
    ]
    return Mesh(vertices=vertices, mode='line')


class OrbitLine:
    def __init__(self, radius: float) -> None:
        self._radius = radius
        self.entity = Entity(
            model=_circle_mesh(radius),
            color=ucolor.Color(200/255, 200/255, 200/255, 80/255),
            unlit=True
        )

    def update_radius(self, radius: float) -> None:
        if abs(radius - self._radius) > 1e-4:
            self._radius = radius
            self.entity.model = _circle_mesh(radius)