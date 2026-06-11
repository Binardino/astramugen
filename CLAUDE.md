# Astramugen — Project Rules

## What this project is

3D solar system simulator in Python using Ursina Engine. Art direction: low-poly Outer Wilds (warm, faceted) + wireframe/grid overlay. The user codes themselves — Claude assists and guides, never writes code autonomously.

## Hard rules

- **All files, commits, docstrings, comments, specs must be 100% English.** No French in any project file.
- **Never add Co-Authored-By or any AI attribution** to commit messages.
- **User codes themselves.** Guide and unblock — do not implement features unprompted.

## Architecture (non-negotiable)

Three strictly separated layers:

```
simulation/   ← pure Python, zero Ursina, testable with pytest
rendering/    ← everything that touches Ursina
ui/           ← Ursina dashboard
core/         ← abstract base classes shared between layers
```

**`simulation/` never imports Ursina. `rendering/` never computes orbits.**

Each feature = one focused file. No spaghetti, no cross-layer imports.

## Key docs

- Design spec: `docs/superpowers/specs/2026-06-11-astramugen-design.md`
- V1 implementation plan: `docs/superpowers/plans/2026-06-11-v1-implementation.md`

## V1 scope

Star + 1–5 configurable planets, circular Keplerian orbits, wireframe orbit lines + background grid, per-planet dashboard (size/color/radius/speed), global time speed slider, mouse camera.

## Version roadmap

| Version | Content |
|---------|---------|
| V1 | Star + planets + Keplerian orbits + dashboard |
| V2 | Moons, atmospheres, procedural generation |
| V3 | Asteroids, comets |
| V4 | Supernova, collisions |
| V5 | Newtonian physics, binary star |
| V6 | Black hole mode |
| V7 | Export, save/load |
