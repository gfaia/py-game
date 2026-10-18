import pygame as pg

from map_data import MAP_ROWS
from settings import (
    BACKGROUND_COLOR,
    BOILER_COLOR,
    DAMAGE_COLOR,
    ENEMY_COLOR,
    FLOOR_COLOR,
    FPS,
    GRID_COLOR,
    HEALTH_COLOR,
    HUD_COLOR,
    MOVE_KEYS,
    NPC_COLOR,
    PIPE_COLOR,
    PLAYER_COLOR,
    TEXT_COLOR,
    TILE_SIZE,
    WALL_COLOR,
    WALL_EDGE_COLOR,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
)
from world import World


class Game:
    def __init__(self):
        pg.init()
        pg.display.set_caption(WINDOW_TITLE)
        self.screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pg.time.Clock()
        self.font = pg.font.Font(None, 28)
        self.small_font = pg.font.Font(None, 22)
        self.title_font = pg.font.Font(None, 72)
        self.world = World()
        self.running = True
        self.in_menu = True
        self.selected_menu_index = 0

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.draw()
        pg.quit()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                self.handle_key(event.key)
            elif event.type == pg.MOUSEMOTION and self.in_menu:
                self.select_menu_option(event.pos)
            elif event.type == pg.MOUSEBUTTONDOWN and self.in_menu and event.button == 1:
                self.activate_menu_option(event.pos)

    def handle_key(self, key):
        if self.in_menu:
            self.handle_menu_key(key)
            return
        key_deltas = {
            pg.K_LEFT: MOVE_KEYS["left"],
            pg.K_a: MOVE_KEYS["left"],
            pg.K_RIGHT: MOVE_KEYS["right"],
            pg.K_d: MOVE_KEYS["right"],
            pg.K_UP: MOVE_KEYS["up"],
            pg.K_w: MOVE_KEYS["up"],
            pg.K_DOWN: MOVE_KEYS["down"],
            pg.K_s: MOVE_KEYS["down"],
        }
        if key == pg.K_ESCAPE:
            self.running = False
        elif key == pg.K_r:
            self.world.reset()
        elif key == pg.K_e:
            self.world.interact()
        elif key == pg.K_SPACE:
            self.world.attack_enemy()
        elif key in key_deltas:
            self.world.move_player(key_deltas[key])

    def handle_menu_key(self, key):
        if key == pg.K_ESCAPE:
            self.running = False
        elif key in {pg.K_UP, pg.K_w}:
            self.selected_menu_index = (self.selected_menu_index - 1) % len(self.menu_options())
        elif key in {pg.K_DOWN, pg.K_s}:
            self.selected_menu_index = (self.selected_menu_index + 1) % len(self.menu_options())
        elif key in {pg.K_RETURN, pg.K_KP_ENTER}:
            self.activate_selected_menu_option()

    def menu_options(self):
        return ("Start Game", "Quit")

    def menu_option_rects(self):
        button_width = 280
        button_height = 58
        button_left = (WINDOW_WIDTH - button_width) // 2
        button_top = 330
        return [
            pg.Rect(button_left, button_top + index * 76, button_width, button_height)
            for index in range(len(self.menu_options()))
        ]

    def select_menu_option(self, position):
        for index, rect in enumerate(self.menu_option_rects()):
            if rect.collidepoint(position):
                self.selected_menu_index = index
                return

    def activate_menu_option(self, position):
        for index, rect in enumerate(self.menu_option_rects()):
            if rect.collidepoint(position):
                self.selected_menu_index = index
                self.activate_selected_menu_option()
                return

    def activate_selected_menu_option(self):
        if self.selected_menu_index == 0:
            self.world.reset()
            self.in_menu = False
        else:
            self.running = False

    def draw(self):
        if self.in_menu:
            self.draw_menu()
            pg.display.flip()
            return
        self.screen.fill(BACKGROUND_COLOR)
        self.draw_map()
        self.draw_entities()
        self.draw_hud()
        pg.display.flip()

    def draw_menu(self):
        self.screen.fill(BACKGROUND_COLOR)
        center_x = WINDOW_WIDTH // 2
        pg.draw.circle(self.screen, BOILER_COLOR, (center_x, 175), 76)
        pg.draw.circle(self.screen, PIPE_COLOR, (center_x, 175), 76, 8)
        pg.draw.circle(self.screen, HUD_COLOR, (center_x, 175), 34)
        self.draw_centered_text("BRASS STATION", center_x, 72, self.title_font)
        self.draw_centered_text("A clockwork expedition", center_x, 260, self.font)

        for index, (label, rect) in enumerate(zip(self.menu_options(), self.menu_option_rects())):
            is_selected = index == self.selected_menu_index
            fill_color = PIPE_COLOR if is_selected else HUD_COLOR
            border_color = TEXT_COLOR if is_selected else WALL_EDGE_COLOR
            pg.draw.rect(self.screen, fill_color, rect, border_radius=8)
            pg.draw.rect(self.screen, border_color, rect, 3, border_radius=8)
            self.draw_centered_text(label, rect.centerx, rect.centery - 12, self.font)

        self.draw_centered_text("Use arrows, W/S, Enter, or the mouse", center_x, 510, self.small_font)
        self.draw_centered_text("Esc: quit", center_x, 540, self.small_font)

    def draw_map(self):
        for row, map_row in enumerate(MAP_ROWS):
            for column, terrain in enumerate(map_row):
                rect = pg.Rect(column * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if terrain == "#":
                    pg.draw.rect(self.screen, WALL_COLOR, rect)
                    pg.draw.rect(self.screen, WALL_EDGE_COLOR, rect, 3)
                else:
                    pg.draw.rect(self.screen, FLOOR_COLOR, rect)
                    if terrain == "=":
                        pg.draw.line(self.screen, PIPE_COLOR, rect.midleft, rect.midright, 10)
                        pg.draw.circle(self.screen, PIPE_COLOR, rect.center, 8)
                    elif terrain == "B":
                        pg.draw.circle(self.screen, BOILER_COLOR, rect.center, TILE_SIZE // 3)
                        pg.draw.circle(self.screen, PIPE_COLOR, rect.center, TILE_SIZE // 3, 3)
                pg.draw.rect(self.screen, GRID_COLOR, rect, 1)

    def draw_entities(self):
        self.draw_entity(self.world.player, PLAYER_COLOR, "P")
        self.draw_entity(self.world.mechanic, NPC_COLOR, "A")
        if self.world.sentinel.alive:
            self.draw_entity(self.world.sentinel, ENEMY_COLOR, "S")

    def draw_entity(self, entity, color, label):
        column, row = entity.position
        center = (column * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2)
        pg.draw.circle(self.screen, color, center, TILE_SIZE // 3)
        text = self.small_font.render(label, True, TEXT_COLOR)
        text_rect = text.get_rect(center=center)
        self.screen.blit(text, text_rect)

    def draw_hud(self):
        top = len(MAP_ROWS) * TILE_SIZE
        hud_rect = pg.Rect(0, top, WINDOW_WIDTH, WINDOW_HEIGHT - top)
        pg.draw.rect(self.screen, HUD_COLOR, hud_rect)
        self.draw_health_bar(20, top + 18)
        self.draw_text(self.world.quest_label(), 20, top + 55, self.small_font)
        self.draw_text(self.world.message, 20, top + 82, self.small_font)
        self.draw_text("Arrows or WASD: move   E: talk   Space: attack   R: restart   Esc: quit", 20, top + 112, self.small_font)

    def draw_health_bar(self, left, top):
        self.draw_text("Health", left, top, self.small_font)
        bar_rect = pg.Rect(left + 72, top + 4, 180, 18)
        pg.draw.rect(self.screen, DAMAGE_COLOR, bar_rect)
        health_width = int(bar_rect.width * self.world.player.health / self.world.player.max_health)
        pg.draw.rect(self.screen, HEALTH_COLOR, (bar_rect.left, bar_rect.top, health_width, bar_rect.height))
        pg.draw.rect(self.screen, TEXT_COLOR, bar_rect, 2)
        self.draw_text(f"{self.world.player.health}/{self.world.player.max_health}", left + 262, top, self.small_font)

    def draw_text(self, value, left, top, font):
        surface = font.render(value, True, TEXT_COLOR)
        self.screen.blit(surface, (left, top))

    def draw_centered_text(self, value, center_x, top, font):
        surface = font.render(value, True, TEXT_COLOR)
        text_rect = surface.get_rect(midtop=(center_x, top))
        self.screen.blit(surface, text_rect)


if __name__ == "__main__":
    Game().run()
