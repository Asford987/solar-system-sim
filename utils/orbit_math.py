from math import sin, cos, radians
from panda3d.core import Vec3

def get_orbit_position(orbit_radius, orbit_angle_degrees, center=Vec3(0, 0, 0)):
    """
    Returns the position of an object orbiting on a flat XY plane.
    """
    angle_rad = radians(orbit_angle_degrees)
    x = center.getX() + orbit_radius * cos(angle_rad)
    y = center.getY() + orbit_radius * sin(angle_rad)
    return Vec3(x, y, center.getZ())

def clamp_angle(angle):
    """
    Keeps angles within [0, 360).
    """
    return angle % 360

def degrees_to_radians(deg):
    return radians(deg)
