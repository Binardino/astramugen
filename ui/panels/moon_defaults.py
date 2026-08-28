"""Default moons for a fixed set of planets, keyed by planet name.

Consumed by `PlanetPanel._add_planet` (see `ui/panels/planet_panel.py`) to
attach moons when a planet is created. Per the V2 scope decision (see
`docs/superpowers/specs/2026-06-11-astramugen-design.md#v2-scope--detail`),
moon counts are fixed in code and not yet dashboard-configurable — kept at
0-2 per planet, not the full real moon count (Jupiter alone has 95).

Each entry is a list of (name, visual_size, color, orbital_radius, speed)
tuples, same stylized/compressed convention as `PLANET_DEFAULTS`. Planets
not listed here (the default) get no moons.
"""

MOON_DEFAULTS = {
    # A single moon, matching Earth's real single natural satellite.
    "Earth": [
        ("Luna", 0.25, (0.7, 0.7, 0.7), 1.2, 2.0),
    ],
    # Mars's two real moons: small, fast, close-orbiting captured asteroids.
    "Mars": [
        ("Phobos", 0.12, (0.6, 0.5, 0.45), 0.9, 3.0),
        ("Deimos", 0.1, (0.65, 0.55, 0.5), 1.4, 1.5),
    ],
}
