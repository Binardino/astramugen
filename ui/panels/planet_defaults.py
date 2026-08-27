"""Default values for dynamically created planets, indexed by slot.

Each entry is a tuple of (name, orbital_radius, speed, visual_size, color,
eccentricity), consumed by `PlanetPanel._add_planet` (see
`ui/panels/planet_panel.py`) to build a new `Planet` + `KeplerOrbit`
whenever the planet count slider is increased. List index 0 is used for
the first planet added, index 1 for the second, and so on — the order
below fixes the slot order shown in the dashboard.

Values are stylized for the low-poly art direction (see
`docs/superpowers/specs/2026-06-11-astramugen-design.md`), not scaled to
real astronomical units: orbital_radius and speed follow the real
ordering (farther planets orbit slower, on a wider circle) but are
compressed to fit the visible scene. Colors approximate each planet's
real-world appearance. eccentricity uses the real orbital eccentricity of
each planet (unscaled) — most are subtle, Mercury is the standout.
"""

PLANET_DEFAULTS = [
    # Closest to the star: smallest orbit, fastest speed, grey rocky surface.
    # Most eccentric orbit of the 8 real planets — the ellipse should read clearly.
    ("Mercury", 5.0, 1.5, 0.5, (0.6, 0.58, 0.55), 0.206),
    # Thick cloud cover gives it a pale cream/gold tone. Near-circular orbit.
    ("Venus",   7.0, 1.1, 0.8, (0.9, 0.85, 0.65), 0.007),
    # Reference "blue marble" appearance.
    ("Earth",   9.0, 0.8, 0.9, (0.2, 0.5, 1.0), 0.017),
    # Iron oxide surface gives its signature rust-red color.
    ("Mars",   13.0, 0.5, 0.7, (0.9, 0.3, 0.2), 0.093),
    # Gas giant: farther and slower, banded tan/orange atmosphere.
    ("Jupiter",17.0, 0.3, 0.7, (0.85, 0.65, 0.4), 0.048),
    # Gas giant with a paler gold atmosphere than Jupiter (rings not modeled).
    ("Saturn", 21.0, 0.22, 0.65, (0.9, 0.8, 0.5), 0.056),
    # Ice giant: pale cyan tint from methane in its atmosphere.
    ("Uranus", 25.0, 0.15, 0.55, (0.4, 0.8, 0.9), 0.047),
    # Ice giant: deepest blue, farthest and slowest orbit. Near-circular orbit.
    ("Neptune",29.0, 0.1, 0.55, (0.2, 0.3, 0.9), 0.009),
]
