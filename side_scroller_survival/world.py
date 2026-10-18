"""Rules and mutable state for the side-scroller survival demo."""

from __future__ import annotations

from collections.abc import Sequence

import pygame

from entities import Bullet, Gate, Player, SupplyCrate, Zombie
from map_data import (
    GROUND_RECT,
    PLAYER_START,
    PLATFORMS,
    SAFEHOUSE_GATE,
    SUPPLY_CRATES,
    WALLS,
    ZOMBIE_SPAWNS,
)
from settings import (
    DAY_DURATION,
    GATE_MAX_HEALTH,
    INITIAL_AMMO,
    INITIAL_BOARDS,
    INITIAL_FOOD,
    MAX_ZOMBIES,
    NIGHT_DURATION,
    PLAYER_MELEE_DAMAGE,
    RESULT_DURATION,
    WINDOW_HEIGHT,
    WORLD_WIDTH,
    ZOMBIE_SPAWN_INTERVAL,
)


class World:
    """Keep the game entities, resource totals, and phase rules together."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Restore the complete demo to its first daytime state."""
        self.world_bounds = pygame.Rect(0, 0, WORLD_WIDTH, WINDOW_HEIGHT)
        self.platforms = [pygame.Rect(GROUND_RECT)]
        self.platforms.extend(pygame.Rect(rect) for rect in PLATFORMS)
        self.platforms.extend(pygame.Rect(rect) for rect in WALLS)
        self.player = Player(PLAYER_START)
        self.gate = Gate(pygame.Rect(SAFEHOUSE_GATE), GATE_MAX_HEALTH)
        self.crates = [SupplyCrate((rect[0], rect[1])) for rect in SUPPLY_CRATES]
        self.bullets: list[Bullet] = []
        self.zombies: list[Zombie] = []
        self.resources = {
            "ammo": INITIAL_AMMO,
            "food": INITIAL_FOOD,
            "boards": INITIAL_BOARDS,
        }
        self.phase = "day"
        self.time_remaining = float(DAY_DURATION)
        self.result_time_remaining = 0.0
        self.elapsed_time = 0.0
        self.spawn_time_remaining = 0.0
        self.spawn_index = 0
        self.message = "Search supply crates before night falls."

    @property
    def status(self) -> str:
        """Return the current phase for HUD and end-screen code."""
        return self.phase

    @property
    def active(self) -> bool:
        """Return true while player controls can change the world."""
        return self.phase in {"day", "night"}

    @property
    def is_night(self) -> bool:
        """Return true when zombies can enter the world."""
        return self.phase == "night"

    def update_player(
        self,
        delta_time: float,
        move_direction: float,
        aim_target: tuple[float, float] | None = None,
    ) -> None:
        """Move and aim the player while the demo is active."""
        if not self.active or not self.player.alive:
            return
        if aim_target is not None:
            self.player.aim(aim_target)
        self.player.update(delta_time, move_direction, self.platforms)
        self.player.rect.left = max(self.world_bounds.left, self.player.rect.left)
        self.player.rect.right = min(self.world_bounds.right, self.player.rect.right)
        self.player.position.x = self.player.rect.x

    def try_search(self) -> dict[str, int] | None:
        """Open the nearby crate once and add its supplies to the inventory."""
        if not self.active:
            return None
        for crate in self.crates:
            loot = crate.search(self.player)
            if loot is None:
                continue
            for resource, amount in loot.items():
                self.resources[resource] = self.resources.get(resource, 0) + amount
            found = ", ".join(f"{amount} {resource}" for resource, amount in loot.items())
            self.message = f"Found {found}."
            return loot
        self.message = "Move closer to an unopened supply crate."
        return None

    def fire(self) -> Bullet | None:
        """Use one ammunition unit to fire a bullet when possible."""
        if not self.active:
            return None
        if not self.player.has_ranged_weapon:
            self.message = "Fists equipped. Press Q to equip your weapon."
            return None
        if self.resources["ammo"] <= 0:
            self.message = "No ammunition. Search a supply crate."
            return None
        bullet = self.player.fire(self.elapsed_time)
        if bullet is None:
            return None
        self.resources["ammo"] -= 1
        self.bullets.append(bullet)
        return bullet

    def melee_attack(self) -> int | None:
        """Punch zombies in front of the unarmed player and return the hit count."""
        if not self.active:
            return None
        attack_area = self.player.melee_attack(self.elapsed_time)
        if attack_area is None:
            return None
        hit_count = 0
        for zombie in self.zombies:
            if zombie.alive and attack_area.colliderect(zombie.rect):
                zombie.take_damage(int(PLAYER_MELEE_DAMAGE), self.elapsed_time)
                hit_count += 1
        self.message = "Punch hit a zombie." if hit_count == 1 else "Punch missed."
        if hit_count > 1:
            self.message = f"Punch hit {hit_count} zombies."
        return hit_count

    def switch_weapon(self) -> str | None:
        """Switch the player's equipped weapon while the game is active."""
        if not self.active:
            return None
        weapon_state = self.player.switch_weapon()
        if weapon_state == "unarmed":
            self.message = "Fists equipped."
        else:
            self.message = f"Equipped {weapon_state}."
        return weapon_state

    def update(self, delta_time: float) -> None:
        """Advance timers, projectiles, enemies, and the current game phase."""
        if delta_time <= 0:
            return
        if not self.active:
            if self.phase in {"success", "failure"}:
                self.result_time_remaining = max(0.0, self.result_time_remaining - delta_time)
            return

        self.elapsed_time += delta_time
        self._update_bullets(delta_time)
        if self.is_night:
            self._spawn_zombies(delta_time)
            self._update_zombies(delta_time)
        self._remove_dead_zombies()

        if not self.player.alive:
            self._finish("failure", "You did not survive the night.")
            return
        if not self.gate.alive:
            self._finish("failure", "The safehouse gate fell.")
            return

        self.time_remaining = max(0.0, self.time_remaining - delta_time)
        if self.time_remaining > 0:
            return
        if self.phase == "day":
            self._start_night()
        else:
            self._finish("success", "Dawn arrived. The safehouse survived.")

    def _start_night(self) -> None:
        self.phase = "night"
        self.time_remaining = float(NIGHT_DURATION)
        self.spawn_time_remaining = 0.0
        self.message = "Night started. Defend the safehouse gate."

    def _finish(self, outcome: str, message: str) -> None:
        self.phase = outcome
        self.message = message
        self.result_time_remaining = float(RESULT_DURATION)

    def _spawn_zombies(self, delta_time: float) -> None:
        self.spawn_time_remaining -= delta_time
        if self.spawn_time_remaining > 0 or len(self.zombies) >= MAX_ZOMBIES:
            return
        spawn = ZOMBIE_SPAWNS[self.spawn_index % len(ZOMBIE_SPAWNS)]
        self.spawn_index += 1
        self.zombies.append(Zombie(spawn))
        self.spawn_time_remaining = float(ZOMBIE_SPAWN_INTERVAL)

    def _update_zombies(self, delta_time: float) -> None:
        for zombie in self.zombies:
            if not zombie.alive:
                continue
            zombie.update(delta_time, self.player, self.gate)
            zombie.attack(self.elapsed_time, self.player, self.gate)

    def _update_bullets(self, delta_time: float) -> None:
        for bullet in self.bullets:
            bullet.update(delta_time, self.world_bounds)
            if not bullet.active:
                continue
            if any(bullet.rect.colliderect(platform) for platform in self.platforms):
                bullet.active = False
                continue
            for zombie in self.zombies:
                if zombie.alive and bullet.rect.colliderect(zombie.rect):
                    zombie.take_damage(bullet.damage, self.elapsed_time)
                    bullet.active = False
                    break
        self.bullets = [bullet for bullet in self.bullets if bullet.active]

    def _remove_dead_zombies(self) -> None:
        defeated = len([zombie for zombie in self.zombies if zombie.death_animation_finished(self.elapsed_time)])
        if defeated:
            self.message = "A zombie fell."
        self.zombies = [zombie for zombie in self.zombies if not zombie.death_animation_finished(self.elapsed_time)]

    def nearby_crates(self) -> Sequence[SupplyCrate]:
        """Return unopened crates that the player can search now."""
        return tuple(crate for crate in self.crates if crate.can_search(self.player))
