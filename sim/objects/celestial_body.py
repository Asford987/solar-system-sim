import math
from panda3d.core import (
    Vec3, LineSegs, NodePath, TextureStage, TransparencyAttrib,
    GeomVertexData, GeomVertexFormat, GeomVertexWriter,
    GeomTriangles, Geom, GeomNode, Texture, BitMask32, CollisionNode, CollisionSphere
)

from panda3d.core import ClockObject
globalClock = ClockObject.getGlobalClock()

from utils.orbit_math import clamp_angle

def _make_sphere_geom(radius=1.0, lat_steps=16, long_steps=32):
    fmt     = GeomVertexFormat.get_v3n3t2()
    vdata   = GeomVertexData('sphere', fmt, Geom.UHStatic)
    vwriter = GeomVertexWriter(vdata, 'vertex')
    nwriter = GeomVertexWriter(vdata, 'normal')
    uvwriter= GeomVertexWriter(vdata, 'texcoord')

    for i in range(lat_steps+1):
        phi = math.pi * i / lat_steps
        v   = i / lat_steps
        for j in range(long_steps+1):
            theta = 2*math.pi * j / long_steps
            u     = j / long_steps
            x = radius*math.sin(phi)*math.cos(theta)
            y = radius*math.sin(phi)*math.sin(theta)
            z = radius*math.cos(phi)
            vwriter.add_data3(x, y, z)
            nwriter.add_data3(x/radius, y/radius, z/radius)
            uvwriter.add_data2(u, 1-v)

    tris = GeomTriangles(Geom.UHStatic)
    stride = long_steps+1
    for i in range(lat_steps):
        for j in range(long_steps):
            v0 =  i   * stride + j
            v1 =  i   * stride + j+1
            v2 = (i+1)* stride + j
            v3 = (i+1)* stride + j+1
            tris.add_vertices(v0, v2, v1)
            tris.add_vertices(v1, v2, v3)

    geom = Geom(vdata)
    geom.add_primitive(tris)
    node = GeomNode('sphere')
    node.add_geom(geom)
    return node

def _make_ring_vertex_data(inner_radius, outer_radius, segments=64):
    fmt    = GeomVertexFormat.get_v3t2()
    vdata  = GeomVertexData('ring', fmt, Geom.UHStatic)
    vwriter = GeomVertexWriter(vdata, 'vertex')
    twriter = GeomVertexWriter(vdata, 'texcoord')

    for i in range(segments + 1):
        t = 2 * math.pi * i / segments
        x_out, y_out = outer_radius * math.cos(t), outer_radius * math.sin(t)
        vwriter.add_data3(x_out, y_out, 0)
        twriter.add_data2((math.cos(t)*0.5 + 0.5), (math.sin(t)*0.5 + 0.5))
        x_in, y_in = inner_radius * math.cos(t), inner_radius * math.sin(t)
        vwriter.add_data3(x_in, y_in, 0)
        twriter.add_data2(
            (math.cos(t)*(inner_radius/outer_radius)*0.5 + 0.5),
            (math.sin(t)*(inner_radius/outer_radius)*0.5 + 0.5)
        )
    return vdata

def _make_ring_primitive(segments=64):
    tris = GeomTriangles(Geom.UHStatic)
    for i in range(segments):
        idx = 2 * i
        tris.add_vertices(idx,   idx+1, idx+2)
        tris.add_vertices(idx+2, idx+1, idx+3)
    return tris


