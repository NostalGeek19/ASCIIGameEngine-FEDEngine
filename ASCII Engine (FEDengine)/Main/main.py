# FEDEngine an ASCII roguelike game engine by NostalGeek19: https://github.com/NostalGeek19

# pip install tcod.

import tcod
import random
import os
from typing import List, Tuple


# CONFIG.
SCREEN_W = 80
SCREEN_H = 50
MAP_W = 80
MAP_H = 45
Z_LEVELS = 3
FOV_RADIUS = 8

SURFACE_LIMIT = MAP_H // 3


# COLORS.
COLOR_GRASS = (100, 180, 60)
COLOR_TREE = (20, 120, 20)
COLOR_WATER = (40, 80, 180)
COLOR_DIRT = (120, 90, 60)
COLOR_STONE = (140, 140, 140)
COLOR_WALL = (100, 100, 100)
COLOR_PLAYER = (255, 255, 220)
COLOR_STAIRS = (200, 160, 120)


# TILE.
class Tile:
    def __init__(self, walkable: bool, char: str, color: Tuple[int, int, int]):
        self.walkable = walkable
        self.char = char
        self.color = color

# Tiles.
FLOOR_GRASS = Tile(True, ",", COLOR_GRASS)
FLOOR_DIRT  = Tile(True, "·", COLOR_DIRT)
WATER       = Tile(False, "≈", COLOR_WATER)
TREE        = Tile(False, "♣", COLOR_TREE)

WALL_LIGHT  = Tile(False, "▒", COLOR_WALL)
WALL_MEDIUM = Tile(False, "▓", COLOR_WALL)
WALL_HEAVY  = Tile(False, "█", COLOR_WALL)

STAIRS_UP   = Tile(True, "<", COLOR_STAIRS)
STAIRS_DOWN = Tile(True, ">", COLOR_STAIRS)

PLAYER_CHAR = "☻"


# CAVE UTILS.
def carve_corridor(gmap, x1, y1, x2, y2):
    x, y = x1, y1
    while x != x2:
        gmap[x][y] = FLOOR_DIRT
        x += 1 if x < x2 else -1
    while y != y2:
        gmap[x][y] = FLOOR_DIRT
        y += 1 if y < y2 else -1
    gmap[x][y] = FLOOR_DIRT

def carve_vertical_shaft(gmap, x, y_top, y_bottom):
    for y in range(y_top, y_bottom + 1):
        gmap[x][y] = FLOOR_DIRT


# REGION DETECTION.
def get_largest_cave_region(gmap, y_start):
    visited = set()
    largest = []

    def flood(x, y):
        stack = [(x, y)]
        region = []
        while stack:
            cx, cy = stack.pop()
            if (cx, cy) in visited:
                continue
            if not (0 <= cx < MAP_W and y_start <= cy < MAP_H):
                continue
            if not gmap[cx][cy].walkable:
                continue
            visited.add((cx, cy))
            region.append((cx, cy))
            stack.extend([
                (cx+1, cy), (cx-1, cy),
                (cx, cy+1), (cx, cy-1)
            ])
        return region

    for x in range(MAP_W):
        for y in range(y_start, MAP_H):
            if gmap[x][y].walkable and (x, y) not in visited:
                region = flood(x, y)
                if len(region) > len(largest):
                    largest = region

    return largest


# WALL RELIEF.
def apply_wall_relief(gmap, y_start):
    for x in range(1, MAP_W - 1):
        for y in range(y_start, MAP_H - 1):
            if gmap[x][y].walkable:
                continue
            walls = 0
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                if not gmap[x+dx][y+dy].walkable:
                    walls += 1
            if walls <= 1:
                gmap[x][y] = WALL_LIGHT
            elif walls <= 3:
                gmap[x][y] = WALL_MEDIUM
            else:
                gmap[x][y] = WALL_HEAVY


# SURFACE LEVEL.
def generate_surface_level() -> List[List[Tile]]:
    gmap = [[FLOOR_GRASS for _ in range(MAP_H)] for _ in range(MAP_W)]

    # Forest.
    for x in range(MAP_W):
        for y in range(SURFACE_LIMIT):
            r = random.random()
            if r < 0.08:
                gmap[x][y] = TREE
            elif r < 0.12:
                gmap[x][y] = WATER
            else:
                gmap[x][y] = FLOOR_GRASS

    # Underground = walls.
    for x in range(MAP_W):
        for y in range(SURFACE_LIMIT, MAP_H):
            gmap[x][y] = WALL_MEDIUM

    # Caves.
    rooms = []
    for _ in range(25):
        w = random.randint(4, 10)
        h = random.randint(4, 8)
        x0 = random.randint(2, MAP_W - w - 3)
        y0 = random.randint(SURFACE_LIMIT + 4, MAP_H - h - 3)

        room = []
        for x in range(x0, x0 + w):
            for y in range(y0, y0 + h):
                gmap[x][y] = FLOOR_DIRT
                room.append((x, y))
        rooms.append(room)

    for i in range(1, len(rooms)):
        x1, y1 = random.choice(rooms[i - 1])
        x2, y2 = random.choice(rooms[i])
        carve_corridor(gmap, x1, y1, x2, y2)

    cave_region = get_largest_cave_region(gmap, SURFACE_LIMIT)

    # Entrances (1–2).
    random.shuffle(cave_region)
    entrances = 0
    for (x, y) in cave_region:
        if entrances >= 2:
            break
        if y > SURFACE_LIMIT + 2:
            carve_vertical_shaft(gmap, x, SURFACE_LIMIT - 1, y)
            entrances += 1

    # Stairs down.
    sx, sy = random.choice(cave_region)
    gmap[sx][sy] = STAIRS_DOWN

    apply_wall_relief(gmap, SURFACE_LIMIT)
    return gmap




