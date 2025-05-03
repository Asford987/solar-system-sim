from panda3d.core import Vec3, WindowProperties, TextNode
from direct.gui.OnscreenText import OnscreenText
from direct.task import Task


class CameraController:
    def __init__(self, app):
        self.app = app
        self.win = app.win
        self.camera = app.camera

        app.disableMouse()

        self.speed = 25.0
        self.mouse_sensitivity = 0.15
        self.heading = 0.0
        self.pitch = 0.0

        self.keys = {
            "w": False, "s": False, "a": False, "d": False,
            "q": False, "e": False,
            "space": False, "shift": False,
        }
        
        for k in self.keys:
            app.accept(k, self.set_key, [k, True])
            app.accept(f"{k}-up", self.set_key, [k, False])

        props = WindowProperties()
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.M_confined)
        self.win.requestProperties(props)
        self.center_mouse()

        self.coord_text = OnscreenText(
            text="Pos:",
            pos=(-1.29, -0.95),
            scale=0.05,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            mayChange=True,
        )

        app.taskMgr.add(self.update_camera, "free_fly_camera")

    def center_mouse(self):
        sx, sy = self.win.getProperties().getXSize(), self.win.getProperties().getYSize()
        self.cx, self.cy = sx // 2, sy // 2
        self.win.movePointer(0, self.cx, self.cy)

    def set_key(self, key, value):
        self.keys[key] = value

    def update_camera(self, task):
        dt = globalClock.getDt()

        if self.app.mouseWatcherNode.hasMouse():
            md = self.win.getPointer(0)
            dx = md.getX() - self.cx
            dy = md.getY() - self.cy

            self.heading -= dx * self.mouse_sensitivity
            self.pitch = max(-90, min(90, self.pitch - dy * self.mouse_sensitivity))
            self.camera.setHpr(self.heading, self.pitch, 0)

            self.center_mouse()

        direction = Vec3()
        quat = self.camera.getQuat()

        if self.keys["w"]: direction += quat.getForward()
        if self.keys["s"]: direction -= quat.getForward()
        if self.keys["a"]: direction -= quat.getRight()
        if self.keys["d"]: direction += quat.getRight()
        if self.keys["q"]: direction -= quat.getUp()
        if self.keys["e"]: direction += quat.getUp()

        if direction.length_squared() > 0:
            direction.normalize()
            self.camera.setPos(self.camera.getPos() + direction * self.speed * dt)

        if self.keys["shift"]:
            self.camera.setZ(self.camera, -self.speed * dt)
        if self.keys["space"]:
            self.camera.setZ(self.camera,  self.speed * dt)

        pos = self.camera.getPos()
        self.coord_text.setText(f"Pos: X={pos.x:.1f}, Y={pos.y:.1f}, Z={pos.z:.1f}")

        return Task.cont
