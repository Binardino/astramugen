"""
GridEffect — background wireframe grid on the XZ plane.

Belongs to the rendering layer: pure visual, no simulation state.
The grid is static — it never moves or updates after creation.

How the mesh is built:
  For each of (divisions+1) steps, we emit two line segments:
    - one parallel to Z (varying X)  → the "vertical" lines of the grid
    - one parallel to X (varying Z)  → the "horizontal" lines of the grid
  All Y=0 so the grid stays flat on the ground plane.

Key Ursina notes:
  - Mesh(vertices, mode='line') draws line segments between consecutive pairs of vertices
  - unlit=True + color.Color() required in Ursina 7 to get the correct tinted color
    (values must be 0–1; passing 0–255 integers gets clamped to 1.0 = white)
"""

from __future__ import annotations
from ursina import Entity, Mesh, color as ucolor


def make_grid_mesh(size: float, divisions: int) -> Mesh:
    """Build a flat XZ-plane grid mesh of line segments.

    Args:
        size: half-extent of the grid (grid spans from -size to +size)
        divisions: number of cells per axis
    """
    vertices = []
    step = (size * 2) / divisions
    for i in range(divisions + 1):
        t = -size + i * step
        vertices.extend([(t, 0, -size), (t, 0,  size)])  # line parallel to Z
        vertices.extend([(-size, 0, t), ( size, 0,  t)])  # line parallel to X
    return Mesh(vertices=vertices, mode='line')


class GridEffect:
    """Static wireframe grid placed on the XZ plane at Y=0."""

    def __init__(self, size: float = 30.0, divisions: int = 30) -> None:
        self.entity = Entity(
            model = make_grid_mesh(size, divisions),
            color = ucolor.Color(100/255, 160/255, 255/255, 0.7),  # light blue
            unlit = True,
        )
