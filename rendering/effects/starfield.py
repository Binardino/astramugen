"""
Starfield — static field of distant background stars.

Belongs to the rendering layer: pure visual, no simulation state.
The stars are static — they never move or update after creation.
"""

from __future__ import annotations
import random
from ursina import Entity, Vec3, color as ucolor


class Starfield:
    """Static field of small point-like sphere entities scattered on a spherical shell.

    A shell (fixed radius, random direction) rather than a filled cube ensures
    stars surround the scene evenly in every direction, regardless of camera angle.
    """

    def __init__(self, count: int = 800, radius: float = 60.0) -> None:
        self.entities = []
        for _ in range(count):
            direction = Vec3(
                random.uniform(-1, 1),
                random.uniform(-1, 1),
                random.uniform(-1, 1),
            ).normalized()
            # Randomize scale so stars read as being at different distances
            # instead of a uniform, flat-looking dot pattern.
            self.entities.append(Entity(
                model='sphere',
                color=ucolor.white,
                scale=random.uniform(0.03, 0.12),
                position=direction * random.uniform(radius * 0.7, radius),
                unlit=True,
            ))
