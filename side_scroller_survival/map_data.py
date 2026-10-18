"""Static world geometry for the side-scroller survival demo."""

from settings import GROUND_Y, WORLD_WIDTH

# Rectangles use (left, top, width, height) world coordinates.
GROUND_RECT = (0, GROUND_Y, WORLD_WIDTH, 100)

# This demo uses one flat ground surface. Decals below are visual only.
PLATFORMS = ()
WALLS = ()

SAFEHOUSE_RECT = (28, 350, 334, 270)
SAFEHOUSE_GATE = (330, 510, 32, 110)
PLAYER_START = (110, GROUND_Y - 58)

# Each crate has a fixed location. World code chooses one resource when the
# player opens it.
SUPPLY_CRATES = (
    (790, GROUND_Y - 32, 32, 32),
    (1_720, GROUND_Y - 32, 32, 32),
    (2_740, GROUND_Y - 32, 32, 32),
)

# Decorative objects use (type, left, top). They have no game collision.
BACKGROUND_DECALS = (
    ("billboard", 520, 365),
    ("wrecked_vehicle", 1_120, 535),
    ("road_sign", 1_540, 445),
    ("graffiti", 2_150, 500),
    ("streetlight", 2_520, 330),
    ("billboard", 3_050, 390),
    ("wrecked_vehicle", 3_340, 535),
)

# Foreground objects move faster than the world to create depth.
FOREGROUND_DECALS = (
    ("fence", 690, 510),
    ("rubble", 1_420, 565),
    ("utility_pole", 2_260, 260),
    ("fence", 3_060, 510),
)

LEFT_ZOMBIE_SPAWN = (-48, GROUND_Y - 54)
RIGHT_ZOMBIE_SPAWN = (WORLD_WIDTH + 48, GROUND_Y - 54)
ZOMBIE_SPAWNS = (LEFT_ZOMBIE_SPAWN, RIGHT_ZOMBIE_SPAWN)
