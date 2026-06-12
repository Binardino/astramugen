from __future__ import annotations
from ursina import Entity, Vec3, color as ucolor
from simulation.bodies.planet import Planet

class PlanetRenderer:
    def __init__(self, planet: Planet) -> None:
        self.planet = planet
        self.entity = Entity(
            model='sphere',
            color=self._to_color(planet.color),
            scale=planet.radius,
            unlit=True,
            position=Vec3(*planet.position),
        )
    
    def sync(self) -> None:
        self.entity.position = Vec3(*self.planet.position)
        self.entity.color = self._to_color(self.planet.color)
        self.entity.scale = self.planet.radius

    @staticmethod
    def _to_color(rgb: tuple[float, float, float]):
        r, g, b = rgb  # already 0–1
        return ucolor.Color(r, g, b, 1)
