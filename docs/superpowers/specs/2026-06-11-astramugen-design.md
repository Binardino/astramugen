# Astramugen — Design Spec

**Date:** 2026-06-11
**Engine:** Ursina Engine (Python)
**Style:** Low-poly Outer Wilds (warm, faceted) + wireframe/grid overlay
**Physics:** Keplerian orbits (v1), optional Newtonian gravity (v5)

---

## Vision

A 3D solar system simulator, 100% Python, with an art direction inspired by Outer Wilds. The user configures celestial bodies through a dashboard, watches them orbit in real time, and will later trigger catastrophic events (supernova, collisions). The project is a vehicle for progressive Python practice — each version adds one isolated feature.

---

## Architecture

Three strictly separated layers plus an abstract core. **Hard rule: `simulation/` never imports Ursina. `rendering/` never computes orbits.**

```
astramugen/
├── core/                        ← contracts between layers (abstract base classes)
│   ├── body_base.py             ← CelestialBody (ABC)
│   └── renderer_base.py        ← Renderer (ABC)
│
├── simulation/                  ← pure Python, zero Ursina, testable with pytest
│   ├── system.py                ← SolarSystem: registry + tick(dt)
│   ├── bodies/
│   │   ├── star.py              ← Star
│   │   ├── planet.py            ← Planet
│   │   ├── moon.py              ← Moon              (v2)
│   │   ├── asteroid.py          ← Asteroid          (v3)
│   │   └── comet.py             ← Comet             (v3)
│   ├── physics/
│   │   ├── kepler.py            ← KeplerOrbit       (v1)
│   │   └── newton.py            ← NewtonSolver      (v5)
│   └── events/
│       ├── supernova.py         ← SupernovaEvent    (v4)
│       └── collision.py        ← CollisionEvent    (v4)
│
├── rendering/                   ← everything that touches Ursina
│   ├── scene.py                 ← orchestrates renderers, sync() each frame
│   ├── camera.py                ← camera control (rotation, zoom)
│   ├── bodies/
│   │   ├── star_renderer.py
│   │   ├── planet_renderer.py
│   │   └── moon_renderer.py     (v2)
│   └── effects/
│       ├── orbit_line.py        ← wireframe orbit trail        (v1)
│       ├── grid.py              ← background reference grid    (v1)
│       ├── atmosphere.py        ← halo/glow around planets     (v2)
│       └── supernova_fx.py      ← supernova visual effect      (v4)
│
├── ui/                          ← Ursina dashboard
│   ├── hud.py                   ← informational overlay
│   └── panels/
│       ├── planet_panel.py      ← per-planet sliders           (v1)
│       ├── time_panel.py        ← time speed control           (v1)
│       └── system_panel.py      ← planet count, generation     (v2)
│
└── main.py                      ← entry point, wires everything together
```

---

## Data Flow

```
UI (sliders) ──commands──► SolarSystem ──state──► Scene.sync() ──► Ursina Entities
                                ▲
                            tick(dt)
                          (every frame)
```

- UI writes directly to `SolarSystem.bodies` properties
- `SolarSystem.tick(dt)` calls `body.update(dt)` on each body
- `Scene.sync()` reads `body.position` and updates Ursina entities
- The renderer does not know about physics; the simulation does not know about Ursina

---

## Key Data Structures

```python
# core/body_base.py
@dataclass
class CelestialBody(ABC):
    name: str
    radius: float
    color: tuple[float, float, float]
    position: tuple[float, float, float] = (0, 0, 0)

    @abstractmethod
    def update(self, dt: float) -> None: ...
```

```python
# simulation/physics/kepler.py
@dataclass
class KeplerOrbit:
    semi_major_axis: float   # orbital radius
    eccentricity: float      # 0 = circle, <1 = ellipse
    inclination: float       # degrees
    speed: float             # angular speed factor
    time: float = 0.0

    def advance(self, dt: float) -> None:
        self.time += dt * self.speed

    def position_at(self, t: float) -> tuple[float, float, float]:
        ...  # returns (x, y, z)
```

```python
# simulation/system.py
class SolarSystem:
    bodies: list[CelestialBody]

    def tick(self, dt: float) -> None:
        for body in self.bodies:
            body.update(dt)
```

---

## Art Direction

- **Planets:** Ursina low-poly spheres (low subdivision count), warm saturated colors
- **Star:** larger sphere, emissive material, yellow-orange glow
- **Orbits:** thin semi-transparent white/grey wireframe lines, always visible
- **Grid:** reference plane in fine wireframe, deep blue color
- **Background:** deep black with static star particles
- **Color palette (v1):** Outer Wilds-inspired — saturated oranges, blues, greens, purples

---

## Version Roadmap

