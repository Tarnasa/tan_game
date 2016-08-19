from math import atan2, degrees

from physics import V


def sign(x):  # Because copysign is stupid
    return int(x > 0) - int(x < 0)


def angle90(x, y):
    """
    Returns an angle between 0 and 45
    0 when the delta is perfectly aligned with the x/y grid
    45 when the delta is at 45 degree angle with the x/y grid
    """
    angle = degrees(atan2(y, x))
    angle %= 90.0
    if angle > 45.0:
        angle = 90.0 - angle
    return angle


def align(x, y):
    if x == 0.0:
        return 0.0, y
    r = y / x
    if abs(r) > 1.0:
        return 0.0, y
    else:
        return x, 0.0


def direction(x, y):
    if y == 0.0:
        if x > 0:
            return 0
        else:
            return 2
    else:
        if y > 0:
            return 3
        else:
            return 1


def from_direction(d):
    return deltas[d]

def v_from_direction(d):
    return vdeltas[d]


deltas = [(1, 0), (0, -1), (-1, 0), (0, 1)]
vdeltas = [V(*d) for d in deltas]


