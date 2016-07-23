from collections import defaultdict

from gameobject import GameObject, Static
from loader import images
from physics import V
from spider import Spider


def load_world(filename):
    """Returns a list of created objects represented by the world file"""
    with open(filename, 'rb') as f:
        start_pos = V(0, 0)
        objs = list()
        floors = {
            '.': 'grass1',
            ',': 'grass2',
            '"': 'red_brick_floor',
        }
        walls = {
            '#': 'bush',
            'R': 'red_tiles',
        }
        char_grid = defaultdict(lambda: ' ')
        for y, line in enumerate(f.readlines()):
            for x, char in enumerate(line.rstrip()):
                pos = V(x * 64, y * 64)
                char_grid[pos.tup()] = char
                if char in floors:
                    obj = Static(sprites=images[floors[char]], depth=-2)
                    obj.rect.topleft = pos.tup()
                    obj.pos = V(*obj.rect.center)
                    objs.append(obj)
                elif char in walls:
                    if char == 'R':
                        pass
                    else:
                        obj = Static(sprites=images[walls[char]], wall=True, depth=-1)
                        obj.rect.topleft = pos.tup()
                        obj.pos = V(*obj.rect.center)
                        objs.append(obj)
                elif char == 'P':
                    start_pos = pos + V(32, 32)
                    obj = Static(sprites=images[floors['.']], depth=-2)
                    obj.rect.topleft = pos.tup()
                    obj.pos = V(*obj.rect.center)
                    objs.append(obj)
                elif char == 's':
                    spider = Spider(pos=pos + V(32, 32), authority=True)
                    objs.append(spider)
                    obj = Static(sprites=images[floors['.']], depth=-2)
                    obj.rect.topleft = pos.tup()
                    obj.pos = V(*obj.rect.center)
                    objs.append(obj)

        for pos, char in char_grid.items():
            if char == 'R':
                pos = V(pos[0], pos[1])
                c = tuple([int(char_grid[tuple(pos + off)] == char) for off in
                           [V(64, 0), V(0, -64), V(-64, 0), V(0, 64)]])
                simple_map = {
                    (0, 1, 1, 1): 4,
                    (1, 0, 1, 1): 3,
                    (1, 1, 0, 1): 2,
                    (1, 1, 1, 0): 5,

                    (0, 0, 1, 1): 6,
                    (1, 0, 0, 1): 7,
                    (1, 1, 0, 0): 8,
                    (0, 1, 1, 0): 9,
                }
                index = 1
                if c in simple_map:
                    index = simple_map[c]
                else:
                    if c == (1, 1, 1, 1):
                        if char_grid[tuple(pos + V(64, -64))] != char:
                            index = 10
                        elif char_grid[tuple(pos + V(-64, -64))] != char:
                            index = 11
                        elif char_grid[tuple(pos + V(-64, 64))] != char:
                            index = 13
                        elif char_grid[tuple(pos + V(64, 64))] != char:
                            index = 12
                obj = Static(sprites=images[walls[char]][index], wall=True, depth=-1)
                obj.rect.topleft = pos.tup()
                obj.pos = V(*obj.rect.center)
                objs.append(obj)

    return objs, start_pos
