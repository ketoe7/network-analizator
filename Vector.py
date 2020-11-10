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

    def distance(self, line_point1, line_point2):
        AB = line_point2 - line_point1
        AC = self - line_point1
        area = (AB * AC).magnitude()
        distance = area / AB.magnitude()
        return distance

    def distance_from_point(self, other):
        return math.sqrt((other.x - self.x)**2 + (other.y - self.y)**2 + (other.z - self.z)**2)

    def __repr__(self):
        return f'({self.x:.5f}, {self.y:.5f}, {self.z:.5f})'

line_point1 = Vector(0, 0, 0)
line_point2 = Vector(1, 0, 0)
point = Vector(4, 2, 2)
print(point.distance(line_point1, line_point2))

