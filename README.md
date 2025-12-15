# ASCII-GameEngine-FEDEngine-by-NostalGeek19
An ASCII roguelike engine developed in Python. The project is intended as a base engine that can be customized: resource mining, creatures, simulation, chunks, world saving, etc.
<img width="812" height="629" alt="FEDEngine" src="https://github.com/user-attachments/assets/4b8f942f-504a-4513-a5de-6ec7cb706377" />

# Key Features

  - ASCII graphics (character rendering)

  - Above-ground and underground caves

  - Multiple levels along the Z axis

  - Guaranteed passage from the surface to the caves

  - Vertical shafts (no diagonal errors)

  - Relief walls

  - Simple, clear architecture


# Dependencies

```pip install tcod```

Windows and Linux are supported.


# Project architecture

The entire engine is located in a single file, ```main.py```, and is logically divided into blocks.

# Colors

All colors are in RGB format and are used for display purposes only.

```COLOR_GRASS = (100, 180, 60)```
```COLOR_TREE = (20, 120, 20)```
```COLOR_WATER = (40, 80, 180)```

# Tile system

Each cell of the map is an object of type Tile:

```
class Tile:
  def __init__(self, walkable, char, color):
    self.walkable = walkable
    self.char = char
    self.color = color
```

# Cave generation

```carve_corridor()```

- Orthogonal directions only

- No diagonals

- Compatible with player movement

```carve_vertical_shaft()```

- Connect the surface to the caves.

- Used for entrances.

- Maximum 1-2 per level.

# Connected Regions (Fill)

```get_largest_cave_region()```

Used for:

  - Finding the main cave

  - Maintaining passability

  - Correct placement of stairs

Algorithm:

  - Filling with floodplain

  - 4 directions (north/east/south/west)

  - Selecting the largest region

# Relief of the walls

The type of wall depends on the number of adjacent walls:

```apply_wall_relief()```

<img width="379" height="340" alt="Снимок экрана 2025-12-15 144728" src="https://github.com/user-attachments/assets/7a21573a-837e-42ee-af08-804b2d8a800f" />

# Surface

```generate_surface_level()```

Stages:

  - Creating a forest (grass, trees, water)

  - Below the surface are solid walls

  - Creating caves

  - Connecting corridors

  - Finding the main cave

  - Building vertical entrances

  - Installing a staircase leading downwards

Caves are never created directly from forests—only through shafts.

# Underground levels

```generate_cave_level()```

  - Only walls and rooms

  - No surface

  - One staircase down

  - The same poured fill was used

# World

```generate_world()```

  - Level 0 — Surface

  - Others — Caves

  - Stored as ```World[z][x][y]```

# Field of view (FOV)

```compute_fov()```

# Rendering

```render()```

Responsible only for the use of:

  - tiles

  - player

  - current Z-level

# Loading a font

```load_tileset()```

Reason:

  - The get_default() function is deprecated and returns an error.

  - Windows + Python 3.13

Algorithm:

  - PNG tile set (if available)

  - System TTF

  - Help error

Using a monospaced font is recommended.
