from __future__ import annotations
from ursina import Entity, Vec3, color as ucolor
from simulation.bodies.star import Star

class StarRenderer:
    def __init__(self, star: Star) -> None:
        self.star = star
        r, g, b = star.color  # already 0–1
        self.entity = Entity(
            model    = 'sphere',
            color    = ucolor.Color(r, g, b, 1),
            scale    = star.radius,
            position = Vec3(0, 0, 0),
            unlit    = True,
        )
    def sync(self) -> None:
        self.entity.position = Vec3(*self.star.position)