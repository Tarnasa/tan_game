from math import hypot


class V(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def copy(self):
        return V(self.x, self.y)

    def __add__(self, other):
        return V(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __sub__(self, other):
        return V(self.x - other.x, self.y - other.y)

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self

    def __mul__(self, factor):
        return V(self.x * factor, self.y * factor)

    def __imul__(self, factor):
        self.x *= factor
        self.y *= factor
        return self

    def __div__(self, divisor):
        return V(self.x / divisor, self.y / divisor)

    def __idiv__(self, divisor):
        self.x /= divisor
        self.y /= divisor
        return self

    def __neg__(self):
        return V(-self.x, -self.y)

    def __iter__(self):
        yield self.x
        yield self.y

    def magnitude(self):
        return hypot(self.x, self.y)

    def r2(self):
        return self.x**2 + self.y**2

    def normalized(self):
        d = hypot(self.x, self.y)
        return V(self.x / d, self.y / d)

    def tup(self):
        return self.x, self.y

    def __getitem__(self, n):
        if n == 0: return self.x
        if n == 1: return self.y

    def x_part(self):
        return V(self.x, 0)

    def y_part(self):
        return V(0, self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return self.x != other.x or self.y != other.y

    def __repr__(self):
        return 'V({0}, {1})'.format(self.x, self.y)


if __name__ == '__main__':
    assert(V(0, 0) == V(0, 0))
    assert((V(0, 0) != V(0, 0)) == False)
    assert(V(1, 0) != V(0, 0))
