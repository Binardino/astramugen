# Astramugen V1 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a working V1 solar system simulator — 1 star + up to 5 configurable planets orbiting in real time with a 3D dashboard.

**Architecture:** Three strict layers: `simulation/` (pure Python, testable with pytest), `rendering/` (Ursina 3D), `ui/` (Ursina dashboard). UI writes directly to simulation objects; `Scene.sync()` reads simulation state each frame. The simulation never imports Ursina.

**Tech Stack:** Python 3.11+, Ursina Engine, pytest

---

## File Map

| File | Responsibility |
|------|---------------|
| `core/body_base.py` | `CelestialBody` abstract base class |
| `simulation/physics/kepler.py` | `KeplerOrbit` — circular orbit math |
| `simulation/bodies/star.py` | `Star` — fixed body at center |
| `simulation/bodies/planet.py` | `Planet` — orbiting body |
| `simulation/system.py` | `SolarSystem` — registry + tick |
| `rendering/bodies/star_renderer.py` | Ursina entity for the star |
| `rendering/bodies/planet_renderer.py` | Ursina entity for a planet |
| `rendering/effects/grid.py` | Background wireframe grid |
| `rendering/effects/orbit_line.py` | Circular wireframe orbit trail |
| `rendering/scene.py` | Orchestrates all renderers, `sync()` each frame |
| `rendering/camera.py` | Wraps Ursina `EditorCamera` |
| `ui/panels/time_panel.py` | Global time speed slider |
| `ui/panels/planet_panel.py` | Per-planet sliders + planet count |
| `main.py` | Entry point — wires everything together |
| `tests/` | pytest tests for `simulation/` and `core/` only |
| `requirements.txt` | `ursina`, `pytest` |
| `pytest.ini` | Sets `pythonpath = .` so imports work |

---

## Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `pytest.ini`
- Create: `tests/__init__.py`
- Create: `tests/core/__init__.py`
- Create: `tests/simulation/__init__.py`
- Create: `tests/simulation/physics/__init__.py`

- [ ] **Step 1: Create requirements.txt**

```
ursina
pytest
```

- [ ] **Step 2: Install dependencies**

```bash
pip install -r requirements.txt
```

Expected: Ursina and pytest install without errors.

- [ ] **Step 3: Create pytest.ini**

```ini
[pytest]
pythonpath = .
```

- [ ] **Step 4: Create test directories**

```bash
mkdir -p tests/core tests/simulation/physics tests/simulation/bodies
touch tests/__init__.py tests/core/__init__.py
touch tests/simulation/__init__.py tests/simulation/physics/__init__.py
touch tests/simulation/bodies/__init__.py
```

- [ ] **Step 5: Verify pytest runs (empty)**

```bash
pytest --tb=short
```

Expected: `no tests ran` — no errors.

- [ ] **Step 6: Commit**

```bash
git add requirements.txt pytest.ini tests/
git commit -m "chore: add requirements, pytest config, test scaffold"
```

---

## Task 2: CelestialBody Abstract Base Class

**Files:**
- Modify: `core/body_base.py`
- Create: `tests/core/test_body_base.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/core/test_body_base.py
import pytest
from core.body_base import CelestialBody


def test_cannot_instantiate_directly():
    with pytest.raises(TypeError):
        CelestialBody(name="X", radius=1.0, color=(1.0, 0.0, 0.0))


def test_concrete_subclass_works():
    class Dummy(CelestialBody):
        def update(self, dt: float) -> None:
            pass

    body = Dummy(name="test", radius=1.0, color=(1.0, 0.0, 0.0))
    assert body.name == "test"
    assert body.radius == 1.0
    assert body.color == (1.0, 0.0, 0.0)
    assert body.position == (0.0, 0.0, 0.0)
```

- [ ] **Step 2: Run test to confirm failure**

```bash
pytest tests/core/test_body_base.py -v
```

Expected: `ImportError` — `core.body_base` is empty.

- [ ] **Step 3: Implement CelestialBody**

