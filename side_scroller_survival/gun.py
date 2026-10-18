"""Gun state, weapon artwork names, and firing cooldown rules."""

from __future__ import annotations


WEAPON_DIRECTORIES = {"gun": "Gun", "pistol": "Pistol", "shotgun": "Shotgun"}
BULLET_FILES = {
    "gun": "Gun-bullet_Bullet.png",
    "pistol": "Pistol-bullet_Bullet.png",
    "shotgun": "Shotgun-bullet.png",
}


class Gun:
    """Represent one ranged weapon that the player can equip and fire."""

    def __init__(self, name: str, fire_cooldown: float) -> None:
        if name not in WEAPON_DIRECTORIES:
            raise ValueError(f"Unsupported weapon: {name}")
        self.name = name
        self.fire_cooldown = fire_cooldown
        self.last_shot_at = -fire_cooldown

    @property
    def asset_directory(self) -> str:
        """Return the directory name that contains this gun's artwork."""
        return WEAPON_DIRECTORIES[self.name]

    @property
    def bullet_filename(self) -> str:
        """Return the filename for this gun's bullet artwork."""
        return BULLET_FILES[self.name]

    def fire(self, now: float) -> bool:
        """Record a shot when the firing cooldown allows it."""
        if now - self.last_shot_at < self.fire_cooldown:
            return False
        self.last_shot_at = now
        return True
