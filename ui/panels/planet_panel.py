"""Per-planet slider row for the planet dashboard panel."""

from ursina import Slider, Text, color, destroy
from simulation.bodies.planet import Planet
from ui.panels.planet_defaults import PLANET_DEFAULTS
from simulation.physics.kepler import KeplerOrbit
class _PlanetRow:
    """One row of sliders controlling a single planet's orbit and size.

    Attributes:
        planet: The Planet instance this row controls.
    """

    def __init__(self, planet: Planet, index: int):
        """Create the radius, speed and size sliders for a planet.

        Args:
            planet: The Planet instance to bind sliders to.
            index: 0-based row position, used to vertically offset this
                row so multiple planet rows don't overlap on screen.
        """
        self.planet = planet

        # Stack rows vertically by index so each planet gets its own space.
        y = -0.25 - index * 0.18

        self._radius_slider = Slider(
            min=2.0, max=25.0,
            default=planet.orbit.semi_major_axis,
            step=0.5,
            text='radius',
            position=(-0.6, y),
        )
        self._speed_slider = Slider(
            min=0.1, max=4.0,
            default=planet.orbit.speed,
            step=0.1,
            text='speed',
            position=(-0.6, y - 0.06),
        )
        self._size_slider = Slider(
            min=0.2, max=3.0,
            default=planet.radius,
            step=0.1,
            text='size',
            position=(-0.6, y - 0.12),
        )

        # Ursina calls these after the user releases a slider drag.
        self._radius_slider.on_value_changed = self._apply
        self._speed_slider.on_value_changed = self._apply
        self._size_slider.on_value_changed = self._apply

    def _apply(self) -> None:
        """Write current slider values back onto the bound planet.

        Called automatically when any of this row's three sliders
        finishes a drag (see the `on_value_changed` wiring in `__init__`).
        """
        self.planet.radius                = self._size_slider.value
        self.planet.orbit.speed           = self._speed_slider.value
        self.planet.orbit.semi_major_axis = self._radius_slider.value

    def destroy(self) -> None:
        """Destroy this row's slider widgets, removing them from the UI."""
        destroy(self._radius_slider)
        destroy(self._speed_slider)
        destroy(self._size_slider)

class PlanetPanel:
    """Dashboard panel managing the planet count slider and per-planet rows.

    `_planets` and `_rows` are kept in sync by index: `_planets[i]` is
    the planet controlled by `_rows[i]`.
    """

    def __init__(self, scene, planet_range):
        """Create the count slider and populate the initial planets.

        Args:
            scene: The Scene to add/remove planet bodies through.
            planet_range: Initial number of planets to create
                (must be between 1 and len(PLANET_DEFAULTS)).
        """
        self.scene = scene
        self._planets = []
        self._rows = []

        self._count_slider = Slider(
            min=1, max=len(PLANET_DEFAULTS), default=planet_range, step=1,
            text='planet count',
            position=(-0.6, 0.35),
        )
        self._count_slider.on_value_changed = self._on_count_changed

        for _ in range(planet_range):
            self._add_planet()

    def _add_planet(self):
        """Create and register the next planet from PLANET_DEFAULTS.

        Adds the planet to the scene (which creates its renderer and
        orbit line) and creates a matching _PlanetRow for dashboard control.
        """
        index = len(self._planets)
        name, orbital_radius, speed, size, planet_color, eccentricity = PLANET_DEFAULTS[index]
        orbit  = KeplerOrbit(semi_major_axis=orbital_radius, eccentricity=eccentricity, speed=speed)
        planet = Planet(name=name, radius=size, color=planet_color, orbit=orbit)
        self.scene.add_body(planet)
        self._planets.append(planet)
        self._rows.append(_PlanetRow(planet, index))

    def _remove_last(self):
        """Remove the last planet and destroy its dashboard row.

        Mirrors `_add_planet`: pops the last entries off `_rows` and
        `_planets` (kept in sync by index) and tears each of them down.
        """
        # list.pop() removes and returns the last element in one step,
        # so we hold the row/planet to destroy instead of losing it.
        row = self._rows.pop()
        row.destroy()
        planet = self._planets.pop()
        self.scene.remove_body(planet)

    def _on_count_changed(self):
        """Add or remove planets to match the count slider's new value.

        Called automatically when the count slider finishes a drag (see
        the `on_value_changed` wiring in `__init__`).
        """
        slider_value = int(self._count_slider.value)
        # Only one of these two loops actually runs per call, depending
        # on whether the slider moved up or down.
        while len(self._planets) < slider_value :
            self._add_planet()

        while len(self._planets) > slider_value :
            self._remove_last()