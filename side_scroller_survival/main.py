"""Run the Safehouse: Night Watch side-scroller demo."""

from __future__ import annotations

import pygame

import map_data
import settings
from renderer import PUNCH_ANIMATION_DURATION, SHOOT_ANIMATION_DURATION
from renderer_registry import create_renderer_registry
from world import World


class Camera:
    """Convert world positions into screen positions."""

    def __init__(self) -> None:
        self.x = 0.0

    def update(self, player_rect: pygame.Rect) -> None:
        target_x = player_rect.centerx - settings.CAMERA_FOLLOW_X
        maximum_x = settings.WORLD_WIDTH - settings.WINDOW_WIDTH
        self.x = max(0.0, min(float(maximum_x), target_x))

    def rect(self, world_rect: pygame.Rect) -> pygame.Rect:
        return world_rect.move(-round(self.x), 0)

    def point(self, world_point: pygame.Vector2 | tuple[float, float]) -> tuple[int, int]:
        return (round(world_point[0] - self.x), round(world_point[1]))

    def world_point(self, screen_point: tuple[int, int]) -> tuple[float, float]:
        return (screen_point[0] + self.x, screen_point[1])


class Game:
    """Own the Pygame loop, input handling, drawing, and reset behavior."""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(settings.WINDOW_TITLE)
        self.screen = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)
        self.large_font = pygame.font.Font(None, 52)
        self.world = World()
        self.renderer_registry = create_renderer_registry(self.world.player.gun)
        self.camera = Camera()
        self.running = True
        self.showing_start_menu = True
        self.player_shoot_started_at = -SHOOT_ANIMATION_DURATION
        self.player_punch_started_at = -PUNCH_ANIMATION_DURATION

    def run(self) -> None:
        """Process frames until the player closes the game window."""
        while self.running:
            delta_time = min(self.clock.tick(settings.FPS) / 1000.0, 0.05)
            self._handle_events()
            self._update(delta_time)
            self._draw()
        pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif self.showing_start_menu and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._start_game()
                elif event.key == pygame.K_r:
                    self.world.reset()
                elif event.key == pygame.K_SPACE:
                    self.world.player.jump()
                elif event.key == pygame.K_e:
                    self.world.try_search()
                elif event.key == pygame.K_q:
                    self.world.switch_weapon()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.showing_start_menu:
                    if self._start_button_rect().collidepoint(event.pos):
                        self._start_game()
                else:
                    self._fire_player()

    def _update(self, delta_time: float) -> None:
        if self.showing_start_menu:
            return
        keys = pygame.key.get_pressed()
        move_direction = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        mouse_target = self.camera.world_point(pygame.mouse.get_pos())
        self.world.update_player(delta_time, move_direction, mouse_target)
        if pygame.mouse.get_pressed(3)[0]:
            self._fire_player()
        self.world.update(delta_time)
        self.camera.update(self.world.player.rect)

    def _draw(self) -> None:
        if self.showing_start_menu:
            self._draw_start_menu()
            pygame.display.flip()
            return
        background = settings.SKY_NIGHT_COLOR if self.world.is_night else settings.SKY_DAY_COLOR
        self.screen.fill(background)
        self._draw_skyline()
        self._draw_background_decals()
        self._draw_world()
        self._draw_foreground_decals()
        self._draw_hud()
        if self.world.phase in {"success", "failure"}:
            self._draw_outcome()
        pygame.display.flip()

    def _start_game(self) -> None:
        self.world.reset()
        self.camera.x = 0.0
        self.showing_start_menu = False

    def _start_button_rect(self) -> pygame.Rect:
        return pygame.Rect(settings.WINDOW_WIDTH // 2 - 150, 445, 300, 64)

    def _draw_start_menu(self) -> None:
        self.screen.fill(settings.SKY_NIGHT_COLOR)
        self._draw_skyline()
        pygame.draw.rect(
            self.screen,
            settings.GROUND_COLOR,
            (0, settings.GROUND_Y, settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT - settings.GROUND_Y),
        )
        overlay = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 85))
        self.screen.blit(overlay, (0, 0))

        self._draw_text(
            "SAFEHOUSE: NIGHT WATCH",
            (settings.WINDOW_WIDTH // 2, 250),
            self.large_font,
            settings.TEXT_COLOR,
            anchor="center",
        )
        self._draw_text(
            "Survive the night. Protect the safehouse.",
            (settings.WINDOW_WIDTH // 2, 315),
            self.font,
            settings.BULLET_COLOR,
            anchor="center",
        )
        self._draw_text(
            "Search for supplies before the zombies arrive.",
            (settings.WINDOW_WIDTH // 2, 355),
            self.small_font,
            settings.TEXT_COLOR,
            anchor="center",
        )

        button = self._start_button_rect()
        is_hovered = button.collidepoint(pygame.mouse.get_pos())
        button_color = settings.HEALTH_COLOR if is_hovered else settings.GATE_COLOR
        pygame.draw.rect(self.screen, button_color, button, border_radius=8)
        pygame.draw.rect(self.screen, settings.TEXT_COLOR, button, 2, border_radius=8)
        self._draw_text("START GAME", button.center, self.font, settings.TEXT_COLOR, anchor="center")
        self._draw_text(
            "Press Enter or click Start Game",
            (settings.WINDOW_WIDTH // 2, 550),
            self.small_font,
            settings.TEXT_COLOR,
            anchor="center",
        )

    def _draw_skyline(self) -> None:
        for index in range(-1, 9):
            left = index * 460 - int(self.camera.x * 0.18)
            height = 110 + (index % 3) * 45
            pygame.draw.rect(
                self.screen,
                settings.BUILDING_COLOR,
                (left, settings.GROUND_Y - height, 290, height),
            )

    def _draw_background_decals(self) -> None:
        """Draw static scenery that does not affect movement or collision."""
        for decal_type, world_left, world_top in map_data.BACKGROUND_DECALS:
            left = round(world_left - self.camera.x * 0.72)
            top = round(world_top)
            if decal_type == "billboard":
                self._draw_billboard(left, top)
            elif decal_type == "wrecked_vehicle":
                self._draw_wrecked_vehicle(left, top)
            elif decal_type == "road_sign":
                self._draw_road_sign(left, top)
            elif decal_type == "graffiti":
                self._draw_graffiti(left, top)
            elif decal_type == "streetlight":
                self._draw_streetlight(left, top)

    def _draw_foreground_decals(self) -> None:
        """Draw nearby scenery after game objects to create depth."""
        for decal_type, world_left, world_top in map_data.FOREGROUND_DECALS:
            left = round(world_left - self.camera.x * 1.16)
            top = round(world_top)
            if decal_type == "fence":
                self._draw_foreground_fence(left, top)
            elif decal_type == "rubble":
                self._draw_foreground_rubble(left, top)
            elif decal_type == "utility_pole":
                self._draw_utility_pole(left, top)

    def _draw_billboard(self, left: int, top: int) -> None:
        board = pygame.Rect(left, top, 146, 58)
        pygame.draw.rect(self.screen, (64, 51, 54), board, border_radius=4)
        pygame.draw.rect(self.screen, (147, 109, 56), board, 4, border_radius=4)
        pygame.draw.line(self.screen, (58, 50, 48), (left + 34, top + 58), (left + 24, settings.GROUND_Y), 7)
        pygame.draw.line(self.screen, (58, 50, 48), (left + 110, top + 58), (left + 122, settings.GROUND_Y), 7)

    def _draw_wrecked_vehicle(self, left: int, top: int) -> None:
        body = pygame.Rect(left, top, 118, 38)
        pygame.draw.rect(self.screen, (92, 62, 51), body, border_radius=10)
        pygame.draw.polygon(self.screen, (92, 62, 51), ((left + 24, top), (left + 48, top - 24), (left + 88, top - 24), (left + 105, top)))
        pygame.draw.rect(self.screen, (46, 58, 67), (left + 51, top - 19, 32, 15))
        for wheel_left in (left + 19, left + 86):
            pygame.draw.circle(self.screen, (37, 35, 36), (wheel_left, top + 37), 14)
            pygame.draw.circle(self.screen, (113, 103, 89), (wheel_left, top + 37), 5)

    def _draw_road_sign(self, left: int, top: int) -> None:
        pygame.draw.line(self.screen, (72, 71, 65), (left + 20, top + 30), (left + 20, settings.GROUND_Y), 6)
        pygame.draw.polygon(self.screen, (183, 159, 67), ((left + 20, top), (left + 47, top + 18), (left + 20, top + 36), (left - 7, top + 18)))
        pygame.draw.polygon(self.screen, (75, 64, 49), ((left + 20, top + 5), (left + 38, top + 18), (left + 20, top + 31), (left + 2, top + 18)), 3)

    def _draw_graffiti(self, left: int, top: int) -> None:
        wall = pygame.Rect(left, top, 115, 80)
        pygame.draw.rect(self.screen, (75, 68, 66), wall)
        pygame.draw.line(self.screen, (181, 70, 92), (left + 16, top + 58), (left + 40, top + 22), 7)
        pygame.draw.line(self.screen, (181, 70, 92), (left + 39, top + 22), (left + 64, top + 58), 7)
        pygame.draw.line(self.screen, (181, 70, 92), (left + 75, top + 25), (left + 99, top + 55), 7)

    def _draw_streetlight(self, left: int, top: int) -> None:
        pygame.draw.line(self.screen, (55, 59, 61), (left + 10, top + 10), (left + 10, settings.GROUND_Y), 7)
        pygame.draw.line(self.screen, (55, 59, 61), (left + 10, top + 10), (left + 40, top + 10), 6)
        pygame.draw.circle(self.screen, (232, 205, 113), (left + 42, top + 17), 8)

    def _draw_foreground_fence(self, left: int, top: int) -> None:
        for post_left in range(left, left + 152, 38):
            pygame.draw.line(self.screen, (48, 45, 41), (post_left, top), (post_left, top + 128), 7)
        pygame.draw.line(self.screen, (68, 61, 54), (left, top + 38), (left + 152, top + 64), 5)
        pygame.draw.line(self.screen, (68, 61, 54), (left, top + 78), (left + 152, top + 104), 5)

    def _draw_foreground_rubble(self, left: int, top: int) -> None:
        pygame.draw.polygon(
            self.screen,
            (57, 54, 52),
            ((left, top + 44), (left + 32, top + 8), (left + 66, top + 31), (left + 102, top + 47)),
        )
        pygame.draw.polygon(
            self.screen,
            (93, 81, 69),
            ((left + 16, top + 44), (left + 42, top + 19), (left + 69, top + 46)),
        )
        pygame.draw.rect(self.screen, (45, 44, 43), (left, top + 47, 108, 12))

    def _draw_utility_pole(self, left: int, top: int) -> None:
        pygame.draw.line(self.screen, (43, 42, 40), (left + 24, top), (left + 24, settings.GROUND_Y), 10)
        pygame.draw.line(self.screen, (48, 46, 43), (left - 20, top + 38), (left + 70, top + 38), 7)
        pygame.draw.line(self.screen, (39, 39, 39), (left - 18, top + 45), (left - 96, top + 84), 3)
        pygame.draw.line(self.screen, (39, 39, 39), (left + 67, top + 45), (left + 150, top + 76), 3)

    def _draw_world(self) -> None:
        safehouse = self.camera.rect(pygame.Rect(map_data.SAFEHOUSE_RECT))
        pygame.draw.rect(self.screen, settings.SAFEHOUSE_COLOR, safehouse)
        pygame.draw.rect(self.screen, settings.PLATFORM_EDGE_COLOR, safehouse, 3)

        for platform in self.world.platforms:
            rect = self.camera.rect(platform)
            color = (
                settings.GROUND_COLOR
                if platform.top >= settings.GROUND_Y
                else settings.PLATFORM_COLOR
            )
            pygame.draw.rect(self.screen, color, rect)
            if platform.top < settings.GROUND_Y:
                pygame.draw.line(self.screen, settings.PLATFORM_EDGE_COLOR, rect.topleft, rect.topright, 3)

        gate_rect = self.camera.rect(self.world.gate.rect)
        pygame.draw.rect(self.screen, settings.GATE_COLOR, gate_rect)
        pygame.draw.rect(self.screen, settings.PLATFORM_EDGE_COLOR, gate_rect, 2)

        for crate in self.world.crates:
            crate_rect = self.camera.rect(crate.rect)
            color = settings.CRATE_OPEN_COLOR if crate.opened else settings.CRATE_COLOR
            pygame.draw.rect(self.screen, color, crate_rect)
            pygame.draw.rect(self.screen, settings.SHADOW_COLOR, crate_rect, 2)
            if crate.can_search(self.world.player):
                self._draw_text("E Search", crate_rect.midtop, self.small_font, settings.TEXT_COLOR, anchor="midbottom")

        for bullet in self.world.bullets:
            self.renderer_registry.bullet.draw(self.screen, self.camera.point(bullet.position), bullet.velocity)

        for zombie in self.world.zombies:
            rect = self.camera.rect(zombie.rect)
            self.renderer_registry.zombie.draw(self.screen, zombie, rect, self.world.elapsed_time)
            if zombie.alive:
                self._draw_health_bar(rect, zombie.health, zombie.max_health, 5)

        self.renderer_registry.player.draw(
            self.screen,
            self.world.player,
            self.camera.rect(self.world.player.rect),
            self.player_shoot_started_at,
            self.player_punch_started_at,
        )
        player_rect = self.camera.rect(self.world.player.rect)
        self._draw_health_bar(player_rect, self.world.player.health, self.world.player.max_health, 6)

    def _draw_hud(self) -> None:
        panel = pygame.Rect(14, 14, 490, 118)
        pygame.draw.rect(self.screen, settings.HUD_COLOR, panel, border_radius=8)
        pygame.draw.rect(self.screen, settings.TEXT_COLOR, panel, 2, border_radius=8)
        phase = self.world.phase.upper()
        self._draw_text(f"{phase}  {self.world.time_remaining:04.1f}s", (28, 27), self.font, settings.TEXT_COLOR)
        inventory = self.world.resources
        self._draw_text(
            f"Health {self.world.player.health}/{self.world.player.max_health}    "
            f"Gate {self.world.gate.health}/{self.world.gate.max_health}",
            (28, 56),
            self.small_font,
            settings.TEXT_COLOR,
        )
        self._draw_text(
            f"Ammo {inventory['ammo']}   Food {inventory['food']}   Boards {inventory['boards']}   "
            f"Weapon {self.world.player.weapon_state.upper()}",
            (28, 82),
            self.small_font,
            settings.TEXT_COLOR,
        )
        self._draw_text(self.world.message, (28, 106), self.small_font, settings.BULLET_COLOR)
        hint = "A/D move  Space jump  E search  Q switch weapon  Click shoot  R restart  Esc quit"
        self._draw_text(
            hint,
            (settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT - 20),
            self.small_font,
            settings.TEXT_COLOR,
            anchor="midbottom",
        )

    def _draw_outcome(self) -> None:
        overlay = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        title = "SAFEHOUSE SURVIVED" if self.world.phase == "success" else "SAFEHOUSE LOST"
        color = settings.HEALTH_COLOR if self.world.phase == "success" else settings.DAMAGE_COLOR
        self._draw_text(title, (settings.WINDOW_WIDTH // 2, 290), self.large_font, color, anchor="center")
        self._draw_text(
            self.world.message,
            (settings.WINDOW_WIDTH // 2, 345),
            self.font,
            settings.TEXT_COLOR,
            anchor="center",
        )
        self._draw_text(
            "Press R to start again",
            (settings.WINDOW_WIDTH // 2, 390),
            self.font,
            settings.TEXT_COLOR,
            anchor="center",
        )

    def _fire_player(self) -> None:
        self.world.player.aim(self.camera.world_point(pygame.mouse.get_pos()))
        if self.world.player.has_ranged_weapon and self.world.fire() is not None:
            self.player_shoot_started_at = pygame.time.get_ticks()
        elif not self.world.player.has_ranged_weapon and self.world.melee_attack() is not None:
            self.player_punch_started_at = pygame.time.get_ticks()

    def _draw_health_bar(self, rect: pygame.Rect, health: int, maximum: int, height: int) -> None:
        bar = pygame.Rect(rect.left, rect.top - height - 4, rect.width, height)
        pygame.draw.rect(self.screen, settings.DAMAGE_COLOR, bar)
        ratio = 0 if maximum <= 0 else max(0.0, health / maximum)
        pygame.draw.rect(self.screen, settings.HEALTH_COLOR, (bar.left, bar.top, round(bar.width * ratio), bar.height))

    def _draw_text(
        self,
        value: str,
        position: tuple[int, int],
        font: pygame.font.Font,
        color: tuple[int, int, int],
        anchor: str = "topleft",
    ) -> None:
        text = font.render(value, True, color)
        text_rect = text.get_rect()
        setattr(text_rect, anchor, position)
        self.screen.blit(text, text_rect)


if __name__ == "__main__":
    Game().run()
