"""Entity data and behavior for the side-scroller survival demo."""

from __future__ import annotations

import random
from collections.abc import Iterable

import pygame

import settings
from gun import Gun


def _setting(name: str, default: float | int) -> float | int:
    """Read a game constant while keeping entity defaults in one place."""
    return getattr(settings, name, default)


GRAVITY = _setting("GRAVITY", 1_800)
PLAYER_SPEED = _setting("PLAYER_SPEED", 300)
PLAYER_JUMP_SPEED = _setting("PLAYER_JUMP_SPEED", 650)
PLAYER_MAX_HEALTH = _setting("PLAYER_MAX_HEALTH", 100)
PLAYER_FIRE_COOLDOWN = _setting("PLAYER_FIRE_COOLDOWN", 0.25)
PLAYER_MELEE_DAMAGE = _setting("PLAYER_MELEE_DAMAGE", 1)
PLAYER_MELEE_COOLDOWN = _setting("PLAYER_MELEE_COOLDOWN", 0.35)
PLAYER_MELEE_RANGE = _setting("PLAYER_MELEE_RANGE", 68)
BULLET_SPEED = _setting("BULLET_SPEED", 850)
BULLET_DAMAGE = _setting("BULLET_DAMAGE", 20)
ZOMBIE_SPEED = _setting("ZOMBIE_SPEED", 90)
ZOMBIE_WIDTH = _setting("ZOMBIE_WIDTH", 36)
ZOMBIE_HEIGHT = _setting("ZOMBIE_HEIGHT", 54)
ZOMBIE_MAX_HEALTH = _setting("ZOMBIE_MAX_HEALTH", 40)
ZOMBIE_ATTACK_DAMAGE = _setting("ZOMBIE_ATTACK_DAMAGE", 8)
ZOMBIE_ATTACK_COOLDOWN = _setting("ZOMBIE_ATTACK_COOLDOWN", 1.0)
ZOMBIE_HIT_EFFECT_DURATION = _setting("ZOMBIE_HIT_EFFECT_DURATION", 0.18)
ZOMBIE_DEATH_ANIMATION_DURATION = _setting("ZOMBIE_DEATH_ANIMATION_DURATION", 0.72)


class Player:
    """A controllable survivor with platform movement and ranged attacks."""

    def __init__(self, position: tuple[int, int]) -> None:
        self.rect = pygame.Rect(position[0], position[1], 30, 48)
        self.position = pygame.Vector2(self.rect.topleft)
        self.velocity = pygame.Vector2()
        self.aim_direction = pygame.Vector2(1, 0)
        self.health = int(PLAYER_MAX_HEALTH)
        self.max_health = int(PLAYER_MAX_HEALTH)
        self.on_ground = False
        self.facing = 1
        self.gun = Gun(str(getattr(settings, "INITIAL_WEAPON", "gun")), float(PLAYER_FIRE_COOLDOWN))
        self.weapon_slots = ("unarmed", self.gun.name)
        self.weapon_state = self.gun.name
        self.last_melee_at = -float(PLAYER_MELEE_COOLDOWN)

    @property
    def alive(self) -> bool:
        return self.health > 0

    @property
    def has_ranged_weapon(self) -> bool:
        """Return true when the player equips a weapon that can fire bullets."""
        return self.weapon_state != "unarmed"

    def switch_weapon(self) -> str:
        """Equip the next available weapon and return its state name."""
        current_index = self.weapon_slots.index(self.weapon_state)
        self.weapon_state = self.weapon_slots[(current_index + 1) % len(self.weapon_slots)]
        return self.weapon_state

    def update(
        self,
        delta_time: float,
        move_direction: float,
        platforms: Iterable[pygame.Rect],
    ) -> None:
        """Move the player and resolve horizontal and vertical collisions."""
        self.velocity.x = max(-1, min(1, move_direction)) * float(PLAYER_SPEED)
        if self.velocity.x:
            self.facing = 1 if self.velocity.x > 0 else -1

        self.position.x += self.velocity.x * delta_time
        self.rect.x = round(self.position.x)
        self._resolve_horizontal(platforms)

        self.velocity.y += float(GRAVITY) * delta_time
        self.position.y += self.velocity.y * delta_time
        self.rect.y = round(self.position.y)
        self.on_ground = False
        self._resolve_vertical(platforms)

    def jump(self) -> bool:
        """Start a jump when the player stands on a platform."""
        if not self.on_ground or not self.alive:
            return False
        self.velocity.y = -float(PLAYER_JUMP_SPEED)
        self.on_ground = False
        return True

    def aim(self, world_target: tuple[float, float]) -> None:
        """Set the firing direction from a target in world coordinates."""
        direction = pygame.Vector2(world_target) - pygame.Vector2(self.rect.center)
        if direction.length_squared() > 0:
            self.aim_direction = direction.normalize()
            self.facing = 1 if self.aim_direction.x >= 0 else -1

    def fire(self, now: float) -> Bullet | None:
        """Create a bullet when the fire cooldown and health allow it."""
        if not self.alive or not self.has_ranged_weapon or not self.gun.fire(now):
            return None
        self.last_shot_at = now
        start = pygame.Vector2(self.rect.center) + self.aim_direction * 20
        return Bullet(start, self.aim_direction)

    def melee_attack(self, now: float) -> pygame.Rect | None:
        """Return the current punch area when the melee cooldown allows it."""
        if not self.alive or self.has_ranged_weapon:
            return None
        if now - self.last_melee_at < float(PLAYER_MELEE_COOLDOWN):
            return None
        self.last_melee_at = now
        attack_range = int(PLAYER_MELEE_RANGE)
        attack_top = self.rect.centery - attack_range // 2
        if self.facing >= 0:
            return pygame.Rect(self.rect.right, attack_top, attack_range, attack_range)
        return pygame.Rect(self.rect.left - attack_range, attack_top, attack_range, attack_range)

    def take_damage(self, amount: int) -> None:
        self.health = max(0, self.health - amount)

    def _resolve_horizontal(self, platforms: Iterable[pygame.Rect]) -> None:
        for platform in platforms:
            if not self.rect.colliderect(platform):
                continue
            if self.velocity.x > 0:
                self.rect.right = platform.left
            elif self.velocity.x < 0:
                self.rect.left = platform.right
            self.position.x = self.rect.x

    def _resolve_vertical(self, platforms: Iterable[pygame.Rect]) -> None:
        for platform in platforms:
            if not self.rect.colliderect(platform):
                continue
            if self.velocity.y > 0:
                self.rect.bottom = platform.top
                self.on_ground = True
            elif self.velocity.y < 0:
                self.rect.top = platform.bottom
            self.velocity.y = 0
            self.position.y = self.rect.y


