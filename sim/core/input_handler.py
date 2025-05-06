import sys
from direct.gui.DirectGui import DirectButton
from panda3d.core import WindowProperties


class InputHandler:
    def __init__(self, app, camera_controller):
        self.app = app
        self.camera_controller = camera_controller

        app.accept("r", self.reset_camera)
        app.accept("v", self.toggle_speed)
        app.accept("escape", self.pause)
        
    def pause(self):
        self.camera_controller.set_mouse_enabled(True)
        self.pause_buttons = []
        self.pause_buttons.append(
            DirectButton(text="Resume", scale=0.1, pos=(-0.2, 0, 0), command=self.resume, parent=self.app.aspect2d)
        )
        self.pause_buttons.append(
            DirectButton(text="Quit", scale=0.1, pos=(0.2, 0, 0), command=self.quit, parent=self.app.aspect2d)
        )

    def resume(self):
        for btn in self.pause_buttons:
            btn.destroy()
        self.pause_buttons = []
        self.camera_controller.set_mouse_enabled(False)
        
    def quit(self):
        self.app.user_exit = True
        self.app.destroy()
        sys.exit(0)
        
    def toggle_speed(self):
        if not hasattr(self, '_speed_levels'):
            self._speed_levels = [50, 100, 150, 200, 250, 300, 350]
            self._speed_index = 2
        self._speed_index = (self._speed_index + 1) % len(self._speed_levels)
        self.camera_controller.speed = self._speed_levels[self._speed_index]

    def reset_camera(self):
        self.camera_controller.center_mouse()
        self.app.camera.setPos(0, -30, 5)
        self.app.camera.lookAt(0, 0, 0)