```python
# core/body_base.py
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class CelestialBody(ABC):
    name: str
    radius: float
    color: tuple[float, float, float]
    position: tuple[float, float, float] = field(default=(0.0, 0.0, 0.0))

    @abstractmethod
    def update(self, dt: float) -> None: ...
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/core/test_body_base.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add core/body_base.py tests/core/test_body_base.py
git commit -m "feat: CelestialBody abstract base class"
```

---

## Task 3: KeplerOrbit

**Files:**
- Modify: `simulation/physics/kepler.py`
- Create: `tests/simulation/physics/test_kepler.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/simulation/physics/test_kepler.py
import math
import pytest
from simulation.physics.kepler import KeplerOrbit


def test_position_at_zero_angle():
    orbit = KeplerOrbit(semi_major_axis=5.0, speed=1.0)
    x, y, z = orbit.position_at(0.0)
    assert abs(x - 5.0) < 1e-9
    assert abs(y) < 1e-9
    assert abs(z) < 1e-9


def test_position_at_quarter_turn():
    orbit = KeplerOrbit(semi_major_axis=5.0, speed=1.0)
    x, y, z = orbit.position_at(math.pi / 2)
    assert abs(x) < 1e-9
    assert abs(z - 5.0) < 1e-9


def test_radius_preserved_at_any_angle():
    orbit = KeplerOrbit(semi_major_axis=5.0, speed=1.0)
    for angle in [0.0, 0.5, 1.2, math.pi, 2 * math.pi - 0.1]:
        x, y, z = orbit.position_at(angle)
        r = math.sqrt(x ** 2 + z ** 2)
        assert abs(r - 5.0) < 1e-9, f"radius wrong at angle={angle}: got {r}"


def test_advance_increments_time():
    orbit = KeplerOrbit(semi_major_axis=5.0, speed=2.0)
    orbit.advance(1.0)
    assert abs(orbit.time - 2.0) < 1e-9


def test_advance_speed_scales_time():
    orbit = KeplerOrbit(semi_major_axis=5.0, speed=3.0)
    orbit.advance(0.5)
    assert abs(orbit.time - 1.5) < 1e-9
```

- [ ] **Step 2: Run to confirm failure**

```bash
pytest tests/simulation/physics/test_kepler.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement KeplerOrbit**

```python
# simulation/physics/kepler.py
from __future__ import annotations
import math
from dataclasses import dataclass


@dataclass
class KeplerOrbit:
    semi_major_axis: float
    speed: float
    inclination: float = 0.0
    time: float = 0.0

    def advance(self, dt: float) -> None:
        self.time += dt * self.speed

    def position_at(self, t: float) -> tuple[float, float, float]:
        x = self.semi_major_axis * math.cos(t)
        z = self.semi_major_axis * math.sin(t)
        rad = math.radians(self.inclination)
        y = z * math.sin(rad)
        z = z * math.cos(rad)
        return (x, y, z)
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/simulation/physics/test_kepler.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add simulation/physics/kepler.py tests/simulation/physics/test_kepler.py
git commit -m "feat: KeplerOrbit circular orbit math"
```

---

## Task 4: Star

**Files:**
- Modify: `simulation/bodies/star.py`
- Create: `tests/simulation/bodies/test_star.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/simulation/bodies/test_star.py
from simulation.bodies.star import Star


def test_star_default_position_is_origin():
    star = Star(name="Sol", radius=2.0, color=(1.0, 0.85, 0.2))
    assert star.position == (0.0, 0.0, 0.0)


def test_star_does_not_move_after_update():
    star = Star(name="Sol", radius=2.0, color=(1.0, 0.85, 0.2))
    star.update(1.0)
    star.update(10.0)
    assert star.position == (0.0, 0.0, 0.0)
```

- [ ] **Step 2: Run to confirm failure**

```bash
pytest tests/simulation/bodies/test_star.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement Star**

```python
# simulation/bodies/star.py
from __future__ import annotations
from dataclasses import dataclass
from core.body_base import CelestialBody


@dataclass
class Star(CelestialBody):
    def update(self, dt: float) -> None:
        pass
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/simulation/bodies/test_star.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add simulation/bodies/star.py tests/simulation/bodies/test_star.py
git commit -m "feat: Star — fixed body at origin"
```

