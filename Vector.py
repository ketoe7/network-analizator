# from Devices.Router import Router
import math


class Vector:
    """
        @classDescription:
        @author: Mikołaj Wierzbicki
    """

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        x1 = self.x + other.x
        y1 = self.y + other.y
        z1 = self.z + other.z
        return Vector(x1, y1, z1)

    def __sub__(self, other):
        x1 = self.x - other.x
        y1 = self.y - other.y
        z1 = self.z - other.z
        return Vector(x1, y1, z1)

    def __mul__(self, other):
        """cross product"""
        x1 = self.y * other.z - self.z * other.y
        y1 = self.z * other.x - self.x * other.z
        z1 = self.x * other.y - self.y * other.x
        return Vector(x1, y1, z1)

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def distance_from_line(self, line_point1, line_point2):
        AB = line_point2 - line_point1
        AC = self - line_point1
        area = (AB * AC).magnitude()
        distance = area / AB.magnitude()
        return distance

    def distance_from_point(self, other):
        return math.sqrt((other.x - self.x)**2 + (other.y - self.y)**2 + (other.z - self.z)**2)

    def can_cross_transmission_range(self, router: object):
        return (router.position.y - router.transmission_radius <= self.y <= router.position.y + router.transmission_radius) \
               and (router.position.z - router.transmission_radius <= self.z <= router.position.z + router.transmission_radius)

    def move_vector(self, time, velocity):
        return Vector(self.x + (time * velocity), self.y, self.z)

    def get_sphere_intersections(self, center, radius):
        a = 1
        b = 2*self.x - 2*center.x
        c = self.x**2 + self.y**2 + self.z**2 + center.x**2 + center.y**2 + center.z**2 - 2*self.x*center.x - 2*self.y*center.y - 2*self.z*center.z - radius**2

        d = b**2 - 4*a*c
        # print(d)
        sqrt_val = math.sqrt(abs(d))
        if d > 0:
            # print(" real and different roots ")
            t = [(-b - sqrt_val) / (2 * a), (-b + sqrt_val) / (2 * a)]
        elif d == 0:
            # print(" real and same roots")
            t = [-b / (2 * a)]
        else:
            t = []

        v = []
        for _ in t:
            v.append(Vector(self.x + _, self.y, self.z))
        return v

    def __repr__(self):
        return f'({self.x:.5f}, {self.y:.5f}, {self.z:.5f})'

# P = Vector(0, 0, 1)
# S = Vector(2, 0, 0)
# r = 1
# print(P.get_sphere_intersections(S, r))