from panda3d.core import *
from direct.showbase.ShowBase import ShowBase

loadPrcFileData("", "load-file-type p3assimp")
from panda3d.core import LineSegs, Vec3, NodePath, TextureStage
from utils.orbit_math import get_orbit_position, clamp_angle
from math import radians, cos, sin


class CelestialBody:
    def __init__(
        self,
        name,
        parent_node,
        orbit_radius,
        orbit_speed,
        rotation_speed,
        radius,
        texture_path=None,
        debug_orbit=False,
    ):
        self.name           = name
        self.orbit_radius   = orbit_radius
        self.orbit_speed    = orbit_speed
        self.rotation_speed = rotation_speed
        self.radius         = radius
        self.texture_path   = texture_path

        self.orbit_angle    = 0.0
        self.rotation_angle = 0.0

        self.node  = parent_node.attachNewNode(self.name)

        # centre the sphere at the node origin
        self.model = loader.loadModel("assets/models/planet_sphere.OBJ")
        self.model.reparentTo(self.node)
        self.model.setScale(self.radius)

        # texture (unchanged)
        if self.texture_path:
            try:
                tex = loader.loadTexture(self.texture_path)
                tex.setMinfilter(tex.FT_linear_mipmap_linear)
                self.model.setTexture(tex, 1)
                # flip V so it isn’t upside‑down
                self.model.setTexScale(TextureStage.getDefault(), 1, -1)
            except Exception as e:
                print(f"[{self.name}] texture load failed: {e}")

        if debug_orbit and self.orbit_radius > 0:
            self._make_orbit_ring(parent_node)

        # start at correct position
        self.node.setPos(get_orbit_position(self.orbit_radius, self.orbit_angle))

    def _make_orbit_ring(self, parent_node, segments=128, colour=(1, 0, 0, 1)):
        segs = LineSegs()
        segs.setThickness(1.5)
        segs.setColor(*colour)

        for i in range(segments + 1):
            a = radians(i * 360 / segments)
            x = self.orbit_radius * cos(a)
            y = self.orbit_radius * sin(a)
            if i == 0:
                segs.moveTo(x, y, 0)
            else:
                segs.drawTo(x, y, 0)

        ring = segs.create()
        NodePath(ring).reparentTo(parent_node)

    # ------------------------------------------------------------------ #
    # per‑frame update
    # ------------------------------------------------------------------ #
    def update_task(self, task):
        dt = globalClock.getDt()

        # move along the orbit
        self.orbit_angle = clamp_angle(self.orbit_angle + self.orbit_speed * dt)
        self.node.setPos(get_orbit_position(self.orbit_radius, self.orbit_angle))

        # self‑rotation
        self.rotation_angle += self.rotation_speed * dt
        self.model.setH(self.rotation_angle)

        return task.cont