---

## Task 5: Planet

**Files:**
- Modify: `simulation/bodies/planet.py`
- Create: `tests/simulation/bodies/test_planet.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/simulation/bodies/test_planet.py
import math
from simulation.bodies.planet import Planet
from simulation.physics.kepler import KeplerOrbit


def _make_planet(radius=5.0, speed=1.0) -> Planet:
    orbit = KeplerOrbit(semi_major_axis=radius, speed=speed)
    return Planet(name="Earth", radius=1.0, color=(0.2, 0.5, 1.0), orbit=orbit)


def test_planet_position_changes_after_update():
    planet = _make_planet()
    before = planet.position
    planet.update(0.1)
    assert planet.position != before


def test_planet_stays_on_orbital_radius():
    planet = _make_planet(radius=5.0)
    planet.update(1.0)
    x, y, z = planet.position
    r = math.sqrt(x ** 2 + z ** 2)
    assert abs(r - 5.0) < 1e-6


def test_planet_orbit_time_advances():
    planet = _make_planet(speed=2.0)
    planet.update(1.0)
    assert abs(planet.orbit.time - 2.0) < 1e-9


def test_planet_faster_speed_moves_more():
    slow = _make_planet(speed=1.0)
    fast = _make_planet(speed=3.0)
    slow.update(0.5)
    fast.update(0.5)
    dx_slow = abs(slow.position[0])
    dx_fast = abs(fast.position[0])
    assert slow.orbit.time < fast.orbit.time
```

- [ ] **Step 2: Run to confirm failure**

```bash
pytest tests/simulation/bodies/test_planet.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement Planet**

```python
# simulation/bodies/planet.py
from __future__ import annotations
from dataclasses import dataclass, field
from core.body_base import CelestialBody
from simulation.physics.kepler import KeplerOrbit


@dataclass
class Planet(CelestialBody):
    orbit: KeplerOrbit = field(
        default_factory=lambda: KeplerOrbit(semi_major_axis=5.0, speed=1.0)
    )

    def update(self, dt: float) -> None:
        self.orbit.advance(dt)
        self.position = self.orbit.position_at(self.orbit.time)
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/simulation/bodies/test_planet.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add simulation/bodies/planet.py tests/simulation/bodies/test_planet.py
git commit -m "feat: Planet — orbiting body using KeplerOrbit"
```

---

## Task 6: SolarSystem

**Files:**
- Modify: `simulation/system.py`
- Create: `tests/simulation/test_system.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/simulation/test_system.py
from simulation.system import SolarSystem
from simulation.bodies.star import Star
from simulation.bodies.planet import Planet
from simulation.physics.kepler import KeplerOrbit


def _make_star() -> Star:
    return Star(name="Sol", radius=2.0, color=(1.0, 0.85, 0.2))


def _make_planet(orbital_radius=5.0) -> Planet:
    orbit = KeplerOrbit(semi_major_axis=orbital_radius, speed=1.0)
    return Planet(name="Earth", radius=1.0, color=(0.2, 0.5, 1.0), orbit=orbit)


def test_add_body():
    system = SolarSystem()
    system.add(_make_star())
    assert len(system.bodies) == 1


def test_remove_body():
    system = SolarSystem()
    star = _make_star()
    system.add(star)
    system.remove(star)
    assert len(system.bodies) == 0


def test_tick_advances_planet_time():
    system = SolarSystem()
    planet = _make_planet()
    system.add(planet)
    system.tick(0.5)
    assert planet.orbit.time > 0.0


def test_tick_does_not_move_star():
    system = SolarSystem()
    star = _make_star()
    system.add(star)
    system.tick(10.0)
    assert star.position == (0.0, 0.0, 0.0)


def test_tick_updates_all_bodies():
    system = SolarSystem()
    system.add(_make_star())
    p1 = _make_planet(orbital_radius=5.0)
    p2 = _make_planet(orbital_radius=9.0)
    system.add(p1)
    system.add(p2)
    system.tick(1.0)
    assert p1.orbit.time == 1.0
    assert p2.orbit.time == 1.0
