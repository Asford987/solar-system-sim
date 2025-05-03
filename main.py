from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData, DirectionalLight, AmbientLight
import json
import os

from core.scene_manager import SceneManager
from core.camera_controller import CameraController
from core.input_handler import InputHandler

# Optional: Configure Panda3D window
loadPrcFileData('', 'window-title Solar System Sandbox')
loadPrcFileData('', 'show-frame-rate-meter 1')

class SolarSystemApp(ShowBase):
    def __init__(self):
        super().__init__()

        # Load scene.json
        scene_data = self.load_scene_data("scene.json")

        # Initialize core components
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

    def load_scene_data(self, filename):
        path = os.path.join(os.path.dirname(__file__), filename)
        with open(path, 'r') as f:
            return json.load(f)

# Run the app
if __name__ == "__main__":
    app = SolarSystemApp()
    app.run()
