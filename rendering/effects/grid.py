from __future__ import annotations
from ursina import Entity, Mesh, color as ucolor

def make_grid_mesh(size: float, divisions: int) -> Mesh:
    vertices = []
    step = (size * 2) / divisions
    for i in range(divisions + 1):
        t = -size + i * step
        vertices.extend([(t, 0, -size), (t, 0, size)])
        vertices.extend([(-size, t, 0), (size, t, 0)])
    
    return Mesh(vertices=vertices, mode='line')

class GridEffect:
    def __init__(self, size: float = 30.0, divisions: int = 30) -> None:
        self.entity = Entity(
            model = make_grid_mesh(size, divisions),
            color = ucolor.Color(100/255, 160/255, 255/255, 0.7),
            unlit = True,
        )