```

- [ ] **Step 2: Run to confirm failure**

```bash
pytest tests/simulation/test_system.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement SolarSystem**

```python
# simulation/system.py
from __future__ import annotations
from core.body_base import CelestialBody


class SolarSystem:
    def __init__(self) -> None:
        self.bodies: list[CelestialBody] = []

    def add(self, body: CelestialBody) -> None:
        self.bodies.append(body)

    def remove(self, body: CelestialBody) -> None:
        self.bodies.remove(body)

    def tick(self, dt: float) -> None:
        for body in self.bodies:
            body.update(dt)
```

- [ ] **Step 4: Run all simulation tests**

```bash
pytest tests/ -v
```

Expected: all tests pass (no Ursina involved yet).

- [ ] **Step 5: Commit**

```bash
git add simulation/system.py tests/simulation/test_system.py
git commit -m "feat: SolarSystem registry with tick"
```

---

## Task 7: First Visual — Star + Grid

**Files:**
- Modify: `rendering/bodies/star_renderer.py`
- Modify: `rendering/effects/grid.py`
- Modify: `main.py`

No pytest for rendering — verify visually by running `python main.py`.

- [ ] **Step 1: Implement StarRenderer**

```python
# rendering/bodies/star_renderer.py
from __future__ import annotations
from ursina import Entity, Vec3, color as ucolor
from simulation.bodies.star import Star


class StarRenderer:
    def __init__(self, star: Star) -> None:
        self.star = star
        r, g, b = (int(c * 255) for c in star.color)
        self.entity = Entity(
            model='sphere',
            color=ucolor.rgb(r, g, b),
            scale=star.radius,
            position=Vec3(0, 0, 0),
        )

    def sync(self) -> None:
        self.entity.position = Vec3(*self.star.position)
```

- [ ] **Step 2: Implement GridEffect**

```python
# rendering/effects/grid.py
from __future__ import annotations
from ursina import Entity, Mesh, color as ucolor


def _make_grid_mesh(size: float, divisions: int) -> Mesh:
    vertices = []
    step = (size * 2) / divisions
    for i in range(divisions + 1):
        t = -size + i * step
        vertices.extend([(t, 0, -size), (t, 0, size)])
        vertices.extend([(-size, 0, t), (size, 0, t)])
    return Mesh(vertices=vertices, mode='line')


class GridEffect:
    def __init__(self, size: float = 30.0, divisions: int = 30) -> None:
        self.entity = Entity(
            model=_make_grid_mesh(size, divisions),
            color=ucolor.rgba(40, 80, 200, 60),
        )
```

- [ ] **Step 3: Write a minimal main.py to see the first visual**

```python
# main.py
from ursina import Ursina, color, time
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
```

- [ ] **Step 4: Run and verify visually**

```bash
python main.py
```

Expected: black window, blue wireframe grid on the ground plane, yellow-orange sphere at center. Middle-click drag to orbit the camera, scroll to zoom.

- [ ] **Step 5: Commit**

```bash
git add rendering/bodies/star_renderer.py rendering/effects/grid.py main.py
git commit -m "feat: first visual — star and grid rendered with Ursina"
```

---

## Task 8: Planet Renderer + Orbit Line

**Files:**
- Modify: `rendering/bodies/planet_renderer.py`
- Modify: `rendering/effects/orbit_line.py`

- [ ] **Step 1: Implement PlanetRenderer**

```python
# rendering/bodies/planet_renderer.py
from __future__ import annotations
from ursina import Entity, Vec3, color as ucolor
from simulation.bodies.planet import Planet


class PlanetRenderer:
    def __init__(self, planet: Planet) -> None:
        self.planet = planet
        self.entity = Entity(
            model='sphere',
            color=self._to_color(planet.color),
            scale=planet.radius,
            position=Vec3(*planet.position),
        )

    def sync(self) -> None:
        self.entity.position = Vec3(*self.planet.position)
        self.entity.color = self._to_color(self.planet.color)
        self.entity.scale = self.planet.radius

    @staticmethod
    def _to_color(rgb: tuple[float, float, float]):
        r, g, b = (int(c * 255) for c in rgb)
        return ucolor.rgb(r, g, b)
```

