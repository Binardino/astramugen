from ursina import Ursina, color, time, window
from ursina.prefabs.editor_camera import EditorCamera

from simulation.bodies.star import Star
from simulation.system import SolarSystem
from rendering.bodies.star_renderer import StarRenderer
from rendering.effects.grid import GridEffect

app = Ursina()
window.color = color.black

system = SolarSystem()
star = Star(name="Sol", radius=2.0, color=(1.0, 0.85, 0.2))
system.add(star)

star_renderer = StarRenderer(star)
grid = GridEffect()

EditorCamera()

def update():
    system.tick(time.dt)


app.run()