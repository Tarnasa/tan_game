"""
Partitions the world space into (w by h)-size buckets
Rectangles are placed into all buckets which they overlap
This allows quick collision detection, and nearest-neighbor searching

The partition of the first cell is (0, 0, w-1, h-1)

Example usage:

qt = Quadtree(64, 64)
a = Rect(0, 0, 10, 10)
qt.add(a)
qt.add(Rect(10, 0, 20, 10))

for other in qt.collide_rect(Rect(5, 5, 15, 15)):
    print(other)

qt.remove(a)

"""

from collections import defaultdict

from pygame import Rect


class Quadtree(object):
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.buckets = defaultdict(lambda: list())

    def add(self, gameobj):
        rect = gameobj.rect
        for y in range(rect.top / self.h, (rect.bottom-1) / self.h + 1):
            for x in range(rect.left / self.w, (rect.right-1) / self.w + 1):
                self.buckets[x, y].append(gameobj)

    def remove(self, gameobj):
        rect = gameobj.rect
        for y in range(rect.top / self.h, (rect.bottom-1) / self.h + 1):
            for x in range(rect.left / self.w, (rect.right-1) / self.w + 1):
                self.buckets[x, y].remove(gameobj)

    def collide_rect(self, rect):
        for y in range(rect.top / self.h, rect.bottom / self.h + 1):
            for x in range(rect.left / self.w, rect.right / self.w + 1):
                for obj in self.buckets[x, y]:
                    if rect.colliderect(obj.rect):
                        yield obj

    def collide_point(self, x, y):
        for obj in self.buckets[x / self.w, y / self.h]:
            if obj.rect.collidepoint(x, y):
                yield obj


# Unit tests
if __name__ == '__main__':
    class G(object):
        def __init__(self, rect):
            self.rect = rect
    qt = Quadtree(8, 8)
    qt.add(G(Rect(0, 0, 8, 8)))
    qt.add(G(Rect(14, 14, 15-14, 15-14)))
    assert(Rect(0, 0, 1, 1).left == 0)
    assert(Rect(0, 0, 1, 1).right == 1)
    assert(Rect(0, 0, 2, 2).colliderect(Rect(1, 1, 1, 1)))
    assert(0 == sum(1 for _ in qt.collide_rect(Rect(9, 9, 13-9, 13-9))))
    assert(1 == sum(1 for _ in qt.collide_rect(Rect(9, 9, 15-9, 15-9))))
    assert(1 == sum(1 for _ in qt.collide_rect(Rect(7, 7, 13-9, 15-9))))
    assert(2 == sum(1 for _ in qt.collide_rect(Rect(7, 7, 50-9, 50-9))))