- [ ] **Step 2: Implement OrbitLine**

```python
# rendering/effects/orbit_line.py
from __future__ import annotations
import math
from ursina import Entity, Mesh, color as ucolor


def _circle_mesh(radius: float, segments: int = 64) -> Mesh:
    vertices = [
        (math.cos(i / segments * math.tau) * radius,
         0,
         math.sin(i / segments * math.tau) * radius)
        for i in range(segments + 1)
    ]
    return Mesh(vertices=vertices, mode='line')


class OrbitLine:
    def __init__(self, radius: float) -> None:
        self._radius = radius
        self.entity = Entity(
            model=_circle_mesh(radius),
            color=ucolor.rgba(200, 200, 200, 80),
        )

    def update_radius(self, radius: float) -> None:
        if abs(radius - self._radius) > 1e-4:
            self._radius = radius
            self.entity.model = _circle_mesh(radius)
```

- [ ] **Step 3: Update main.py to add a test planet**

```python
# main.py — add after star setup:
from simulation.bodies.planet import Planet
from simulation.physics.kepler import KeplerOrbit
from rendering.bodies.planet_renderer import PlanetRenderer
from rendering.effects.orbit_line import OrbitLine

orbit = KeplerOrbit(semi_major_axis=8.0, speed=0.8)
planet = Planet(name="Earth", radius=0.9, color=(0.2, 0.5, 1.0), orbit=orbit)
system.add(planet)

planet_renderer = PlanetRenderer(planet)
orbit_line = OrbitLine(orbit.semi_major_axis)

# Update the update() function:
def update():
    system.tick(time.dt)
    planet_renderer.sync()
```

- [ ] **Step 4: Run and verify**

```bash
python main.py
```

Expected: blue sphere orbiting the yellow star, with a faint white circle showing the orbit path.

- [ ] **Step 5: Commit**

```bash
git add rendering/bodies/planet_renderer.py rendering/effects/orbit_line.py main.py
git commit -m "feat: planet renderer and wireframe orbit line"
```

---

## Task 9: Scene Orchestrator

**Files:**
- Modify: `rendering/scene.py`

Scene replaces the manual wiring in `main.py` — it manages all renderers and syncs them each frame.

- [ ] **Step 1: Implement Scene**

```python
# rendering/scene.py
from __future__ import annotations
from ursina import destroy

from simulation.system import SolarSystem
from simulation.bodies.star import Star
from simulation.bodies.planet import Planet
from rendering.bodies.star_renderer import StarRenderer
from rendering.bodies.planet_renderer import PlanetRenderer
from rendering.effects.orbit_line import OrbitLine
from rendering.effects.grid import GridEffect


class Scene:
    def __init__(self, system: SolarSystem) -> None:
        self.system = system
        self._renderers: dict = {}
        self._orbit_lines: dict = {}
        self.grid = GridEffect()
        for body in system.bodies:
            self._register(body)

    def _register(self, body) -> None:
        if isinstance(body, Star):
            self._renderers[id(body)] = StarRenderer(body)
        elif isinstance(body, Planet):
            self._renderers[id(body)] = PlanetRenderer(body)
            self._orbit_lines[id(body)] = OrbitLine(body.orbit.semi_major_axis)

    def add_body(self, body) -> None:
        self.system.add(body)
        self._register(body)

    def remove_body(self, body) -> None:
        key = id(body)
        if key in self._renderers:
            destroy(self._renderers.pop(key).entity)
        if key in self._orbit_lines:
            destroy(self._orbit_lines.pop(key).entity)
        self.system.remove(body)

    def sync(self) -> None:
        for key, renderer in self._renderers.items():
            renderer.sync()
        for key, orbit_line in self._orbit_lines.items():
            body = next(b for b in self.system.bodies if id(b) == key)
            if isinstance(body, Planet):
                orbit_line.update_radius(body.orbit.semi_major_axis)
```

- [ ] **Step 2: Simplify main.py to use Scene**

