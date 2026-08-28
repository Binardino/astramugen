# Astramugen V2 — Implementation Plan

**Goal:** Elliptical Keplerian orbits (true equation, not a geometric approximation), moons
orbiting planets, an atmosphere/halo effect on planets, and a "Randomize" dashboard button.

**Architecture reminder:** `simulation/` never imports Ursina. `rendering/` never computes
orbits. Moons live inside `Planet.moons`, never in `SolarSystem.bodies` — `Planet.update()`
is responsible for advancing and world-positioning its own moons, so `SolarSystem.tick()`
needs no changes at all.

**Decisions locked in for V2** (see `docs/superpowers/specs/2026-06-11-astramugen-design.md#v2-scope--detail`):
- Elliptical orbits use the true Kepler equation (Newton-Raphson solve), not a
  constant-angular-speed ellipse.
- Moons: fixed 0–2 per planet, defined in code — no dashboard control yet.
- "Basic procedural generation" = a Randomize button rerolling existing slider ranges.

---

## File Map

| File | Change |
|------|--------|
| `simulation/physics/kepler.py` | Add `eccentricity`, Kepler equation solver |
| `simulation/bodies/moon.py` | New `Moon` — orbits a parent `Planet` in local space |
| `simulation/bodies/planet.py` | Add `moons: list[Moon]`, update() advances + positions them |
| `rendering/effects/orbit_line.py` | Draw a true ellipse (focus at origin), support a moving center |
| `rendering/bodies/moon_renderer.py` | Ursina entity for a moon |
| `rendering/effects/atmosphere.py` | Single-layer translucent halo, reusable by any body |
| `rendering/bodies/planet_renderer.py` | Attach an `AtmosphereEffect` |
| `rendering/scene.py` | Register/destroy moon renderers + orbit lines recursively |
| `ui/panels/planet_panel.py` | Add a "Randomize" button |
| `tests/simulation/physics/test_kepler.py` | New tests for eccentric orbits |
| `tests/simulation/bodies/test_moon.py` | New test file |

---

## Task 1: Elliptical KeplerOrbit

**Files:** Modify `simulation/physics/kepler.py`, `tests/simulation/physics/test_kepler.py`

The existing 5 circular-orbit tests must keep passing unchanged — `eccentricity` defaults
to `0.0`, and the solver must reduce to `E = M` exactly in that case.

- [x] **Step 1: Write the failing tests (append to the existing file)**

```python
# tests/simulation/physics/test_kepler.py — add these
import math
from simulation.physics.kepler import KeplerOrbit


def test_eccentric_orbit_periapsis_at_zero_mean_anomaly():
    # At M=0, a body on an elliptical orbit sits at periapsis: distance = a(1-e)
    orbit = KeplerOrbit(semi_major_axis=10.0, eccentricity=0.5, speed=1.0)
    x, y, z = orbit.position_at(0.0)
    r = math.sqrt(x ** 2 + z ** 2)
    assert abs(r - 10.0 * (1 - 0.5)) < 1e-6


def test_eccentric_orbit_apoapsis_at_half_turn_mean_anomaly():
    # At M=pi, a body sits at apoapsis: distance = a(1+e)
    orbit = KeplerOrbit(semi_major_axis=10.0, eccentricity=0.5, speed=1.0)
    x, y, z = orbit.position_at(math.pi)
    r = math.sqrt(x ** 2 + z ** 2)
    assert abs(r - 10.0 * (1 + 0.5)) < 1e-6


def test_eccentric_orbit_radius_stays_within_periapsis_and_apoapsis():
    orbit = KeplerOrbit(semi_major_axis=10.0, eccentricity=0.7, speed=1.0)
    periapsis, apoapsis = 10.0 * (1 - 0.7), 10.0 * (1 + 0.7)
    for angle in [0.1, 1.0, 2.0, 3.0, 4.5, 6.0]:
        x, y, z = orbit.position_at(angle)
        r = math.sqrt(x ** 2 + z ** 2)
        assert periapsis - 1e-6 <= r <= apoapsis + 1e-6


def test_solver_converges_for_high_eccentricity():
    orbit = KeplerOrbit(semi_major_axis=5.0, eccentricity=0.9, speed=1.0)
    x, y, z = orbit.position_at(1.3)  # arbitrary mean anomaly, just must not raise/hang
    assert math.isfinite(x) and math.isfinite(z)


def test_zero_eccentricity_matches_circular_behavior():
    # Guards the backward-compatibility guarantee: e=0 must behave exactly like V1.
    orbit = KeplerOrbit(semi_major_axis=5.0, eccentricity=0.0, speed=1.0)
    x, y, z = orbit.position_at(math.pi / 2)
    assert abs(x) < 1e-9
    assert abs(z - 5.0) < 1e-9
```

