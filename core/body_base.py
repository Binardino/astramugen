from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

@dataclass
class CelestialBody(ABC):
    name     : str
    radius   : float
    color    : tuple[float,float,float]
    position : tuple[float,float,float] = field(default_factory= lambda : (0.0, 0.0, 0.0))

    @abstractmethod
    def update(self, dt: float) -> None: ...