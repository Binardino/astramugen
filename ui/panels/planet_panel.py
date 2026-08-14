"""Per-planet slider row for the planet dashboard panel."""

from ursina import Slider, Text, color, destroy
from simulation.bodies.planet import Planet


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