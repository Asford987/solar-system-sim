import math
import json
import os
import asyncio
import websockets
import threading

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    loadPrcFileData,
    DirectionalLight,
    AmbientLight,
    TextureStage,
    Texture,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    GeomTriangles,
    Geom,
    GeomNode,
    TransparencyAttrib,
    CullFaceAttrib
)

from core.scene_manager import SceneManager
from core.camera_controller import CameraController
from core.input_handler import InputHandler

# Configurações da janela
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

        self.setBackgroundColor(0, 0, 0, 1)
        self.scene_data = self.load_scene_data("scene.json")

        self.scene_manager = SceneManager(self)
        self.scene_manager.build_scene(self.scene_data)
        sun_light = DirectionalLight('sun')
        sun_np = self.render.attachNewNode(sun_light)
        sun_np.setHpr(45, -60, 0)
        self.render.setLight(sun_np)

        amb_light = AmbientLight('amb')
        amb_light.setColor((0.2, 0.2, 0.2, 1))
        self.render.setLight(self.render.attachNewNode(amb_light))

        self.camera_controller = CameraController(self)
        self.input_handler = InputHandler(self, self.camera_controller)

        self._build_starfield()
        self.input_handler.reset_camera()

        threading.Thread(target=self.start_websocket_server, daemon=True).start()

    def load_scene_data(self, filename):
        path = os.path.join(os.path.dirname(__file__), filename)
        with open(path, 'r') as f:
            return json.load(f)

    def _build_starfield(self):
        """Create an inside-out procedural skydome textured with stars."""
        # 1) gera e parenta o skydome
        dome_np = self.render.attach_new_node(_make_sky_sphere())
        dome_np.setLightOff()
        dome_np.setBin("background", 0)
        dome_np.setDepthWrite(False)
        dome_np.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullNone))

        # 2) carrega a textura seamless da galáxia
        stars = loader.loadTexture("../assets/textures/space.jpg")
        stars.setMinfilter(Texture.FTLinearMipmapLinear)
        stars.setWrapU(Texture.WMRepeat)
        stars.setWrapV(Texture.WMClamp)

        # 3) aplica no modo REPLACE
        ts = TextureStage("env")
        ts.setMode(TextureStage.MReplace)
        dome_np.setTexture(ts, stars)
        dome_np.setTexScale(ts, 1, 1)
        dome_np.setTexOffset(ts, 0.5, 0)
        
    async def websocket_handler(self, websocket, path):
        async for message in websocket:
            data = json.loads(message)
            if data["action"] == "add_moon":
                planet_name = data["planet"]
                self.add_moon_to_planet(planet_name)

    def add_moon_to_planet(self, planet_name):
        for obj in self.scene_data["children"]:
            if obj["name"] == planet_name:
                if "children" not in obj:
                    obj["children"] = []
                new_moon = {
                    "name": f"New Moon {len(obj['children']) + 1}",
                    "type": "moon",
                    "radius": 0.1,
                    "orbit_radius": 2.0,
                    "orbit_speed": 20.0,
                    "rotation_speed": 10.0,
                    "inclination": 0.5,
                    "texture": "assets/textures/moon.jpg"
                }
                obj["children"].append(new_moon)
                self.scene_manager.build_scene(self.scene_data)
                with open(os.path.join(os.path.dirname(__file__), "scene.json"), 'w') as f:
                    json.dump(self.scene_data, f, indent=2)
                
                break

    def start_websocket_server(self):
        """Start the WebSocket server in a separate thread with its own event loop."""
        async def run_server():
            async with websockets.serve(self.websocket_handler, "localhost", 8765):
                await asyncio.Future()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_server())


if __name__ == "__main__":
    app = SolarSystemApp()
    app.run()