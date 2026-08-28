"""
Scene — orchestrates all renderers for a SolarSystem.

Registers a renderer (and orbit line, for planets) for each body in the
system, and keeps them in sync with the simulation state every frame.
Belongs to the rendering layer: reads simulation state, never writes it.
"""

from simulation.bodies.star import Star
from simulation.bodies.planet import Planet
from rendering.bodies.star_renderer import StarRenderer
from rendering.bodies.planet_renderer import PlanetRenderer
from rendering.bodies.moon_renderer import MoonRenderer
from rendering.effects.orbit_line import OrbitLine
from rendering.effects.grid import GridEffect
from rendering.effects.starfield import Starfield
from ursina import destroy


class Scene:
    """Owns and syncs one renderer per body in a SolarSystem, plus the background grid."""

    def __init__(self, system):
        self.system = system
        self._renderers = {}
        self._orbit_lines = {}
        self.grid = GridEffect()
        self.starfield = Starfield()
        for body in self.system.bodies:
            self._register(body)

    def _register(self, body):
        """Create and store the renderer (and orbit line, for planets) for a single body."""
        if isinstance(body, Star):
            self._renderers[id(body)] = StarRenderer(body)

        if isinstance(body, Planet):
            self._renderers[id(body)] = PlanetRenderer(body)
            self._orbit_lines[id(body)] = OrbitLine(body.orbit.semi_major_axis, body.orbit.eccentricity)
            for moon in body.moons:
                self._renderers[id(moon)] = MoonRenderer(moon)
                self._orbit_lines[id(moon)] = OrbitLine(moon.orbit.semi_major_axis, moon.orbit.eccentricity)

    def add_body(self, body):
        """Add a body to the system and create its renderer."""
        self.system.add(body)
        self._register(body)

    def remove_body(self, body):
        """Destroy a body's Ursina entities and remove it from the system.

        For a Planet, also destroys its moons' entities first — they are
        never in system.bodies, so nothing else would ever clean them up.
        """
        if isinstance(body, Planet):
            for moon in body.moons:
                destroy(self._renderers.pop(id(moon)).entity)
                destroy(self._orbit_lines.pop(id(moon)).entity)

        key = id(body)
        renderer = self._renderers.pop(key, None)
        if renderer is not None:
            destroy(renderer.entity)
        orbit_line = self._orbit_lines.pop(key, None)
        if orbit_line is not None:
            destroy(orbit_line.entity)
        self.system.remove(body)

    def sync(self):
        """Update every renderer and orbit line to match current simulation state.

        Called each frame. Orbit lines are only updated by walking
        system.bodies (never by iterating self._orbit_lines directly) —
        that dict also holds moon entries, and moons are never in
        system.bodies, so a blind iteration would raise StopIteration
        trying to look one up there.
        """
        for renderer in self._renderers.values():
            renderer.sync()
        for body in self.system.bodies:
            if isinstance(body, Planet):
                self._orbit_lines[id(body)].update_radius(body.orbit.semi_major_axis, body.orbit.eccentricity)
                for moon in body.moons:
                    self._orbit_lines[id(moon)].update_radius(moon.orbit.semi_major_axis, moon.orbit.eccentricity)
                    # Moons orbit their planet, not the world origin — the
                    # orbit line has to follow the planet's current position.
                    self._orbit_lines[id(moon)].set_center(body.position)
