"""
SolarSystem — registry and simulation tick for all celestial bodies.

Owns the list of active bodies and advances the simulation each frame.
Pure Python: no Ursina imports here. Rendering reads this state via Scene.sync().
"""

from __future__ import annotations
from core.body_base import CelestialBody


class SolarSystem:
    """Holds all celestial bodies and drives the simulation forward.

    The main loop calls tick(dt) every frame. Each body's update() is
    responsible for moving itself — SolarSystem just iterates and delegates.
    """

    def __init__(self) -> None:
        self.bodies: list[CelestialBody] = []

    def add(self, body: CelestialBody) -> None:
        """Register a body in the simulation."""
        self.bodies.append(body)

    def remove(self, body: CelestialBody) -> None:
        """Remove a body from the simulation (and later from the scene via Scene)."""
        self.bodies.remove(body)

    def tick(self, dt: float) -> None:
        """Advance every body by dt seconds. Called once per frame by main.py."""
        for body in self.bodies:
            body.update(dt)
