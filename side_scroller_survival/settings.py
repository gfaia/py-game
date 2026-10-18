"""Shared constants for the side-scroller survival demo."""

from pathlib import Path
import tomllib


CONFIG_PATH = Path(__file__).with_name("game_config.toml")


def _load_config() -> dict[str, object]:
    try:
        with CONFIG_PATH.open("rb") as config_file:
            return tomllib.load(config_file)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise RuntimeError(f"Cannot load game configuration: {CONFIG_PATH}") from error


def _config_value(section: str, name: str, default: object) -> object:
    values = GAME_CONFIG.get(section)
    if not isinstance(values, dict):
        return default
    return values.get(name, default)


def _config_int(section: str, name: str, default: int) -> int:
    try:
        return int(_config_value(section, name, default))
    except (TypeError, ValueError) as error:
        raise RuntimeError(f"Invalid integer for {section}.{name} in {CONFIG_PATH}") from error


def _config_float(section: str, name: str, default: float) -> float:
    try:
        return float(_config_value(section, name, default))
    except (TypeError, ValueError) as error:
        raise RuntimeError(f"Invalid number for {section}.{name} in {CONFIG_PATH}") from error


GAME_CONFIG = _load_config()

WINDOW_TITLE = "Safehouse: Night Watch"
WINDOW_WIDTH = 1_280
WINDOW_HEIGHT = 720
FPS = 60

# World and camera
WORLD_WIDTH = 3_600
GROUND_Y = 620
CAMERA_FOLLOW_X = WINDOW_WIDTH // 2

# Physics values use pixels and seconds.
GRAVITY = 1_800
MAX_FALL_SPEED = 900
PLAYER_SPEED = _config_float("player", "speed", 300)
PLAYER_JUMP_SPEED = _config_float("player", "jump_speed", 650)

# Entity dimensions and state
PLAYER_WIDTH = 38
PLAYER_HEIGHT = 58
PLAYER_MAX_HEALTH = _config_int("player", "max_health", 100)
PLAYER_FIRE_COOLDOWN = _config_float("player", "fire_cooldown", 0.22)
PLAYER_MELEE_DAMAGE = _config_int("player", "melee_damage", 1)
PLAYER_MELEE_COOLDOWN = _config_float("player", "melee_cooldown", 0.35)
PLAYER_MELEE_RANGE = _config_int("player", "melee_range", 68)
PLAYER_DAMAGE_COOLDOWN = 0.75
INITIAL_WEAPON = str(_config_value("player", "initial_weapon", "gun")).lower()
INITIAL_AMMO = _config_int("player", "initial_ammo", 6)
INITIAL_FOOD = _config_int("player", "initial_food", 0)
INITIAL_BOARDS = _config_int("player", "initial_boards", 0)

ZOMBIE_WIDTH = 36
ZOMBIE_HEIGHT = 54
ZOMBIE_SPEED = _config_float("zombies", "speed", 78)
ZOMBIE_MAX_HEALTH = _config_int("zombies", "max_health", 3)
ZOMBIE_DAMAGE = _config_int("zombies", "damage", 8)
ZOMBIE_ATTACK_COOLDOWN = _config_float("zombies", "attack_cooldown", 1.0)
ZOMBIE_HIT_EFFECT_DURATION = _config_float("zombies", "hit_effect_duration", 0.18)
ZOMBIE_DEATH_ANIMATION_DURATION = _config_float("zombies", "death_animation_duration", 0.72)
MAX_ZOMBIES = _config_int("zombies", "max_count", 14)
ZOMBIE_SPAWN_INTERVAL = _config_float("zombies", "spawn_interval", 1.8)

BULLET_RADIUS = 5
BULLET_SPEED = _config_float("weapons", "bullet_speed", 760)
BULLET_DAMAGE = _config_int("weapons", "bullet_damage", 1)
BULLET_MAX_DISTANCE = _config_int("weapons", "bullet_max_distance", 900)

GATE_MAX_HEALTH = _config_int("gate", "max_health", 150)
GATE_DAMAGE = _config_int("gate", "damage", 6)

# A short loop keeps the demo easy to test.
DAY_DURATION = _config_float("timing", "day_duration", 45.0)
NIGHT_DURATION = _config_float("timing", "night_duration", 45.0)
RESULT_DURATION = _config_float("timing", "result_duration", 4.0)

# Colors
SKY_DAY_COLOR = (124, 193, 226)
SKY_NIGHT_COLOR = (20, 31, 59)
GROUND_COLOR = (62, 69, 62)
PLATFORM_COLOR = (90, 78, 65)
PLATFORM_EDGE_COLOR = (147, 119, 82)
BUILDING_COLOR = (76, 83, 91)
SAFEHOUSE_COLOR = (91, 108, 99)
GATE_COLOR = (130, 81, 55)
CRATE_COLOR = (184, 133, 69)
CRATE_OPEN_COLOR = (96, 82, 63)
PLAYER_COLOR = (70, 194, 191)
ZOMBIE_COLOR = (125, 176, 93)
BULLET_COLOR = (255, 229, 119)
HEALTH_COLOR = (83, 205, 105)
DAMAGE_COLOR = (213, 78, 70)
HUD_COLOR = (20, 25, 33)
TEXT_COLOR = (242, 242, 235)
SHADOW_COLOR = (28, 35, 43)

# Controls
MOVE_LEFT_KEY = "a"
MOVE_RIGHT_KEY = "d"
JUMP_KEY = "space"
SEARCH_KEY = "e"
RESTART_KEY = "r"
QUIT_KEY = "escape"
