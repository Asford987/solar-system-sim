import math
import json
import os

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    loadPrcFileData,
    AmbientLight,
    TextureStage,
    Texture,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    GeomTriangles,
    Geom,
    GeomNode,
    CullFaceAttrib
)

from core.scene_manager import SceneManager
from core.camera_controller import CameraController
from core.input_handler import InputHandler

loadPrcFileData('', 'window-title Solar System Sandbox')
loadPrcFileData('', 'show-frame-rate-meter 1')


def _make_sky_sphere(radius=1500, lat_steps=16, long_steps=32):
    """Gera uma esfera interna (skydome) com UVs de 0→1."""
    fmt    = GeomVertexFormat.get_v3t2()
    vdata  = GeomVertexData('sky', fmt, Geom.UHStatic)
    vwriter = GeomVertexWriter(vdata, 'vertex')
    uvwriter= GeomVertexWriter(vdata, 'texcoord')
    for i in range(lat_steps + 1):
        phi = math.pi * i / lat_steps
        v   = 1 - i / lat_steps
        for j in range(long_steps + 1):
            theta = 2 * math.pi * j / long_steps
            u     = j / long_steps
            x = radius * math.sin(phi) * math.cos(theta)
            y = radius * math.sin(phi) * math.sin(theta)
            z = radius * math.cos(phi)
            vwriter.add_data3(x, y, z)
            uvwriter.add_data2(u, v)

    tris = GeomTriangles(Geom.UHStatic)
    stride = long_steps + 1
    for i in range(lat_steps):
        for j in range(long_steps):
            v0 =  i    * stride + j
            v1 =  i    * stride + (j+1)
            v2 = (i+1) * stride + j
            v3 = (i+1) * stride + (j+1)
            tris.add_vertices(v0, v2, v1)
            tris.add_vertices(v1, v2, v3)

    geom = Geom(vdata)
    geom.add_primitive(tris)
    node = GeomNode('skydome')
    node.add_geom(geom)
    return node


class SolarSystemApp(ShowBase):
    def __init__(self):
        super().__init__()
        self._mouse_enabled = False
        self._frozen_time = False
        self._speed_factor = 0.5

        self.setBackgroundColor(0, 0, 0, 1)
        self.scene_data = self.load_scene_data("scene.json")

        self.scene_manager = SceneManager(self)
        self.scene_manager.build_scene(self.scene_data)
        
        self.alight = AmbientLight('alight')
        self.alight.setColor((0.02, 0.02, 0.02, 1))
        self.alnp = self.render.attachNewNode(self.alight)
        self.render.setLight(self.alnp)
        
        self.camera_controller = CameraController(self)
        self.input_handler = InputHandler(self, self.camera_controller)

        self._build_starfield()
        self.input_handler.reset_camera()
        self.taskMgr.add(self.watch_json_file, 'watch_json_updates')
        self.last_mtime = None

    def load_scene_data(self, filename):
        path = os.path.join(os.path.dirname(__file__), filename)
        with open(path, 'r') as f:
            return json.load(f)

    def _build_starfield(self):
        """Create an inside-out procedural skydome textured with stars."""
        dome_np = self.render.attach_new_node(_make_sky_sphere())
        dome_np.setLightOff()
        dome_np.setBin("background", 0)
        dome_np.setDepthWrite(False)
        dome_np.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullNone))

        stars = loader.loadTexture("../assets/textures/space.jpg")
        stars.setMinfilter(Texture.FTLinearMipmapLinear)
        stars.setWrapU(Texture.WMRepeat)
        stars.setWrapV(Texture.WMClamp)

        ts = TextureStage("env")
        ts.setMode(TextureStage.MReplace)
        dome_np.setTexture(ts, stars)
        dome_np.setTexScale(ts, 1, 1)
        dome_np.setTexOffset(ts, 0.5, 0)
        
    def watch_json_file(self, task):
        try:
            current_mtime = os.path.getmtime("sim/scene.json")
            if self.last_mtime is None:
                self.last_mtime = current_mtime
                return
            if self.last_mtime is None or current_mtime != self.last_mtime:
                print("Change found")
                self.last_mtime = current_mtime
                self.render.get_children().detach()
                self._build_starfield()
                self.scene_data = self.load_scene_data("scene.json")
                self.scene_manager.build_scene(self.scene_data)
        except Exception as e:
            print(f"Error reading file: {e}")
        return task.cont

if __name__ == "__main__":
    app = SolarSystemApp()
    app.run()