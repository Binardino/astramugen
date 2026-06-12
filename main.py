"""
main.py — entry point for Astramugen.

Wires together the simulation layer (SolarSystem, Star, Planet) and the
rendering layer (StarRenderer, GridEffect). The update() function is called
by Ursina every frame; it ticks the simulation and syncs the renderers.

Layer contract:
  - simulation/ never imports Ursina
  - rendering/ never computes orbits
  - main.py is the only place that connects the two
"""
### star import
from ursina import Ursina, color, time, window
from ursina.prefabs.editor_camera import EditorCamera

from simulation.bodies.star import Star
from simulation.system import SolarSystem
from rendering.bodies.star_renderer import StarRenderer
from rendering.effects.grid import GridEffect

#planet import
from simulation.bodies.planet import Planet
from simulation.physics.kepler import KeplerOrbit
from rendering.bodies.planet_renderer import PlanetRenderer
from rendering.effects.orbit_line import OrbitLine


app = Ursina()
window.color = color.black

# --- Simulation setup ---
system = SolarSystem()
star = Star(name="Sol", radius=2.0, color=(1.0, 0.85, 0.2))
system.add(star)

# --- Rendering setup ---
star_renderer = StarRenderer(star)
grid = GridEffect()

# EditorCamera: middle-click drag to orbit, scroll to zoom, right-click to pan
EditorCamera()

# --- planet setup ---
orbit = KeplerOrbit(semi_major_axis=8.0, speed=0.8)
planet = Planet(name="Earth", radius=0.9, color=(0.2, 0.5, 1.0), orbit=orbit)
system.add(planet)

planet_renderer = PlanetRenderer(planet)
orbit_line = OrbitLine(orbit.semi_major_axis)

###
def update():
    """Called by Ursina every frame. Advances simulation, then syncs renderers."""
    system.tick(time.dt)
    planet_renderer.sync()


#launch app
app.run()
