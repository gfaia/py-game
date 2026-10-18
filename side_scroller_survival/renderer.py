"""Render player visual states without changing gameplay state."""

from __future__ import annotations

import math
from pathlib import Path

import pygame

from entities import Player, Zombie
from gun import Gun
from settings import ZOMBIE_DEATH_ANIMATION_DURATION, ZOMBIE_HIT_EFFECT_DURATION


ASSET_DIRECTORY = Path(__file__).resolve().parent / "assets" / "Character" / "Main"
PLAYER_SPRITE_SCALE = 3
BULLET_SPRITE_SCALE = 5
ZOMBIE_SPRITE_SCALE = 3
SHOOT_ANIMATION_DURATION = 220
PUNCH_ANIMATION_DURATION = 280


class PlayerRenderer:
    """Load player artwork and draw it from the current player state."""

    def __init__(self, gun: Gun) -> None:
        self.gun_animations = self._load_animations(
            {
                "idle_right": ("Idle/Character_side_idle_no-hands-Sheet6.png", 6),
                "idle_left": ("Idle/Character_side-left_idle_no-hands-Sheet6.png", 6),
                "run_right": ("Run/Character_side_run_no-hands-Sheet6.png", 6),
                "run_left": ("Run/Character_side-left_run_no-hands-Sheet6.png", 6),
            }
        )
        self.unarmed_animations = self._load_animations(
            {
                "idle_right": ("Idle/Character_side_idle-Sheet6.png", 6),
                "idle_left": ("Idle/Character_side-left_idle-Sheet6.png", 6),
                "run_right": ("Run/Character_side_run-Sheet6.png", 6),
                "run_left": ("Run/Character_side-left_run-Sheet6.png", 6),
            }
        )
        self.punch_animations = self._load_animations(
            {
                "right": ("Punch/Character_side_punch-Sheet4.png", 4),
                "left": ("Punch/Character_side-left_punch-Sheet4.png", 4),
            }
        )
        weapon_directory = gun.asset_directory
        guns_directory = ASSET_DIRECTORY.parent / "Guns"
        self.gun_hold_animations = {
            "right": self._load_sprite_sheet(guns_directory / weapon_directory / f"{weapon_directory}_side_idle-and-run-Sheet6.png", 6),
            "left": self._load_sprite_sheet(guns_directory / weapon_directory / f"{weapon_directory}_side-left_idle-and-run-Sheet6.png", 6),
        }
        self.gun_shoot_animations = {
            "right": self._load_sprite_sheet(guns_directory / weapon_directory / f"{weapon_directory}_side_shoot-Sheet3.png", 3),
            "left": self._load_sprite_sheet(guns_directory / weapon_directory / f"{weapon_directory}_side-left_shoot-Sheet3.png", 3),
        }
        self.muzzle_flash_animations = {
            "right": self._load_sprite_sheet(guns_directory / "Fire/Fire_side-Sheet3.png", 3),
            "left": self._load_sprite_sheet(guns_directory / "Fire/Fire_side-left-Sheet3.png", 3),
        }

    def draw(
        self,
        surface: pygame.Surface,
        player: Player,
        screen_rect: pygame.Rect,
        shoot_started_at: int,
        punch_started_at: int,
    ) -> None:
        """Draw the player with the artwork for the equipped weapon state."""
        is_running = abs(player.velocity.x) > 0 and player.on_ground
        direction = "right" if player.facing >= 0 else "left"
        shoot_elapsed = pygame.time.get_ticks() - shoot_started_at
        punch_elapsed = pygame.time.get_ticks() - punch_started_at
        is_shooting = player.has_ranged_weapon and 0 <= shoot_elapsed < SHOOT_ANIMATION_DURATION
        is_punching = not player.has_ranged_weapon and 0 <= punch_elapsed < PUNCH_ANIMATION_DURATION
        if is_punching:
            self._draw_punch(surface, screen_rect, direction, punch_elapsed)
            return
        animation_name = f"{'run' if is_running else 'idle'}_{direction}"
        animations = self.gun_animations if player.has_ranged_weapon else self.unarmed_animations
        animation = animations[animation_name]
        frame_duration = 100 if is_running else 180
        frame_index = (pygame.time.get_ticks() // frame_duration) % len(animation)
        sprite_rect = animation[frame_index].get_rect(midbottom=screen_rect.midbottom)
        surface.blit(animation[frame_index], sprite_rect)
        if is_shooting:
            self._draw_shoot_effects(surface, player, sprite_rect, shoot_elapsed)
        elif player.has_ranged_weapon:
            self._draw_held_weapon(surface, sprite_rect, direction, frame_index)

    def _draw_punch(self, surface: pygame.Surface, screen_rect: pygame.Rect, direction: str, punch_elapsed: int) -> None:
        frame_index = min(3, punch_elapsed * 4 // PUNCH_ANIMATION_DURATION)
        punch_frame = self.punch_animations[direction][frame_index]
        surface.blit(punch_frame, punch_frame.get_rect(midbottom=screen_rect.midbottom))

    def _load_animations(self, files: dict[str, tuple[str, int]]) -> dict[str, list[pygame.Surface]]:
        return {name: self._load_sprite_sheet(ASSET_DIRECTORY / filename, frame_count) for name, (filename, frame_count) in files.items()}

    def _load_sprite_sheet(self, path: Path, frame_count: int) -> list[pygame.Surface]:
        sheet = pygame.image.load(path).convert_alpha()
        frame_width = sheet.get_width() // frame_count
        frame_height = sheet.get_height()
        return [
            pygame.transform.scale(
                sheet.subsurface((index * frame_width, 0, frame_width, frame_height)),
                (frame_width * PLAYER_SPRITE_SCALE, frame_height * PLAYER_SPRITE_SCALE),
            )
            for index in range(frame_count)
        ]

    def _draw_held_weapon(self, surface: pygame.Surface, sprite_rect: pygame.Rect, direction: str, frame_index: int) -> None:
        gun = self.gun_hold_animations[direction][frame_index]
        if direction == "right":
            gun_rect = gun.get_rect(midleft=(sprite_rect.centerx + 6, sprite_rect.centery + 3))
        else:
            gun_rect = gun.get_rect(midright=(sprite_rect.centerx - 6, sprite_rect.centery + 3))
        surface.blit(gun, gun_rect)

    def _draw_shoot_effects(self, surface: pygame.Surface, player: Player, sprite_rect: pygame.Rect, shoot_elapsed: int) -> None:
        effect_frame = min(2, shoot_elapsed * 3 // SHOOT_ANIMATION_DURATION)
        aim_side = "right" if player.aim_direction.x >= 0 else "left"
        gun = self.gun_shoot_animations[aim_side][effect_frame]
        muzzle_flash = self.muzzle_flash_animations[aim_side][effect_frame]
        aim_angle = -math.degrees(math.atan2(player.aim_direction.y, player.aim_direction.x))
        rotation = aim_angle if aim_side == "right" else aim_angle - 180
        rotated_gun = pygame.transform.rotate(gun, rotation)
        rotated_flash = pygame.transform.rotate(muzzle_flash, rotation)
        hand_position = pygame.Vector2(sprite_rect.centerx, sprite_rect.centery + 6)
        gun_center = hand_position + player.aim_direction * (gun.get_width() / 2)
        flash_center = hand_position + player.aim_direction * (gun.get_width() + muzzle_flash.get_width() / 2 - 3)
        gun_rect = rotated_gun.get_rect(center=(round(gun_center.x), round(gun_center.y)))
        muzzle_rect = rotated_flash.get_rect(center=(round(flash_center.x), round(flash_center.y)))
        surface.blit(rotated_gun, gun_rect)
        surface.blit(rotated_flash, muzzle_rect)


class BulletRenderer:
    """Draw bullets fired by one configured gun."""

    def __init__(self, gun: Gun) -> None:
        bullet_path = ASSET_DIRECTORY.parent / "Guns" / "Bullets" / gun.bullet_filename
        bullet = pygame.image.load(bullet_path).convert_alpha()
        self.bullet_sprite = pygame.transform.scale(
            bullet,
            (bullet.get_width() * BULLET_SPRITE_SCALE, bullet.get_height() * BULLET_SPRITE_SCALE),
        )

    def draw(self, surface: pygame.Surface, position: tuple[int, int], velocity: pygame.Vector2) -> None:
        """Draw one bullet using its velocity as the visual direction."""
        bullet_angle = -math.degrees(math.atan2(velocity.y, velocity.x))
        bullet_sprite = pygame.transform.rotate(self.bullet_sprite, bullet_angle)
        surface.blit(bullet_sprite, bullet_sprite.get_rect(center=position))


class ZombieRenderer:
    """Draw small zombies with idle and walking animations."""

    def __init__(self) -> None:
        zombie_directory = ASSET_DIRECTORY.parent.parent / "Enemies" / "Zombie_Small"
        self.animations = {
            "idle_right": self._load_sprite_sheet(zombie_directory / "Zombie_Small_Side_Idle-Sheet6.png", 6),
            "idle_left": self._load_sprite_sheet(zombie_directory / "Zombie_Small_Side-left_Idle-Sheet6.png", 6),
            "walk_right": self._load_sprite_sheet(zombie_directory / "Zombie_Small_Side_Walk-Sheet6.png", 6),
            "walk_left": self._load_sprite_sheet(zombie_directory / "Zombie_Small_Side-left_Walk-Sheet6.png", 6),
            "death_right": self._load_sprite_sheet(zombie_directory / "Zombie_Small_Side_First-Death-Sheet6.png", 6),
            "death_left": self._load_sprite_sheet(zombie_directory / "Zombie_Small_Side-left_First-Death-Sheet6.png", 6),
        }
        effects_directory = zombie_directory.parent / "Shot"
        self.hit_effect = self._load_sprite_sheet(effects_directory / "shot_1-Sheet3.png", 3)

    def draw(self, surface: pygame.Surface, zombie: Zombie, screen_rect: pygame.Rect, game_time: float) -> None:
        """Draw one zombie at its world collision rectangle."""
        direction = "right" if zombie.facing >= 0 else "left"
        if not zombie.alive:
            self._draw_death(surface, zombie, screen_rect, direction, game_time)
            return
        action = "walk" if zombie.is_moving else "idle"
        animation = self.animations[f"{action}_{direction}"]
        frame_duration = 110 if zombie.is_moving else 180
        frame_index = (pygame.time.get_ticks() // frame_duration) % len(animation)
        frame = animation[frame_index]
        surface.blit(frame, frame.get_rect(midbottom=screen_rect.midbottom))
        if zombie.is_hit(game_time):
            self._draw_hit_effect(surface, zombie, screen_rect, game_time)

    def _draw_death(
        self,
        surface: pygame.Surface,
        zombie: Zombie,
        screen_rect: pygame.Rect,
        direction: str,
        game_time: float,
    ) -> None:
        death_started_at = zombie.death_started_at if zombie.death_started_at is not None else game_time
        elapsed = max(0.0, game_time - death_started_at)
        frame_index = min(5, int(elapsed * 6 / ZOMBIE_DEATH_ANIMATION_DURATION))
        frame = self.animations[f"death_{direction}"][frame_index]
        surface.blit(frame, frame.get_rect(midbottom=screen_rect.midbottom))

    def _draw_hit_effect(
        self,
        surface: pygame.Surface,
        zombie: Zombie,
        screen_rect: pygame.Rect,
        game_time: float,
    ) -> None:
        elapsed = max(0.0, game_time - zombie.hit_started_at)
        frame_index = min(2, int(elapsed * 3 / ZOMBIE_HIT_EFFECT_DURATION))
        effect = self.hit_effect[frame_index]
        surface.blit(effect, effect.get_rect(center=screen_rect.center))

    @staticmethod
    def _load_sprite_sheet(path: Path, frame_count: int) -> list[pygame.Surface]:
        sheet = pygame.image.load(path).convert_alpha()
        frame_width = sheet.get_width() // frame_count
        frame_height = sheet.get_height()
        return [
            pygame.transform.scale(
                sheet.subsurface((index * frame_width, 0, frame_width, frame_height)),
                (frame_width * ZOMBIE_SPRITE_SCALE, frame_height * ZOMBIE_SPRITE_SCALE),
            )
            for index in range(frame_count)
        ]