# SIMPLE CAVE LEVEL.
def generate_cave_level() -> List[List[Tile]]:
    gmap = [[WALL_MEDIUM for _ in range(MAP_H)] for _ in range(MAP_W)]

    rooms = []
    for _ in range(30):
        w = random.randint(4, 10)
        h = random.randint(4, 8)
        x0 = random.randint(2, MAP_W - w - 3)
        y0 = random.randint(2, MAP_H - h - 3)

        room = []
        for x in range(x0, x0 + w):
            for y in range(y0, y0 + h):
                gmap[x][y] = FLOOR_DIRT
                room.append((x, y))
        rooms.append(room)

    for i in range(1, len(rooms)):
        carve_corridor(gmap, *random.choice(rooms[i - 1]), *random.choice(rooms[i]))

    cave = get_largest_cave_region(gmap, 0)
    gmap[random.choice(cave)[0]][random.choice(cave)[1]] = STAIRS_DOWN
    apply_wall_relief(gmap, 0)
    return gmap


# WORLD.
def generate_world():
    world = []
    world.append(generate_surface_level())
    for _ in range(Z_LEVELS - 1):
        world.append(generate_cave_level())
    return world


# FOV.
def compute_fov(gmap, px, py):
    visible = [[False]*MAP_H for _ in range(MAP_W)]
    for x in range(MAP_W):
        for y in range(MAP_H):
            if abs(x-px) + abs(y-py) <= FOV_RADIUS:
                visible[x][y] = True
    return visible


# RENDER.
def render(console, gmap, visible, px, py, z):
    console.clear()
    for x in range(MAP_W):
        for y in range(MAP_H):
            if visible[x][y]:
                t = gmap[x][y]
                console.print(x, y, t.char, fg=t.color)
    console.print(px, py, PLAYER_CHAR, fg=COLOR_PLAYER)
    console.print(0, MAP_H, f"Z:{z}", fg=(200,200,200))
    
def load_tileset():
    # 1. PNG tileset.
    png_tilesets = [
       
    ]

    for fn in png_tilesets:
        if os.path.exists(fn):
            try:
                return tcod.tileset.load_tilesheet(
                    fn, 16, 16, tcod.tileset.CHARMAP_CP437
                )
            except Exception:
                pass

    # 2. TTF.
    ttf_fonts = [
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/lucon.ttf",
        "C:/Windows/Fonts/Courier New.ttf",
    ]

    for font in ttf_fonts:
        if os.path.exists(font):
            try:
                return tcod.tileset.load_truetype_font(
                    font, 16, 16
                )
            except Exception:
                pass

    # 3. Error.
    raise RuntimeError(
        "No tileset. "
        "Place the .png file next to main.py"
    )

# MAIN.
def main():
    tileset = load_tileset()

    with tcod.context.new_terminal(
        SCREEN_W,
        SCREEN_H + 1,
        tileset=tileset,
        title="FED-Engine",
        vsync=True
    ) as context:

        console = tcod.Console(SCREEN_W, SCREEN_H + 1, order="F")
        world = generate_world()
        z = 0

        px, py = next(
            (x,y) for x in range(MAP_W) for y in range(MAP_H)
            if world[z][x][y].walkable
        )

        while True:
            visible = compute_fov(world[z], px, py)
            render(console, world[z], visible, px, py, z)
            context.present(console)

            for event in tcod.event.wait():
                if event.type == "QUIT":
                    raise SystemExit()
                if event.type == "KEYDOWN":
                    dx = dy = 0
                    if event.sym in (tcod.event.K_w, tcod.event.K_UP): dy = -1
                    if event.sym in (tcod.event.K_s, tcod.event.K_DOWN): dy = 1
                    if event.sym in (tcod.event.K_a, tcod.event.K_LEFT): dx = -1
                    if event.sym in (tcod.event.K_d, tcod.event.K_RIGHT): dx = 1

                    nx, ny = px + dx, py + dy
                    if 0 <= nx < MAP_W and 0 <= ny < MAP_H:
                        if world[z][nx][ny].walkable:
                            px, py = nx, ny

if __name__ == "__main__":
    main()
