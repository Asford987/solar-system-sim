import sys


class InputHandler:
    def __init__(self, app, camera_controller):
        self.app = app
        self.camera_controller = camera_controller

        app.accept("r", self.reset_camera)
        app.accept("escape", self.quit)
        app.accept("v", self.toggle_speed)
        
    def quit(self):
        self.app.user_exit = True
        self.app.destroy()
        sys.exit(0)
        
    def toggle_speed(self):
        if not hasattr(self, '_speed_levels'):
            self._speed_levels = [100, 200, 250, 300, 350]
            self._speed_index = 2  # start with 250 as the middle value
        self._speed_index = (self._speed_index + 1) % len(self._speed_levels)
        self.app.speed = self._speed_levels[self._speed_index]
        print(f"Speed set to: {self.app.speed}")

    def reset_camera(self):
        self.app.camera.setPos(0, -30, 5)
        self.app.camera.setHpr(0, 0, 0)
