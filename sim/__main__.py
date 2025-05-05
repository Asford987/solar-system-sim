from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData, DirectionalLight, AmbientLight, TextureStage
import json
import os
import asyncio
import websockets
import threading

from core.scene_manager import SceneManager
from core.camera_controller import CameraController
from core.input_handler import InputHandler

loadPrcFileData('', 'window-title Solar System Sandbox')
loadPrcFileData('', 'show-frame-rate-meter 1')

class SolarSystemApp(ShowBase):
    def __init__(self):
        super().__init__()

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

        # Start WebSocket server in a separate thread
        threading.Thread(target=self.start_websocket_server, daemon=True).start()

    def load_scene_data(self, filename):
        path = os.path.join(os.path.dirname(__file__), filename)
        with open(path, 'r') as f:
            return json.load(f)

    def _build_starfield(self):
        """Create an inside‑out sphere textured with stars."""
        sky = loader.loadModel("../assets/models/planet_sphere_with_uv.egg")
        sky.reparentTo(self.render)
        sky.setScale(1500)
        sky.setTwoSided(True)
        sky.setLightOff()
        sky.setBin("background", 0)
        sky.setDepthWrite(False)
        sky.setCompass()

        stars = loader.loadTexture("../assets/textures/space.jpg")
        stars.setMinfilter(stars.FTLinearMipmapLinear)
        sky.setTexture(stars, 1)
        sky.setTexScale(TextureStage.getDefault(), 1, -1)

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
                self.scene_manager.build_scene(self.scene_data)  # Rebuild the scene
                with open(os.path.join(os.path.dirname(__file__), "scene.json"), 'w') as f:
                    json.dump(self.scene_data, f, indent=2)
                
                break

    def start_websocket_server(self):
        """Start the WebSocket server in a separate thread with its own event loop."""
        async def run_server():
            async with websockets.serve(self.websocket_handler, "localhost", 8765):
                await asyncio.Future()  # Run forever

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_server())  # Await inside the loop

# Run the app
if __name__ == "__main__":
    app = SolarSystemApp()
    app.run()