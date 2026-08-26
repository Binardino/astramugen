"""
KeplerOrbit — elliptical orbit math for the simulation layer.

Computes the (x, y, z) position of a body on an elliptical Keplerian orbit
(the star sits at one focus, not the center) given a mean anomaly, and
advances an internal time counter each simulation tick.

No Ursina imports here — this module is pure Python and fully testable with pytest.
"""

from __future__ import annotations
import math
from dataclasses import dataclass


def _solve_eccentric_anomaly(mean_anomaly: float, eccentricity: float,
                              tolerance: float = 1e-9, max_iterations: int = 50) -> float:
    """Solve Kepler's equation M = E - e*sin(E) for the eccentric anomaly E.

    No closed-form solution exists for E, so this iterates from an initial
    guess E0 = M (exact when eccentricity=0) via Newton-Raphson until the
    correction falls below `tolerance`, or `max_iterations` is reached as a
    safety cap against non-convergence.
    """
    E = mean_anomaly
    for _ in range(max_iterations):
        delta = (E - eccentricity * math.sin(E) - mean_anomaly) / (1 - eccentricity * math.cos(E))
        E -= delta
        if abs(delta) < tolerance:
            break
    return E


@dataclass
class KeplerOrbit:
    """Describes an elliptical Keplerian orbit with the star at one focus.

    Attributes:
        semi_major_axis: half the longest diameter of the ellipse, in scene units
        speed: angular speed multiplier (1.0 = real-time, 2.0 = twice as fast)
        eccentricity: 0 = circle, closer to 1 = more elongated ellipse
        inclination: tilt of the orbital plane in degrees (0 = flat on XZ plane)
        time: accumulated time, used as the mean anomaly in position_at()
    """

    semi_major_axis : float
    speed           : float
    eccentricity    : float = 0.0
    inclination     : float = 0.0
    time            : float = 0.0

    def advance(self, dt: float) -> None:
        """Move the orbit forward by one simulation step.

        Called every frame by SolarSystem.tick(). Multiplying by speed lets the
        UI time-speed slider scale all orbits without touching dt.
        """
        self.time += dt * self.speed

    def position_at(self, t: float) -> tuple[float, float, float]:
        """Return the (x, y, z) position at mean anomaly t (radians).

        t is treated as the mean anomaly M, which advances at constant speed
        with time but is not itself the body's real angle on the ellipse.
        It's converted to the eccentric anomaly E by solving Kepler's
        equation, then to a perifocal-frame position with the focus (the
        star) at the origin. With eccentricity=0, E equals M exactly and
        this reduces to the V1 circular formula.
        """
        E = _solve_eccentric_anomaly(t, self.eccentricity)
        # Perifocal frame: periapsis lies on +x, focus (the star) at the origin.
        x = self.semi_major_axis * (math.cos(E) - self.eccentricity)
        z = self.semi_major_axis * math.sqrt(1 - self.eccentricity ** 2) * math.sin(E)
        rad = math.radians(self.inclination)
        # Tilt: project z onto the inclined plane
        y = z * math.sin(rad)
        z = z * math.cos(rad)
        return (x, y, z)