| Version | Name | Content |
|---------|------|---------|
| **V1** | *The skeleton runs* | Star + 1–5 planets, circular Keplerian orbits, grid + orbit lines, dashboard (size/color/radius/speed per planet), time control |
| **V2** | *The system breathes* | Moons, atmosphere/halos, basic procedural generation, elliptical orbits |
| **V3** | *The system populates* | Asteroid belt, long-orbit comets |
| **V4** | *The system dramatizes* | Supernova, planet collision + visual effects |
| **V5** | *The system deepens* | Optional Newtonian physics, binary star system |
| **V6** | *The system darkens* | Black hole mode, accretion disk |
| **V7** | *The system is shared* | Screenshot/video export, JSON save/load, advanced procedural generation |

---

## V1 Scope — Detail

**In scope:**
- 1 star fixed at the center
- 1 to 5 configurable planets (count, size, color, orbital radius, speed)
- Circular Keplerian orbits (eccentricity = 0)
- Wireframe orbit lines + background grid
- Camera: mouse rotation + scroll zoom
- Dashboard: planet count slider, per-planet sliders (size, R/G/B color, radius, speed), global time speed slider

**Out of scope for V1:**
- Moons, asteroids, comets
- Elliptical orbits
- Atmosphere effects
- Procedural generation
- Any events (supernova, collision)

---

## V2 Scope — Detail

**In scope:**
- Elliptical orbits using the true Kepler equation (mean anomaly → eccentric anomaly via
  Newton-Raphson → position). Planets speed up near periapsis and slow down near apoapsis,
  matching Kepler's second law. `eccentricity = 0` reduces exactly to V1's circular case.
- Moons: each planet gets a fixed, non-configurable set of 0–2 moons defined in code
  (not yet exposed on the dashboard).
- Atmosphere/halo effect on planets, reusing the star's fake-bloom technique (a single
  translucent concentric sphere, more subtle than the star's two-layer version).
- A "Randomize" button that rerolls existing planet sliders' values within their current
  min/max ranges.

**Deferred (candidate for a later version, not blocking V2):**
- Per-planet moon count slider.
- Toggle between the "real solar system" preset (`PLANET_DEFAULTS` already models this)
  and an "imaginary randomized system" — needs only a second data source and a small
  dispatch in `PlanetPanel`, no architecture change.
- A dedicated `simulation/generation.py` system generator (archetypes, spacing rules)
  replacing the simple randomizer.

**Out of scope for V2:**
- Asteroids, comets (V3).
- Newtonian gravity between bodies — V2's Kepler equation is still a fixed elliptical
  orbit around one focus, not N-body physics (V5).
- Any events: supernova, collision (V4).

---

## Backlog — Unscheduled Ideas

Ideas captured for later, not yet assigned to a version.

- **Real eclipse prediction (solar + lunar).** Once a "real solar system" preset exists
  (see the real/imaginary toggle deferred above), add a feature to compute and predict
  actual past and future solar/lunar eclipses of the real Moon against real calendar
  dates. This needs genuine ephemeris data/astronomical algorithms — not the stylized,
  compressed orbits used for the visual simulation — so it would live in its own module
  (e.g. `simulation/astronomy/eclipses.py`), decoupled from `KeplerOrbit`, and would take
  a real date as input rather than sim time. Likely needs a proper astronomical library
  (e.g. Skyfield) rather than hand-rolled Meeus-algorithm math. Only meaningful once the
  "real solar system" mode exists — not before.

- **Real moons for the real-solar-system preset.** When the real/imaginary toggle
  (deferred above) is built, populate real planets with their real moons — but curated
  to major moons only, not the full real count. Real moon counts are wildly uneven and
  mostly tiny/irregular/captured bodies: Jupiter has 95 confirmed moons, Saturn 146+, vs.
  0 for Mercury/Venus, 1 for Earth, 2 for Mars. Rendering the full count would clutter the
  low-poly scene for negligible visual payoff. Curated set: the 4 Galilean moons for
  Jupiter, Titan for Saturn, Triton for Neptune, Phobos + Deimos for Mars, the Moon for
  Earth. Needs a `MOON_DEFAULTS`-like data source per planet (name, size, color, orbital
  radius/speed), stylized the same way `PLANET_DEFAULTS` already is — not real
  astronomical units.

- **Per-planet ring systems (Saturn-style).** Not the same thing as the V3 asteroid
  belt (that one orbits the star, between planets, like the real Mars-Jupiter belt) —
  this is a flat ring/disc around an individual planet. Simulating it as thousands of
  individual `CelestialBody` instances would be prohibitively expensive and pointless
  visually; more realistic approach is a static stylized ring mesh (flat annulus/torus)
  purely in `rendering/effects/` (e.g. `planet_rings.py`), with no `simulation/`
  counterpart at all — same treatment as the background grid or starfield, which are
  visual-only with nothing to simulate. Would need a per-planet toggle/option, likely
  alongside the moon-count decision once that becomes dashboard-configurable.

---

## Dependencies

- `ursina` — 3D engine + GUI
- `python >= 3.11`
- No external dependency for `simulation/` (numpy optional in v5 for Newton)
