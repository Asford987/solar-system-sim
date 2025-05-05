import math
from panda3d.core import *
from direct.showbase.ShowBase import ShowBase

loadPrcFileData("", "load-file-type p3assimp")
from panda3d.core import LineSegs, Vec3, NodePath, TextureStage
from math import radians, sin, cos
from utils.orbit_math import clamp_angle


class CelestialBody:
    def __init__(
        self,
        name,
        app,
        parent_node,
        orbit_radius,
        eccentricity, 
        orbit_speed,
        rotation_speed,
        radius,
        texture_path=None,
        inclination=0.0,
        debug_orbit=True,
    ):
        self.name           = name
        self.app            = app
        self.orbit_radius   = orbit_radius
        self.eccentricity   = eccentricity
        self._semi_minor    = orbit_radius * math.sqrt(max(0, 1 - eccentricity**2))
        self.orbit_speed    = orbit_speed
        self.rotation_speed = rotation_speed
        self.radius         = radius
        self.texture_path   = texture_path
        self.inclination    = inclination

        self.orbit_angle    = 0.0
        self.rotation_angle = 0.0

        self.node  = parent_node.attachNewNode(self.name)

        self.model = loader.loadModel("../assets/models/planet_sphere_with_uv.egg")
        self.model.reparentTo(self.node)
        self.model.setScale(self.radius)

        if self.texture_path:
            try:
                tex = loader.loadTexture(self.texture_path)
                tex.setMinfilter(tex.FT_linear_mipmap_linear)
                self.model.setTexture(tex, 1)
                self.model.setTexScale(TextureStage.getDefault(), 1, -1)
            except Exception as e:
                print(f"[{self.name}] texture load failed: {e}")

        if debug_orbit and self.orbit_radius > 0:
            self._make_orbit_ring(parent_node)

        self.node.setPos(self._inclined_pos(self.orbit_angle))

    def _inclined_pos(self, angle_deg):
        """Return position on orbit with inclination applied (rotate about X)."""
        t = math.radians(angle_deg)
        a = self.orbit_radius
        b = self._semi_minor 
        c = a * self.eccentricity    
        x = a * math.cos(t) - c
        y_flat = b * math.sin(t)
        inc = math.radians(self.inclination)
        y = y_flat * math.cos(inc)
        z = y_flat * math.sin(inc)
        return Vec3(x, y, z)

    def _make_orbit_ring(self, parent_node, segs=128, color=(0, 1, 0, 1)):
        ls = LineSegs()
        ls.setThickness(1.2)
        ls.setColor(*color)

        for i in range(segs + 1):
            p = self._inclined_pos(i * 360 / segs)
            if i == 0:
                ls.moveTo(p)
            else:
                ls.drawTo(p)

        NodePath(ls.create()).reparentTo(parent_node)

    def update_task(self, task):
        dt = globalClock.getDt()
        if not self.app._mouse_enabled:

            self.orbit_angle = clamp_angle(self.orbit_angle + self.orbit_speed * dt)
            self.node.setPos(self._inclined_pos(self.orbit_angle))

            self.rotation_angle += self.rotation_speed * dt
            self.model.setH(self.rotation_angle)

        return task.cont
