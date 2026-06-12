from __future__ import annotations
from core.body_base import CelestialBody

class SolarSystem:
    def __init__(self) -> None:
        self.bodies: list[CelestialBody] = []

    def add(self, body:CelestialBody) -> None:
        self.bodies.append(body)

    def remove(self, body:CelestialBody) -> None:
        self.bodies.remove(body)

    def tick(self, dt: float) -> None:
        for body in self.bodies:
            body.update(dt)