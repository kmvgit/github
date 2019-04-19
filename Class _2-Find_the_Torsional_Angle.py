import math

class Points(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __sub__(self, no):
        pass

    def dot(self, no):
        pass

    def cross(self, no):
        pass

    def absolute(self):
        return pow((self.x ** 2 + self.y ** 2 + self.z ** 2), 0.5)


if __name__ == '__main__':
    points = [[0.0, 4.0, 5.0], [1.0, 7.0, 6.0], [0.0, 5.0, 9.0], [1.0, 7.0,
                 2.0]]
    a, b, c, d = Points(*points[0]), Points(*points[1]), Points(
        *points[2]), Points(*points[3])
    print(b-a)


"""
    points = list()
    for i in range(4):
        a = list(map(float, input().split()))
        points.append(a)

    print(points)
"""


"""
    x = (b - a).cross(c - b)
    y = (c - b).cross(d - c)
    angle = math.acos(x.dot(y) / (x.absolute() * y.absolute()))

    print("%.2f" % math.degrees(angle))
"""