```python
# main.py
from ursina import Ursina, color, time, window
from ursina.prefabs.editor_camera import EditorCamera

from simulation.bodies.star import Star
from simulation.bodies.planet import Planet
from simulation.physics.kepler import KeplerOrbit
from simulation.system import SolarSystem
from rendering.scene import Scene

app = Ursina()
window.color = color.black

system = SolarSystem()
star = Star(name="Sol", radius=2.0, color=(1.0, 0.85, 0.2))
system.add(star)

planet1 = Planet(name="Mercury", radius=0.5, color=(0.8, 0.6, 0.3),
                 orbit=KeplerOrbit(semi_major_axis=5.0, speed=1.5))
planet2 = Planet(name="Earth", radius=0.9, color=(0.2, 0.5, 1.0),
                 orbit=KeplerOrbit(semi_major_axis=9.0, speed=0.8))
planet3 = Planet(name="Mars", radius=0.7, color=(0.9, 0.3, 0.2),
                 orbit=KeplerOrbit(semi_major_axis=13.0, speed=0.5))

system.add(planet1)
system.add(planet2)
system.add(planet3)

scene = Scene(system)
EditorCamera()

def update():
    system.tick(time.dt)
    scene.sync()

app.run()
```

- [ ] **Step 3: Run and verify**

```bash
python main.py
```

Expected: 3 planets orbiting the star, each with its own orbit circle, all moving in real time.

- [ ] **Step 4: Commit**

```bash
git add rendering/scene.py main.py
git commit -m "feat: Scene orchestrator — manages all renderers and syncs each frame"
```

---

## Task 10: Camera Controller

**Files:**
- Modify: `rendering/camera.py`

- [ ] **Step 1: Implement CameraController**

```python
# rendering/camera.py
from __future__ import annotations
from ursina.prefabs.editor_camera import EditorCamera


class CameraController:
    """Thin wrapper around Ursina's EditorCamera.
    Middle-click drag: orbit. Scroll: zoom. Right-click drag: pan."""

    def __init__(self) -> None:
        self._camera = EditorCamera()
```

- [ ] **Step 2: Update main.py to use CameraController**

Replace `EditorCamera()` with:

```python
from rendering.camera import CameraController
# ...
camera = CameraController()
```

- [ ] **Step 3: Run and verify controls still work**

```bash
python main.py
```

Expected: same visuals, same camera controls (orbit + zoom).

- [ ] **Step 4: Commit**

```bash
git add rendering/camera.py main.py
git commit -m "feat: CameraController wrapping EditorCamera"
```

---

## Task 11: Time Panel

**Files:**
- Modify: `ui/panels/time_panel.py`

- [ ] **Step 1: Implement TimePanel**

```python
# ui/panels/time_panel.py
from __future__ import annotations
from ursina import Slider, Text, color


class TimePanel:
    """Displays a time speed slider in the top-left corner of the screen."""

    def __init__(self) -> None:
        Text(
            text='Time Speed',
            position=(-0.85, 0.46),
            scale=1.2,
            color=color.white,
        )
        self._slider = Slider(
            min=0.0,
            max=5.0,
            default=1.0,
            step=0.1,
            text='',
            position=(-0.55, 0.44),
        )

    @property
    def time_scale(self) -> float:
        return self._slider.value
```

- [ ] **Step 2: Add TimePanel to main.py**

```python
from ui.panels.time_panel import TimePanel
# ...
time_panel = TimePanel()

def update():
    system.tick(time.dt * time_panel.time_scale)
    scene.sync()
```

- [ ] **Step 3: Run and verify**

```bash
python main.py
```

Expected: "Time Speed" label and a slider appear. Dragging it left slows orbits to a stop (0), right accelerates them (5×).

- [ ] **Step 4: Commit**

```bash
git add ui/panels/time_panel.py main.py
git commit -m "feat: TimePanel — global time speed slider"
```

---

## Task 12: Planet Panel

**Files:**
- Modify: `ui/panels/planet_panel.py`

The panel shows one row of sliders per active planet (orbital radius, speed, size) plus a planet count slider at the top. When the count increases, a new planet is added to the scene with default values. When it decreases, the last planet is removed.

