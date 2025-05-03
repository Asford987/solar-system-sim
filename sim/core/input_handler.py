class InputHandler:
    def __init__(self, app, camera_controller):
        self.app = app
        self.camera_controller = camera_controller

        app.accept("r", self.reset_camera)

    def reset_camera(self):
        self.app.camera.setPos(0, -30, 5)
        self.app.camera.setHpr(0, 0, 0)
