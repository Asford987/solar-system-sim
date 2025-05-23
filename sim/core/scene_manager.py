from objects.celestial_body import CelestialBody
from panda3d.core import PointLight


class SceneManager:
    def __init__(self, app):
        self.app = app
        self.root_node = app.render

    def build_scene(self, scene_data):
        """
        Entry point: Builds the entire scene graph recursively from root node.
        """
        for light_np in self.root_node.getChildren():
            if light_np.node().isOfType(PointLight.getClassType()):
                 self.root_node.clearLight(light_np)
                 
        self._build_recursive(scene_data, self.root_node)

    def _build_recursive(self, body_data, parent_node):
        """
        Recursive scene graph builder.
        Creates a CelestialBody and attaches children if they exist.
        """
        name = body_data.get("name", "Unnamed")
        radius = body_data.get("radius", 1.0)
        orbit_radius = body_data.get("orbit_radius", 0.0)
        eccentricity  = body_data.get("eccentricity", 0.0)
        orbit_speed = body_data.get("orbit_speed", 0.0)
        rotation_speed = body_data.get("rotation_speed", 0.0)
        texture_path='../' + body_data.get("texture", None)
        inclination = body_data.get("inclination", 0.0)
        rings_data = body_data.get("rings", None)
        overlay = body_data.get("overlay", None)

        body = CelestialBody(
            name=name,
            app=self.app,
            parent_node=parent_node,
            orbit_radius=orbit_radius,
            eccentricity=eccentricity,
            orbit_speed=orbit_speed,
            rotation_speed=rotation_speed,
            radius=radius,
            texture_path=texture_path,
            inclination=inclination,
            rings=rings_data,
            overlay=overlay,
        )

        self.app.taskMgr.add(body.update_task, f"update-{name}")

        if "children" in body_data: 
            for child_data in body_data.get("children", []):
                self._build_recursive(child_data, body.node)
