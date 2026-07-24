from simulation.bodies.star import Star
from simulation.bodies.planet import Planet
from rendering.bodies.star_renderer import StarRenderer
from rendering.bodies.planet_renderer import PlanetRenderer
from rendering.effects.orbit_line import OrbitLine
from rendering.effects.grid import GridEffect
from ursina import destroy
class Scene:
    def __init__(self, system):
        self.system = system
        self._renderers   = {}
        self._orbit_lines = {}
        self.grid         = GridEffect()
        for body in self.system.bodies:
            self._register(body)

    def _register(self, body):
        if isinstance(body, Star):
            self._renderers[id(body)] = StarRenderer(body)
        
        if isinstance(body, Planet):
            self._renderers[id(body)] = PlanetRenderer(body)
            self._orbit_lines[id(body)] = OrbitLine(body.orbit.semi_major_axis)

    def add_body(self, body):
        self.system.add(body)
        self._register(body)

    def remove_body(self, body):
        self.destroy(body)
        self.pop(body)
        self.system.remove(body)

    def sync(self):
        for renderer in self._renderers.values():
            renderer.sync()
        for key, value in self._orbit_lines.items():
            body = next(body for body in self.system.bodies if id(body) == key)
            self._orbit_lines[key].update_radius(body.orbit.semi_major_axis)