class Bullet:
    """A short-lived projectile that moves in a straight line."""

    def __init__(self, position: pygame.Vector2, direction: pygame.Vector2) -> None:
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(direction).normalize() * float(BULLET_SPEED)
        self.rect = pygame.Rect(round(position.x) - 4, round(position.y) - 2, 8, 4)
        self.damage = int(BULLET_DAMAGE)
        self.active = True

    def update(self, delta_time: float, world_bounds: pygame.Rect) -> None:
        if not self.active:
            return
        self.position += self.velocity * delta_time
        self.rect.center = (round(self.position.x), round(self.position.y))
        if not world_bounds.colliderect(self.rect):
            self.active = False


class Zombie:
    """A basic enemy that pursues the player, then attacks its target."""

    def __init__(self, position: tuple[int, int]) -> None:
        self.rect = pygame.Rect(position[0], position[1], int(ZOMBIE_WIDTH), int(ZOMBIE_HEIGHT))
        self.position = pygame.Vector2(self.rect.topleft)
        self.health = int(ZOMBIE_MAX_HEALTH)
        self.max_health = int(ZOMBIE_MAX_HEALTH)
        self.speed = float(ZOMBIE_SPEED)
        self.attack_damage = int(ZOMBIE_ATTACK_DAMAGE)
        self.attack_cooldown = float(ZOMBIE_ATTACK_COOLDOWN)
        self.last_attack_at = -self.attack_cooldown
        self.target = "gate"
        self.facing = 1
        self.is_moving = False
        self.hit_started_at = -float(ZOMBIE_HIT_EFFECT_DURATION)
        self.death_started_at: float | None = None

    @property
    def alive(self) -> bool:
        return self.health > 0

    def update(self, delta_time: float, player: Player, gate: Gate) -> None:
        """Move toward the nearest valid player or the safety gate."""
        if not self.alive:
            self.is_moving = False
            return
        target_rect = gate.rect
        self.target = "gate"
        if player.alive and abs(player.rect.centerx - self.rect.centerx) < 420:
            target_rect = player.rect
            self.target = "player"

        distance = target_rect.centerx - self.rect.centerx
        self.is_moving = abs(distance) > 4
        if abs(distance) > 4:
            direction = 1 if distance > 0 else -1
            self.facing = direction
            self.position.x += direction * self.speed * delta_time
            self.rect.x = round(self.position.x)

    def attack(self, now: float, player: Player, gate: Gate) -> str | None:
        """Damage a touching target and return its name, or return None."""
        target = player if self.target == "player" else gate
        if not self.rect.colliderect(target.rect):
            return None
        if now - self.last_attack_at < self.attack_cooldown:
            return None
        self.last_attack_at = now
        target.take_damage(self.attack_damage)
        return self.target

    def take_damage(self, amount: int, now: float) -> None:
        """Record damage and start the hit or death visual state."""
        if not self.alive:
            return
        self.health = max(0, self.health - amount)
        self.hit_started_at = now
        if not self.alive:
            self.death_started_at = now
            self.is_moving = False

    def is_hit(self, now: float) -> bool:
        """Return true while the short hit effect remains visible."""
        return self.alive and now - self.hit_started_at < float(ZOMBIE_HIT_EFFECT_DURATION)

    def death_animation_finished(self, now: float) -> bool:
        """Return true after a dead zombie completes its death animation."""
        return self.death_started_at is not None and now - self.death_started_at >= float(ZOMBIE_DEATH_ANIMATION_DURATION)


class SupplyCrate:
    """A one-use source of ammunition, food, and wooden boards."""

    def __init__(self, position: tuple[int, int], loot: dict[str, int] | None = None) -> None:
        self.rect = pygame.Rect(position[0], position[1], 32, 32)
        self.opened = False
        self.loot = loot or self._random_loot()

    def can_search(self, player: Player, distance: int = 56) -> bool:
        return not self.opened and self.rect.inflate(distance, distance).colliderect(player.rect)

    def search(self, player: Player) -> dict[str, int] | None:
        """Open the crate when the player is close and return its resources."""
        if not self.can_search(player):
            return None
        self.opened = True
        return self.loot.copy()

    @staticmethod
    def _random_loot() -> dict[str, int]:
        resource = random.choice(("ammo", "food", "boards"))
        return {resource: random.randint(1, 3)}


class Gate:
    """The safety-house gate that zombies must not destroy."""

    def __init__(self, rect: pygame.Rect, health: int = 150) -> None:
        self.rect = pygame.Rect(rect)
        self.health = health
        self.max_health = health

    @property
    def alive(self) -> bool:
        return self.health > 0

    def take_damage(self, amount: int) -> None:
        self.health = max(0, self.health - amount)