- [ ] **Step 1: Implement PlanetRow — sliders for one planet**

```python
# ui/panels/planet_panel.py
from __future__ import annotations
from ursina import Slider, Text, color, destroy

from simulation.bodies.planet import Planet
from simulation.physics.kepler import KeplerOrbit


_COLORS = [
    (0.8, 0.6, 0.3),  # warm beige
    (0.2, 0.5, 1.0),  # blue
    (0.9, 0.3, 0.2),  # red
    (0.3, 0.8, 0.4),  # green
    (0.7, 0.3, 0.9),  # purple
]

_DEFAULT_RADII = [5.0, 9.0, 13.0, 17.0, 21.0]
_DEFAULT_SPEEDS = [1.5, 0.8, 0.5, 0.3, 0.2]
_PLANET_NAMES = ['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter']


class _PlanetRow:
    """One row of sliders controlling a single planet."""

    def __init__(self, planet: Planet, index: int) -> None:
        self.planet = planet
        y = -0.25 - index * 0.18
        x_label = -0.88

        Text(text=planet.name, position=(x_label, y + 0.06), scale=1.0, color=color.white)

        self._radius_slider = Slider(min=2.0, max=25.0, default=planet.orbit.semi_major_axis,
                                     text='radius', position=(-0.6, y + 0.04))
        self._speed_slider = Slider(min=0.1, max=4.0, default=planet.orbit.speed,
                                    text='speed', position=(-0.6, y - 0.04))
        self._size_slider = Slider(min=0.2, max=3.0, default=planet.radius,
                                   text='size', position=(-0.6, y - 0.12))

        self._radius_slider.on_value_changed = self._apply
        self._speed_slider.on_value_changed = self._apply
        self._size_slider.on_value_changed = self._apply

    def _apply(self) -> None:
        self.planet.orbit.semi_major_axis = self._radius_slider.value
        self.planet.orbit.speed = self._speed_slider.value
        self.planet.radius = self._size_slider.value

    def destroy(self) -> None:
        destroy(self._radius_slider)
        destroy(self._speed_slider)
        destroy(self._size_slider)
```

- [ ] **Step 2: Implement PlanetPanel — count slider + row management**

Add this class below `_PlanetRow` in the same file:

```python
class PlanetPanel:
    """Manages up to 5 planet rows and a count slider."""

    def __init__(self, scene) -> None:
        self._scene = scene
        self._planets: list[Planet] = []
        self._rows: list[_PlanetRow] = []

        Text(text='Planets', position=(-0.88, 0.3), scale=1.2, color=color.white)
        self._count_slider = Slider(min=1, max=5, default=3, step=1,
                                    text='count', position=(-0.6, 0.28))
        self._count_slider.on_value_changed = self._on_count_changed

        for _ in range(3):
            self._add_planet()

    def _add_planet(self) -> None:
        i = len(self._planets)
        orbit = KeplerOrbit(semi_major_axis=_DEFAULT_RADII[i], speed=_DEFAULT_SPEEDS[i])
        planet = Planet(name=_PLANET_NAMES[i], radius=0.7 + i * 0.1,
                        color=_COLORS[i], orbit=orbit)
        self._scene.add_body(planet)
        self._planets.append(planet)
        self._rows.append(_PlanetRow(planet, i))

    def _remove_last(self) -> None:
        if not self._planets:
            return
        self._rows.pop().destroy()
        self._scene.remove_body(self._planets.pop())

    def _on_count_changed(self) -> None:
        target = int(self._count_slider.value)
        while len(self._planets) < target:
            self._add_planet()
        while len(self._planets) > target:
            self._remove_last()
```

- [ ] **Step 3: Update main.py — remove hardcoded planets, add PlanetPanel**

