import math
from panda3d.core import Geom, GeomNode, GeomTriangles, GeomVertexData
from panda3d.core import GeomVertexFormat, GeomVertexWriter, Vec3, Vec2

def make_uv_sphere(name="uvSphere", rings=32, segments=32):
    fmt = GeomVertexFormat.getV3n3t2()        # pos, normal, uv
    vdata = GeomVertexData(name, fmt, Geom.UHStatic)
    vwriter = GeomVertexWriter(vdata, "vertex")
    nwriter = GeomVertexWriter(vdata, "normal")
    uvwriter = GeomVertexWriter(vdata, "texcoord")

    # vertices
    for r in range(rings + 1):
        phi = math.pi * r / rings            # 0..π
        for s in range(segments + 1):
            theta = 2 * math.pi * s / segments   # 0..2π
            x = math.sin(phi) * math.cos(theta)
            y = math.sin(phi) * math.sin(theta)
            z = math.cos(phi)
            vwriter.addData3f(x, y, z)
            nwriter.addData3f(x, y, z)
            uvwriter.addData2f(s / segments, 1 - r / rings)

    # triangles
    tris = GeomTriangles(Geom.UHStatic)
    for r in range(rings):
        for s in range(segments):
            i0 = r       * (segments + 1) + s
            i1 = (r + 1) * (segments + 1) + s
            i2 = i0 + 1
            i3 = i1 + 1
            tris.addVertices(i0, i1, i2)
            tris.addVertices(i2, i1, i3)

    geom = Geom(vdata)
    geom.addPrimitive(tris)
    node = GeomNode(name)
    node.addGeom(geom)
    return node
