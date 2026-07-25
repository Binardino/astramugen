"""
TimePanel — displays a global time-speed slider in the dashboard.

Read by main.py each frame to scale simulation dt, letting the user
speed up, slow down, or pause all orbital motion.
"""

from ursina import Slider, Text, color


class TimePanel:
    """Shows a 'Time Speed' label and slider controlling global simulation speed."""

    def __init__(self):
        self._text = Text(text='Time Speed', position=(-0.7, 0.46), scale=1.2, color=color.white)
        self._slider = Slider(min=0.0, max=5.0, default=1.0, step=0.1, position=(-0.7, 0.40))

    @property
    def time_scale(self) -> float:
        """Current slider value — multiplier applied to dt before ticking the SolarSystem."""
        return self._slider.value