- [x] **Step 2: Run to confirm failure**

```bash
uv run pytest tests/simulation/physics/test_kepler.py -v
```

Expected: the 5 new tests fail (missing `eccentricity` argument), the 5 old tests still pass.

- [x] **Step 3: Implement the eccentric anomaly solver + elliptical position**

```python
# simulation/physics/kepler.py
from __future__ import annotations
import math
from dataclasses import dataclass


def _solve_eccentric_anomaly(mean_anomaly: float, eccentricity: float,
                              tolerance: float = 1e-9, max_iterations: int = 50) -> float:
    """Solve Kepler's equation M = E - e*sin(E) for E via Newton-Raphson.

    No closed-form solution exists for E, so this iterates from an initial
    guess E0 = M until successive corrections fall below `tolerance`.
    """
    E = mean_anomaly
    for _ in range(max_iterations):
        delta = (E - eccentricity * math.sin(E) - mean_anomaly) / (1 - eccentricity * math.cos(E))
        E -= delta
        if abs(delta) < tolerance:
            break
    return E


@dataclass
class KeplerOrbit:
    """Describes an elliptical Keplerian orbit with the star at one focus.

    Attributes:
        semi_major_axis: half the longest diameter of the ellipse
        speed: angular speed multiplier (1.0 = real-time, 2.0 = twice as fast)
        eccentricity: 0 = circle, closer to 1 = more elongated ellipse
        inclination: tilt of the orbital plane in degrees (0 = flat on XZ plane)
        time: accumulated time, used as the mean anomaly in position_at()
    """

    semi_major_axis : float
    speed           : float
    eccentricity    : float = 0.0
    inclination     : float = 0.0
    time            : float = 0.0

    def advance(self, dt: float) -> None:
        """Move the orbit forward by one simulation step."""
        self.time += dt * self.speed

    def position_at(self, t: float) -> tuple[float, float, float]:
        """Return the (x, y, z) position at mean anomaly t (radians).

        t is treated as the mean anomaly M. It's converted to the eccentric
        anomaly E by solving Kepler's equation, then to a perifocal-frame
        position with the focus (the star) at the origin. With eccentricity=0,
        E equals M exactly and this reduces to the V1 circular formula.
        """
        E = _solve_eccentric_anomaly(t, self.eccentricity)
        x = self.semi_major_axis * (math.cos(E) - self.eccentricity)
        z = self.semi_major_axis * math.sqrt(1 - self.eccentricity ** 2) * math.sin(E)
        rad = math.radians(self.inclination)
        y = z * math.sin(rad)
        z = z * math.cos(rad)
        return (x, y, z)
```

- [x] **Step 4: Run all kepler tests**

```bash
uv run pytest tests/simulation/physics/test_kepler.py -v
```

Expected: 10 passed (5 old + 5 new).

- [x] **Step 5: Run the full suite to catch any regression in Planet/System tests**

```bash
uv run pytest tests/ -v
```

Expected: all passed — `Planet`/`SolarSystem` tests only use `eccentricity`'s default (0.0).

- [x] **Step 6: Commit**

