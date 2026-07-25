"""
main.py — entry point for Astramugen.

Wires together the simulation layer (SolarSystem, Star, Planet) and the
rendering layer (StarRenderer, PlanetRenderer, GridEffect, OrbitLine).
The update() function is called by Ursina every frame; it ticks the
simulation and syncs the renderers.

Layer contract:
  - simulation/ never imports Ursina
  - rendering/ never computes orbits
  - main.py is the only place that connects the two
"""
from ursina import Ursina, color, time, window

from simulation.bodies.star import Star
from simulation.bodies.planet import Planet
from simulation.physics.kepler import KeplerOrbit
from simulation.system import SolarSystem
from rendering.effects.orbit_line import OrbitLine
from rendering.scene import Scene
from rendering.camera import CameraController

app = Ursina()
window.color = color.black

# --- Simulation setup ---
system = SolarSystem()
star = Star(name="Sol", radius=2.0, color=(1.0, 0.85, 0.2))
system.add(star)

# -- Defining Planet --
# Each tuple: (name, orbital radius, orbital speed, visual size, color)
planet_data = [
    ("Mercury", 5.0, 1.5, 0.5, (0.8, 0.6, 0.3)),
    ("Venus",   7.0, 1.1, 0.8, (0.9, 0.7, 0.4)),
    ("Earth",   9.0, 0.8, 0.9, (0.2, 0.5, 1.0)),
    ("Mars",   13.0, 0.5, 0.7, (0.9, 0.3, 0.2)),
]

for name, radius, speed, size, planet_colour in planet_data:
    orbit = KeplerOrbit(semi_major_axis=radius, speed=speed)
    planet = Planet(name=name, radius=size, color=planet_colour, orbit=orbit)
    system.add(planet)

# --- Rendering setup ---
scene = Scene(system)

# EditorCamera: right-click drag to orbit, scroll to zoom
camera = CameraController()

def update():
    """Called by Ursina every frame. Advances simulation, then syncs renderers."""
    system.tick(time.dt)
    scene.sync()


app.run()