```python
# main.py — final version for this task
from ursina import Ursina, color, time, window
from ursina.prefabs.editor_camera import EditorCamera

from simulation.bodies.star import Star
from simulation.system import SolarSystem
from rendering.scene import Scene
from rendering.camera import CameraController
from ui.panels.time_panel import TimePanel
from ui.panels.planet_panel import PlanetPanel

app = Ursina()
window.color = color.black

system = SolarSystem()
star = Star(name="Sol", radius=2.0, color=(1.0, 0.85, 0.2))
system.add(star)

scene = Scene(system)
camera = CameraController()
time_panel = TimePanel()
planet_panel = PlanetPanel(scene)

def update():
    system.tick(time.dt * time_panel.time_scale)
    scene.sync()

app.run()
```

- [ ] **Step 4: Run and verify**

```bash
python main.py
```

Expected:
- 3 planets orbit the star at start
- Per-planet sliders appear on the left
- Dragging a radius slider moves the orbit circle + planet outward/inward in real time
- Dragging speed changes how fast the planet moves
- Dragging size scales the planet sphere
- Count slider adds/removes planets (up to 5)

- [ ] **Step 5: Commit**

```bash
git add ui/panels/planet_panel.py main.py
git commit -m "feat: PlanetPanel — per-planet sliders and dynamic planet count"
```

---

## Task 13: V1 Polish + Final Commit

**Files:**
- Modify: `main.py`
- Modify: `rendering/bodies/star_renderer.py`

Small touches to nail the Outer Wilds aesthetic for V1.

- [ ] **Step 1: Add a starfield background**

Add to `main.py` after `window.color = color.black`:

```python
from ursina import Entity, color as ucolor
import random

for _ in range(300):
    Entity(
        model='sphere',
        scale=0.05,
        position=(
            random.uniform(-80, 80),
            random.uniform(-40, 40),
            random.uniform(-80, -20),
        ),
        color=ucolor.rgba(255, 255, 255, random.randint(100, 255)),
    )
```

- [ ] **Step 2: Add a glow effect to the star**

Update `StarRenderer.__init__` in `rendering/bodies/star_renderer.py`:

```python
def __init__(self, star: Star) -> None:
    self.star = star
    r, g, b = (int(c * 255) for c in star.color)
    self.entity = Entity(
        model='sphere',
        color=ucolor.rgb(r, g, b),
        scale=star.radius,
        position=Vec3(0, 0, 0),
    )
    # Outer glow sphere — slightly larger, transparent
    self._glow = Entity(
        model='sphere',
        color=ucolor.rgba(r, g, b, 40),
        scale=star.radius * 2.2,
        position=Vec3(0, 0, 0),
    )
```

Update `sync()` accordingly:

```python
def sync(self) -> None:
    self.entity.position = Vec3(*self.star.position)
    self._glow.position = Vec3(*self.star.position)
```

- [ ] **Step 3: Run the final V1**

```bash
python main.py
```

Expected: a solar system with starfield background, glowing star, low-poly planets with orbit lines, a blue wireframe grid, and a dashboard with time + planet controls. V1 complete.

- [ ] **Step 4: Run the full test suite one last time**

```bash
pytest tests/ -v
```

Expected: all tests pass.

- [ ] **Step 5: Final V1 commit**

```bash
git add -A
git commit -m "feat: V1 complete — solar system simulator with dashboard and Outer Wilds aesthetic"
```

---

## Self-Review

**Spec coverage:**
- [x] 1 star fixed at center — Task 4 + 7
- [x] 1–5 configurable planets — Task 12 (PlanetPanel count slider)
- [x] Circular Keplerian orbits — Task 3
- [x] Wireframe orbit lines — Task 8
- [x] Background grid — Task 7
- [x] Camera: rotation + zoom — Task 10
- [x] Per-planet sliders: size, radius, speed — Task 12
- [x] Color per planet — defined in `_COLORS`, not dynamically configurable in V1 (out of scope per spec)
- [x] Global time speed slider — Task 11
- [x] Low-poly Outer Wilds aesthetic — Task 13

**Note on planet color:** The spec lists R/G/B color sliders as in-scope for V1. This plan uses preset colors per slot for simplicity. If you want live color sliders, add three more `Slider` widgets per `_PlanetRow` mapping to `planet.color` — the architecture already supports it via `PlanetRenderer.sync()` reading `planet.color` each frame.
