"""Settings"""
import math

# Constants
# The size of game window
# WIDTH, HEIGHT = 1024, 768
WIDTH, HEIGHT = 800, 480

# fps
FPS = 60

# Color
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHTGREY = (100, 100, 100)

# Numbers commonly used.
ZERO = 0
ONE = 1

PI_CONVERT = 180 / math.pi

# Background color
BACKGROUND_COLOR = BLACK

# Tile size
TILE_SIZE = 32
GRID_WIDTH, GRID_HEIGHT = WIDTH / TILE_SIZE, HEIGHT / TILE_SIZE

# signature, you can edit map with these signature
WALL_SIGN = "*"
PLAYER_SIGN = "p"
MOB_SIGN = "m"


# player settings
PLAYER_ACC_RATE = 4
PLAYER_SHOOT_DELAY = 250
PLAYER_HEALTH = 100


# zombie settings
ZOMBIE_HEALTH = 100
ZOMBIE_ACC_RATE = 2
ZOMBIE_DAMAGE = 20
ZOMBIE_PERCEPTION_DISTANCE = 300