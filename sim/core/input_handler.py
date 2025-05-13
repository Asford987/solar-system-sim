import math
import sys
from direct.gui.DirectGui import DirectButton
from panda3d.core import CollisionTraverser, CollisionNode, CollisionRay, CollisionHandlerQueue, BitMask32, Vec3


class InputHandler:
    def __init__(self, app, camera_controller):
        self.app = app
        self.camera_controller = camera_controller
        
        self.orbiting = False
        self.planet_np = None
        self.distance = 50.0
        self.orbit_heading = 0.0
        self.orbit_pitch = 20.0

        self.picker = CollisionTraverser()
        self.pq = CollisionHandlerQueue()
        self.picker_node = CollisionNode('mouseRay')
        self.picker_np = self.app.camera.attachNewNode(self.picker_node)
        self.picker_node.setIntoCollideMask(BitMask32.allOff())
        self.picker_ray = CollisionRay()
        self.picker_node.addSolid(self.picker_ray)
        self.picker.addCollider(self.picker_np, self.pq)
        
        app.accept("r", self.reset_camera)
        app.accept("v", self.toggle_speed)
        app.accept("p", self.freeze_time)
        app.accept("escape", self.pause)
        app.accept('mouse1', self.focus_on_planet)

        app.taskMgr.add(self.update_orbit_camera, "orbit_camera_task")

    def focus_on_planet(self):
        if not self.app.mouseWatcherNode.hasMouse():
            return

        self.picker_ray.setFromLens(self.app.camNode, 0, 0)

        self.picker.traverse(render)
        if self.pq.getNumEntries() > 0:
            self.pq.sortEntries()
            for entry in self.pq.getEntries():
                np = entry.getIntoNodePath()
                if np.hasTag("planet"):
                    self.planet_np = np
                    self.orbiting = True
                    self.camera_controller.set_mouse_enabled(True)
                    self.orbit_heading = 0.0
                    self.orbit_pitch = 20.0
                    return

    def update_orbit_camera(self, task):
        if self.orbiting and self.app.mouseWatcherNode.hasMouse():
            md = self.app.win.getPointer(0)
            dx = md.getX() - self.camera_controller.cx
            dy = md.getY() - self.camera_controller.cy
            self.camera_controller.center_mouse()

            self.orbit_heading -= dx * 0.2
            self.orbit_pitch = max(-85, min(85, self.orbit_pitch - dy * 0.2))

            heading_rad = math.radians(self.orbit_heading)
            pitch_rad = math.radians(self.orbit_pitch)

            x = self.distance * math.cos(pitch_rad) * math.sin(heading_rad)
            y = -self.distance * math.cos(pitch_rad) * math.cos(heading_rad)
            z = self.distance * math.sin(pitch_rad)

            camera_pos = Vec3(x, y, z)

            if self.planet_np:
                self.app.camera.setPos(self.planet_np.getPos() + camera_pos)
                self.app.camera.lookAt(self.planet_np)

        return task.cont
    
    def freeze_time(self):
        self.app._frozen_time = not self.app._frozen_time
    
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