class CelestialBody:
    
    planet_counter = 0

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
        rings=None,
        overlay=None,
    ):
        self.overlay_rotation_angle = 0.0
        self.overlay_rotation_speed = overlay.get("speed", 0.0) if overlay else 0.0
        
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

        sphere_node = _make_sphere_geom(1.0, 16, 32)
        self.model = self.node.attachNewNode(sphere_node)
        self.model.setScale(self.radius)
        self.overlay_np    = None
        self.overlay_angle = 0.0
        self.overlay_speed = 0.0
        self.planet_counter += 1
        
        collider_node = CollisionNode(f"{name}_collider")
        collider_node.setIntoCollideMask(BitMask32.bit(1))
        collider_node.addSolid(CollisionSphere(0, 0, 0, self.radius))
        self.model.setTag("planet", "true")
        self.model.setTag("planet_id", str(self.planet_counter))

        if self.name.lower() == 'sun':
            self.model.setLightOff()
            from panda3d.core import Material, Vec4
            mat = Material()
            mat.setEmission(Vec4(1, 1, 1, 1))
            mat.setAmbient(Vec4(0, 0, 0, 1))
            self.model.setMaterial(mat, 1)

        if self.texture_path:
            tex = loader.loadTexture(self.texture_path)
            tex.setMinfilter(tex.FT_linear_mipmap_linear)
            tex.setWrapU(tex.WMRepeat)
            tex.setWrapV(tex.WMClamp)
            ts = TextureStage.getDefault()
            ts.setMode(TextureStage.MModulate)
            self.model.setTexture(ts, tex)
            self.model.setTexScale(ts, 1, 1)
            self.model.setTransparency(TransparencyAttrib.M_alpha)

        if debug_orbit and self.orbit_radius > 0:
            self._make_orbit_ring(parent_node)

        self.node.setPos(self._inclined_pos(self.orbit_angle))

        self.ring_np = None
        if rings:
            inner  = rings["inner_radius"]
            outer  = rings["outer_radius"]
            tex    = rings["texture"]
            speed  = rings.get("rotation_speed", self.rotation_speed)
            vdata = _make_ring_vertex_data(inner, outer)
            prim  = _make_ring_primitive()
            geom  = Geom(vdata)
            geom.add_primitive(prim)
            node  = GeomNode('saturn_ring')
            node.add_geom(geom)
            ring_np = self.node.attach_new_node(node)
            ring_np.setZ(self.radius * 0.01)
            ring_np.setTwoSided(True)
            ring_np.setBin('transparent', 10)
            ring_np.setDepthWrite(False) 
            ts = TextureStage('ts')
            ring_np.setTexture(ts, loader.loadTexture(tex))
            ring_np.setTransparency(TransparencyAttrib.M_alpha)
            ring_np.setPythonTag('ring_speed', speed)
            self.ring_np = ring_np

        if overlay and overlay.get("texture"):
            overlay_node = _make_sphere_geom(1.0, 16, 32)
            ov_np = self.node.attachNewNode(overlay_node)
            ov_np.setScale(self.radius * 1.01)
            ov_np.setLightOff()  
            ov_np.setTransparency(TransparencyAttrib.M_alpha)
            ov_tex = loader.loadTexture(overlay["texture"])
            ov_tex.setFormat(Texture.FRgba)   
            ov_tex.setMinfilter(ov_tex.FT_linear_mipmap_linear)
            ov_tex.setWrapU(ov_tex.WMRepeat)
            ov_tex.setWrapV(ov_tex.WMClamp)
            ts2 = TextureStage("overlay")
            ts2.setMode(TextureStage.MModulate) 
            ov_np.setTexture(ts2, ov_tex)

            ov_np.setTransparency(TransparencyAttrib.MAlpha)
            ov_np.setBin("transparent", 20)
            ov_np.setDepthWrite(False)
            ov_np.setDepthTest(True)
            ov_np.setTwoSided(True)
            self.overlay_np    = ov_np
            self.overlay_speed = overlay.get("speed", 0.0)

        if not hasattr(app, 'sun_light_np'):
            from panda3d.core import PointLight, AmbientLight, Vec4
            sun_pl = PointLight('sun')
            sun_pl.setColor(Vec4(1, 1, 0.9, 1))
            sun_np = app.render.attachNewNode(sun_pl)
            sun_np.setPos(0, 0, 0)
            sun_pl.setAttenuation((1, 0, 0.0001))
            amb = AmbientLight('ambient')
            amb.setColor(Vec4(0.01, 0.01, 0.01, 1))
            amb_np = app.render.attachNewNode(amb)
            app.render.setLight(sun_np)
            app.render.setLight(amb_np)
            app.sun_light_np = sun_np
            app.ambient_light_np = amb_np

        if self.name.lower() != 'sun':
            self.model.setShaderAuto()
            self.model.setLight(app.sun_light_np)
            self.model.setLight(app.ambient_light_np)
    
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
        dt = globalClock.getDt() * self.app._speed_factor
        if not self.app._frozen_time:

            self.orbit_angle = clamp_angle(self.orbit_angle + self.orbit_speed * dt)
            self.node.setPos(self._inclined_pos(self.orbit_angle))

            self.rotation_angle += self.rotation_speed * dt

            if self.overlay_np:
                self.overlay_rotation_angle += self.overlay_rotation_speed * dt
                self.overlay_np.setHpr(self.overlay_rotation_angle, -90, 0)

        return task.cont
