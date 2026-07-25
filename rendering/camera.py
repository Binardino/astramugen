"""
CameraController — thin wrapper around Ursina's EditorCamera.

Sets a tilted initial angle and position so the solar system reads clearly
as a top-down system with its orbit grid, instead of EditorCamera's default
flat, edge-on start view.
"""

from ursina.prefabs.editor_camera import EditorCamera


class CameraController:
    """Wraps EditorCamera with a fixed initial tilt and position.

    Right-click drag: orbit. Scroll: zoom (EditorCamera defaults).
    """

    def __init__(self):
        self._camera = EditorCamera()
        self._camera.rotation_x = 50  # camera tilt, ~50° from horizontal view
        self._camera.position = (0, 15, -20)