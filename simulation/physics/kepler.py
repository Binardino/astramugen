"""
KeplerOrbit — circular orbit math for the simulation layer.

Computes the (x, y, z) position of a body on a circular orbit given an angle,
and advances an internal time counter each simulation tick.

No Ursina imports here — this module is pure Python and fully testable with pytest.
"""

from __future__ import annotations
import math
from dataclasses import dataclass


@dataclass
class KeplerOrbit:
    """Describes a circular Keplerian orbit around the origin.

    Attributes:
        semi_major_axis: orbital radius in scene units
        speed: angular speed multiplier (1.0 = real-time, 2.0 = twice as fast)
        inclination: tilt of the orbital plane in degrees (0 = flat on XZ plane)
        time: accumulated time, used as the current angle in position_at()
    """

    semi_major_axis : float
    speed           : float
    inclination     : float = 0.0
    time            : float = 0.0

    def advance(self, dt: float) -> None:
        """Move the orbit forward by one simulation step.

        Called every frame by SolarSystem.tick(). Multiplying by speed lets the
        UI time-speed slider scale all orbits without touching dt.
        """
        self.time += dt * self.speed

    def position_at(self, t: float) -> tuple[float, float, float]:
        """Return the (x, y, z) position on the orbit at angle t (radians).

        The orbit lies on the XZ plane by default (y=0 when inclination=0).
        Inclination tilts the plane: a non-zero value lifts the orbit out of XZ,
        splitting the Z component into a Y and a reduced Z.
        """
        x   = self.semi_major_axis * math.cos(t)
        z   = self.semi_major_axis * math.sin(t)
        rad = math.radians(self.inclination)
        # Tilt: project z onto the inclined plane
        y   = z * math.sin(rad)
        z   = z * math.cos(rad)
        return (x, y, z)