```bash
git add simulation/physics/kepler.py tests/simulation/physics/test_kepler.py
git commit -m "feat: elliptical orbits via true Kepler equation solver"
```

---

## Task 2: Elliptical Orbit Line Rendering

**Files:** Modify `rendering/effects/orbit_line.py`

No pytest here — verify visually. The ellipse mesh must place the star's focus (not the
ellipse's geometric center) at the local origin, using the same perifocal formula as
`KeplerOrbit.position_at`, sampled directly over the eccentric anomaly `E` (no need to
solve Kepler's equation just to draw the static shape — uniform `E` sampling traces the
correct ellipse regardless of how a body's *speed* varies along it).

- [x] **Step 1: Update `OrbitLine` to take `eccentricity` and draw an ellipse**

```python
# rendering/effects/orbit_line.py
from __future__ import annotations
import math
from ursina import Entity, Mesh, Vec3, color as ucolor


def _ellipse_mesh(semi_major_axis: float, eccentricity: float, segments: int = 64) -> Mesh:
    """Build a flat XZ-plane ellipse mesh with a focus at the local origin.

    Same perifocal formula as KeplerOrbit.position_at, sampled uniformly over
    the eccentric anomaly to trace the static path (not the timed motion).
    """
    a, e = semi_major_axis, eccentricity
    b = a * math.sqrt(1 - e ** 2)
    vertices = [
        (a * math.cos(E) - a * e, 0, b * math.sin(E))
        for E in (i / segments * math.tau for i in range(segments + 1))
    ]
    return Mesh(vertices=vertices, mode='line')


class OrbitLine:
    """Static wireframe ellipse representing a body's orbital path on the XZ plane.

    Can be re-centered via set_center() so a moon's orbit line follows its
    parent planet each frame.
    """

    def __init__(self, semi_major_axis: float, eccentricity: float = 0.0) -> None:
        self._radius = semi_major_axis
        self._eccentricity = eccentricity
        self.entity = Entity(
            model=_ellipse_mesh(semi_major_axis, eccentricity),
            color=ucolor.Color(200/255, 200/255, 200/255, 80/255),
            unlit=True,
        )

    def update_radius(self, semi_major_axis: float, eccentricity: float | None = None) -> None:
        """Rebuild the ellipse mesh if the orbit's shape has changed."""
        eccentricity = self._eccentricity if eccentricity is None else eccentricity
        if abs(semi_major_axis - self._radius) > 1e-4 or abs(eccentricity - self._eccentricity) > 1e-4:
            self._radius = semi_major_axis
            self._eccentricity = eccentricity
            self.entity.model = _ellipse_mesh(semi_major_axis, eccentricity)

    def set_center(self, position: tuple[float, float, float]) -> None:
        """Move the whole orbit line to follow a moving parent (used for moons)."""
        self.entity.position = Vec3(*position)
```

- [x] **Step 2: Run and verify visually**

```bash
uv run python main.py
```

Expected: orbit lines are now visibly elongated ellipses once a planet's eccentricity is
non-zero (still circular for e=0, since existing planets don't set eccentricity yet).

- [x] **Step 3: Commit**

```bash
git add rendering/effects/orbit_line.py
git commit -m "feat: OrbitLine draws a true ellipse with a movable center"
```

---

## Task 3: Moon (Simulation Layer)

**Files:** Modify `simulation/bodies/moon.py`, `simulation/bodies/planet.py`,
create `tests/simulation/bodies/test_moon.py`

A `Moon` computes its own position in **local space** (relative to its parent). `Planet`
is the one that knows about the parent relationship — it calls `moon.update(dt)`, then
translates the moon's local position into world space by adding its own position. This
keeps `CelestialBody.update(dt)`'s single-argument signature intact for every body type.

- [x] **Step 1: Write the failing tests**

```python
# tests/simulation/bodies/test_moon.py
import math
from simulation.bodies.moon import Moon
from simulation.bodies.planet import Planet
from simulation.physics.kepler import KeplerOrbit


def _make_moon(radius=1.5, speed=2.0) -> Moon:
    orbit = KeplerOrbit(semi_major_axis=radius, speed=speed)
    return Moon(name="Luna", radius=0.3, color=(0.7, 0.7, 0.7), orbit=orbit)


def test_moon_position_is_local_after_update():
    moon = _make_moon(radius=1.5)
    moon.update(1.0)
    x, y, z = moon.position
    r = math.sqrt(x ** 2 + z ** 2)
    assert abs(r - 1.5) < 1e-6


def test_planet_offsets_moon_position_by_its_own_position():
    orbit = KeplerOrbit(semi_major_axis=10.0, speed=1.0)
    planet = Planet(name="Earth", radius=1.0, color=(0.2, 0.5, 1.0), orbit=orbit)
    planet.moons.append(_make_moon(radius=1.5))

    planet.update(1.0)

    px, py, pz = planet.position
    mx, my, mz = planet.moons[0].position
    local_r = math.sqrt((mx - px) ** 2 + (mz - pz) ** 2)
    assert abs(local_r - 1.5) < 1e-6


def test_planet_with_no_moons_still_updates():
    orbit = KeplerOrbit(semi_major_axis=10.0, speed=1.0)
    planet = Planet(name="Earth", radius=1.0, color=(0.2, 0.5, 1.0), orbit=orbit)
    planet.update(1.0)  # must not raise with an empty moons list
    assert planet.moons == []
```

- [x] **Step 2: Run to confirm failure**

```bash
uv run pytest tests/simulation/bodies/test_moon.py -v
```

Expected: `ImportError` / `AttributeError` — `Moon` is empty, `Planet` has no `moons` field.

- [x] **Step 3: Implement Moon**

```python
# simulation/bodies/moon.py
"""
Moon — a celestial body that orbits its parent Planet, not the star.

update(dt) computes a position relative to the parent's origin. It is the
owning Planet's responsibility (see Planet.update()) to translate that local
position into world space — this keeps CelestialBody.update(dt)'s single-
argument signature the same for every body type.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from core.body_base import CelestialBody
from simulation.physics.kepler import KeplerOrbit


@dataclass
class Moon(CelestialBody):
    """A body orbiting a Planet. self.position is LOCAL until the parent offsets it."""

    orbit: KeplerOrbit = field(
        default_factory=lambda: KeplerOrbit(semi_major_axis=1.5, speed=2.0)
    )

    def update(self, dt: float) -> None:
        """Advance the local orbit. Position remains relative to the parent planet."""
        self.orbit.advance(dt)
        self.position = self.orbit.position_at(self.orbit.time)
```

- [x] **Step 4: Extend Planet with a moons list**

```python
# simulation/bodies/planet.py
from __future__ import annotations
from dataclasses import dataclass, field
from core.body_base import CelestialBody
from simulation.physics.kepler import KeplerOrbit
from simulation.bodies.moon import Moon


@dataclass
class Planet(CelestialBody):
    """An orbiting body. Its position is recomputed every tick from its KeplerOrbit."""

    orbit: KeplerOrbit = field(
        default_factory=lambda: KeplerOrbit(semi_major_axis=5.0, speed=1.0)
    )
    moons: list[Moon] = field(default_factory=list)

    def update(self, dt: float) -> None:
        """Advance the orbit, then advance and world-position every attached moon."""
        self.orbit.advance(dt)
        self.position = self.orbit.position_at(self.orbit.time)
        for moon in self.moons:
            moon.update(dt)
            moon.position = tuple(p + m for p, m in zip(self.position, moon.position))
```

- [x] **Step 5: Run tests**

```bash
uv run pytest tests/simulation/bodies/test_moon.py tests/simulation/bodies/test_planet.py -v
```

Expected: all passed — existing Planet tests still pass since `moons` defaults to `[]`.

- [x] **Step 6: Run the full suite**

```bash
uv run pytest tests/ -v
```

Expected: all passed.

- [x] **Step 7: Commit**

```bash
git add simulation/bodies/moon.py simulation/bodies/planet.py tests/simulation/bodies/test_moon.py
git commit -m "feat: Moon orbiting its parent Planet in local space"
```

---

## Task 4: Moon Renderer + Scene Wiring

**Files:** Modify `rendering/bodies/moon_renderer.py`, `rendering/scene.py`

No pytest — verify visually.

- [x] **Step 1: Implement MoonRenderer (same pattern as PlanetRenderer)**

```python
# rendering/bodies/moon_renderer.py
from __future__ import annotations
from ursina import Entity, Vec3, color as ucolor
from simulation.bodies.moon import Moon


class MoonRenderer:
    """Creates and manages the Ursina sphere entity for a Moon."""

    def __init__(self, moon: Moon) -> None:
        self.moon = moon
        r, g, b = moon.color
        self.entity = Entity(
            model    = 'sphere',
            color    = ucolor.Color(r, g, b, 1),
            scale    = moon.radius,
            position = Vec3(*moon.position),
            unlit    = True,
        )

    def sync(self) -> None:
        self.entity.position = Vec3(*self.moon.position)
        self.entity.scale    = self.moon.radius
```

- [x] **Step 2: Wire moons into Scene — register, sync, and destroy recursively**

```python
# rendering/scene.py — extend _register, sync, and remove_body
from simulation.bodies.moon import Moon
from rendering.bodies.moon_renderer import MoonRenderer

# in _register(self, body):
if isinstance(body, Planet):
    self._renderers[id(body)] = PlanetRenderer(body)
    self._orbit_lines[id(body)] = OrbitLine(body.orbit.semi_major_axis, body.orbit.eccentricity)
    for moon in body.moons:
        self._renderers[id(moon)] = MoonRenderer(moon)
        self._orbit_lines[id(moon)] = OrbitLine(moon.orbit.semi_major_axis, moon.orbit.eccentricity)

# in sync(self): after syncing a planet, re-center its moons' orbit lines
for key, renderer in self._renderers.items():
    renderer.sync()
for body in self.system.bodies:
    if isinstance(body, Planet):
        for moon in body.moons:
            self._orbit_lines[id(moon)].set_center(body.position)

# in remove_body(self, body): also tear down a planet's moons
if isinstance(body, Planet):
    for moon in body.moons:
        destroy(self._renderers.pop(id(moon)).entity)
        destroy(self._orbit_lines.pop(id(moon)).entity)
```

Adapt exact placement to the current file structure — the snippets above show the three
insertion points, not a full file rewrite.

- [x] **Step 3: Give at least one PLANET_DEFAULTS entry moons, to see them**

Temporarily (or permanently, your call) attach 1–2 `Moon` instances to a `Planet` in
`PlanetPanel._add_planet` for testing, e.g. give Earth one moon and Jupiter two.

- [x] **Step 4: Run and verify visually**

```bash
uv run python main.py
```

Expected: small spheres orbiting a planet, with their own faint orbit ellipse that moves
together with the planet as it orbits the star.

- [x] **Step 5: Commit**

```bash
git add rendering/bodies/moon_renderer.py rendering/scene.py ui/panels/planet_panel.py
git commit -m "feat: render moons and wire them into Scene"
```

---

## Task 5: Atmosphere / Halo Effect on Planets

**Files:** Modify `rendering/effects/atmosphere.py`, `rendering/bodies/planet_renderer.py`

No pytest — verify visually. Reuses the fake-bloom technique already validated on the star,
but as a single, subtler layer.

- [x] **Step 1: Implement AtmosphereEffect**

```python
# rendering/effects/atmosphere.py
"""
AtmosphereEffect — a single translucent halo sphere around a body.

Same fake-bloom technique as StarRenderer's glow, but one layer only —
planets need a subtle rim, not a dramatic corona.
"""

from __future__ import annotations
from ursina import Entity, Vec3, color as ucolor


class AtmosphereEffect:
    def __init__(self, body_color: tuple[float, float, float], body_radius: float) -> None:
        r, g, b = body_color
        self.entity = Entity(
            model    = 'sphere',
            color    = ucolor.Color(r, g, b, 0.25),
            scale    = body_radius * 1.3,
            position = Vec3(0, 0, 0),
            unlit    = True,
        )

    def sync(self, position: tuple[float, float, float], radius: float) -> None:
        self.entity.position = Vec3(*position)
        self.entity.scale    = radius * 1.3
```

- [x] **Step 2: Attach it in PlanetRenderer**

```python
# rendering/bodies/planet_renderer.py — add to __init__ and sync()
from rendering.effects.atmosphere import AtmosphereEffect

# in __init__, after creating self.entity:
self._atmosphere = AtmosphereEffect(planet.color, planet.radius)

# in sync():
self._atmosphere.sync(self.planet.position, self.planet.radius)
```

- [x] **Step 3: Run and verify visually**

```bash
uv run python main.py
```

Expected: each planet has a faint tinted halo, more subtle than the star's.

- [x] **Step 4: Commit**

```bash
git add rendering/effects/atmosphere.py rendering/bodies/planet_renderer.py
git commit -m "feat: AtmosphereEffect halo on planets"
```

---

## Task 6: Randomize Button

**Files:** Modify `ui/panels/planet_panel.py`

No pytest — verify visually.

- [ ] **Step 1: Add a Button that rerolls existing slider values**

```python
# ui/panels/planet_panel.py
import random
from ursina import Button

# in PlanetPanel.__init__, after the count slider:
self._randomize_button = Button(
    text='Randomize',
    position=(-0.6, 0.28),
    scale=(0.15, 0.05),
)
self._randomize_button.on_click = self._randomize

# new method on PlanetPanel:
def _randomize(self) -> None:
    """Reroll every active planet's sliders within their existing min/max ranges."""
    for row in self._rows:
        row._radius_slider.value = random.uniform(row._radius_slider.min, row._radius_slider.max)
        row._speed_slider.value  = random.uniform(row._speed_slider.min, row._speed_slider.max)
        row._size_slider.value   = random.uniform(row._size_slider.min, row._size_slider.max)
        row._apply()
```

- [ ] **Step 2: Run and verify**

```bash
uv run python main.py
```

Expected: clicking "Randomize" moves every planet's sliders to new random positions and the
planets/orbits update live to match.

- [ ] **Step 3: Commit**

```bash
git add ui/panels/planet_panel.py
git commit -m "feat: Randomize button rerolls planet sliders"
```

---

## Task 7: V2 Polish + Final Test Run

- [ ] **Step 1: Run the full test suite one last time**

```bash
uv run pytest tests/ -v
```

Expected: all tests pass (Task 1 + Task 3 additions, no regressions).

- [ ] **Step 2: Visual pass**

```bash
uv run python main.py
```

Check: elliptical orbits visibly speed up near the star, moons orbit their planets and
follow them, halos are visible but subtle on planets, Randomize works.

- [ ] **Step 3: Final V2 commit (once everything above is confirmed)**

```bash
git commit --allow-empty -m "feat: V2 complete — elliptical orbits, moons, atmospheres, randomize"
```

---

## Self-Review

**Spec coverage** (`docs/superpowers/specs/2026-06-11-astramugen-design.md#v2-scope--detail`):
- [x] Elliptical orbits (true Kepler equation) — Task 1
- [x] Moons (fixed 0–2 per planet) — Task 3, 4
- [x] Atmosphere/halo on planets — Task 5
- [ ] Basic procedural generation (Randomize button) — Task 6
- [ ] Deferred: per-planet moon count slider, real/imaginary system toggle, dedicated
      generator module — documented in the spec as follow-up work, not V2 scope.
