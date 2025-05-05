from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData, DirectionalLight, AmbientLight, TextureStage
import json
import os

from core.scene_manager import SceneManager
from core.camera_controller import CameraController
from core.input_handler import InputHandler

loadPrcFileData('', 'window-title Solar System Sandbox')
loadPrcFileData('', 'show-frame-rate-meter 1')

class SolarSystemApp(ShowBase):
    def __init__(self):
        super().__init__()
        self._mouse_enabled = False

        self.setBackgroundColor(0, 0, 0, 1)
        scene_data = self.load_scene_data("scene.json")

        self.scene_manager = SceneManager(self)
        self.scene_manager.build_scene(scene_data)
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
        
# Run the app
if __name__ == "__main__":
    app = SolarSystemApp()
    app.run()
