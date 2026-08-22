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
from simulation.system import SolarSystem
from rendering.effects.orbit_line import OrbitLine
from rendering.scene import Scene
from rendering.camera import CameraController
from ui.panels.time_panel import TimePanel
from ui.panels.planet_panel import PlanetPanel

app = Ursina()
window.color = color.black

# --- Simulation setup ---
system = SolarSystem()
star = Star(name="Sol", radius=2.0, color=(1.0, 0.85, 0.2))
system.add(star)

# --- Rendering setup ---
scene = Scene(system)

# PlanetPanel builds the dashboard sliders AND creates the initial
# `planet_range` planets (from PLANET_DEFAULTS) into `scene` on construction.
planet_panel = PlanetPanel(scene, planet_range=4)

# EditorCamera: right-click drag to orbit, scroll to zoom
camera = CameraController()

time_panel = TimePanel()

def update():
    """Called by Ursina every frame. Advances simulation, then syncs renderers."""
    system.tick(time.dt * time_panel.time_scale)
    scene.sync()


app.run()
