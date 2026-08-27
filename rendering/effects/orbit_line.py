"""
OrbitLine — wireframe ellipse showing a planet's orbital path.

Belongs to the rendering layer: purely visual, reads orbital shape from
the simulation but never writes back.

How the ellipse mesh is built:
  Same perifocal formula as KeplerOrbit.position_at, but sampled uniformly
  over the eccentric anomaly E (0 → 2π) instead of solving Kepler's equation
  — this traces the static shape of the path, not a timed position, so no
  solver is needed here. The focus (where the star sits) lands at the local
  origin, matching where the simulated body's position actually is.

Key Ursina notes:
  - color.Color(r, g, b, a) takes 0–1 values (not 0–255)
  - unlit=True required for correct tinted color without lighting wash-out
"""

from __future__ import annotations
import math
from ursina import Entity, Mesh, Vec3, color as ucolor


def _circle_mesh(radius: float, segments: int = 64) -> Mesh:
    """Build a flat XZ-plane circle mesh of line segments.

    Superseded by _ellipse_mesh (a circle is just eccentricity=0), kept
    unused for now in case a pure-circle shortcut is useful later.

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

def _ellipse_mesh(semi_major_axis: float, eccentricity: float, segments: int = 64) -> Mesh:
    """Build a flat XZ-plane ellipse mesh with a focus at the local origin.

    Args:
        semi_major_axis: half the longest diameter of the ellipse
        eccentricity: 0 = circle, closer to 1 = more elongated ellipse
        segments: number of line segments — higher gives a smoother ellipse
    """
    a, e = semi_major_axis, eccentricity
    b = a * math.sqrt(1 - e ** 2)  # semi-minor axis
    vertices = [
        # -a*e shifts the geometric center back so the FOCUS sits at the
        # origin, not the center — otherwise this wouldn't match the real
        # orbital path traced by KeplerOrbit.position_at.
        (a * math.cos(E) - a * e, 0, b * math.sin(E))
        for E in (i / segments * math.tau for i in range(segments + 1))
    ]
    return Mesh(vertices=vertices, mode='line')


class OrbitLine:
    """Static wireframe ellipse representing a body's orbital path on the XZ plane.

    Can be re-centered via set_center() so a moon's orbit line follows its
    parent planet each frame instead of staying fixed at the world origin.
    """

    def __init__(self, semi_major_axis: float, eccentricity: float = 0.0) -> None:
        self._radius = semi_major_axis
        self._eccentricity = eccentricity
        self.entity = Entity(
            model=_ellipse_mesh(semi_major_axis, eccentricity),
            color=ucolor.Color(200/255, 200/255, 200/255, 80/255),  # faint grey
            unlit=True,
        )

    def update_radius(self, semi_major_axis: float, eccentricity: float | None = None) -> None:
        """Rebuild the ellipse mesh if the orbit's shape has changed.

        Called by Scene.sync() when a UI slider moves the planet's orbit.
        The 1e-4 threshold avoids rebuilding the mesh on every frame for
        floating-point noise. `eccentricity=None` means "unchanged", so
        existing callers that only pass a radius keep working as before.
        """
        eccentricity = self._eccentricity if eccentricity is None else eccentricity
        if abs(semi_major_axis - self._radius) > 1e-4 or abs(eccentricity - self._eccentricity) > 1e-4:
            self._radius = semi_major_axis
            self._eccentricity = eccentricity
            self.entity.model = _ellipse_mesh(semi_major_axis, eccentricity)

    def set_center(self, position: tuple[float, float, float]) -> None:
        """Move the whole orbit line to follow a moving parent (used for moons)."""
        self.entity.position = Vec3(*position)
