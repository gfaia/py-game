import random

import pygame as pg


WIDTH, HEIGHT = 1100, 700
WORLD_WIDTH, WORLD_HEIGHT = 2600, 1800
DAY_LENGTH, NIGHT_LENGTH = 75, 45
GRASS, NIGHT_GRASS, GRID = (59, 92, 57), (27, 43, 39), (76, 112, 68)
BASE_COLOR, TEXT, ZOMBIE, PLAYER = (72, 102, 118), (238, 241, 229), (143, 184, 92), (241, 190, 91)
RESOURCE_COLORS = {"food": (214, 163, 74), "parts": (122, 177, 202), "medicine": (220, 93, 93)}


def clamp(value, low, high):
    return max(low, min(high, value))


class Game:
    def __init__(self):
        pg.init()
        pg.display.set_caption("Last Light: Base Defense")
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()
        self.font = pg.font.Font(None, 26)
        self.small_font = pg.font.Font(None, 21)
        self.title_font = pg.font.Font(None, 42)
        self.running = True
        self.reset()

    def reset(self):
        self.day, self.phase, self.phase_time = 1, "day", DAY_LENGTH
        self.player = pg.Vector2(WORLD_WIDTH / 2, WORLD_HEIGHT / 2 + 120)
        self.player_health, self.base_health = 100, 100
        self.food, self.parts, self.medicine = 4, 3, 1
        self.survivors, self.ammo, self.base_level = 1, 60, 1
        self.message, self.message_time = "Search the ruins before night falls.", 5
        self.zombies, self.bullets = [], []
        self.resources = self.make_resources()
        self.survivors_on_map = [{"pos": self.random_point(400), "name": name} for name in ("Mia", "Noah", "Iris")]
        self.trees = [self.random_point(160) for _ in range(85)]

    def random_point(self, base_distance):
        while True:
            point = pg.Vector2(random.randint(80, WORLD_WIDTH - 80), random.randint(80, WORLD_HEIGHT - 80))
            if point.distance_to((WORLD_WIDTH / 2, WORLD_HEIGHT / 2)) > base_distance:
                return point

    def make_resources(self):
        return [{"pos": self.random_point(260), "kind": kind} for kind, count in (("food", 7), ("parts", 6), ("medicine", 4)) for _ in range(count)]

    def camera(self):
        return pg.Vector2(clamp(self.player.x - WIDTH / 2, 0, WORLD_WIDTH - WIDTH), clamp(self.player.y - HEIGHT / 2, 0, WORLD_HEIGHT - HEIGHT))

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.running = False
                elif event.key == pg.K_r:
                    self.reset()
                elif event.key == pg.K_e:
                    self.interact()
                elif event.key == pg.K_b:
                    self.upgrade_base()
                elif event.key == pg.K_n and self.phase == "day":
                    self.start_night()
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                self.shoot(event.pos)

    def move_player(self, delta, seconds):
        if self.phase != "day" or self.player_health <= 0:
            return
        direction = pg.Vector2(delta)
        if direction.length_squared():
            candidate = self.player + direction.normalize() * 260 * seconds
            candidate.x, candidate.y = clamp(candidate.x, 25, WORLD_WIDTH - 25), clamp(candidate.y, 25, WORLD_HEIGHT - 25)
            if not any(candidate.distance_to(tree) < 34 for tree in self.trees):
                self.player = candidate

    def interact(self):
        if self.phase != "day":
            return self.notice("You cannot search during the attack.")
        item = min(self.resources, key=lambda entry: self.player.distance_to(entry["pos"]), default=None)
        if item and self.player.distance_to(item["pos"]) < 55:
            self.resources.remove(item)
            setattr(self, item["kind"], getattr(self, item["kind"]) + (1 if item["kind"] == "medicine" else 2))
            return self.notice(f"Collected {item['kind']}.")
        survivor = min(self.survivors_on_map, key=lambda entry: self.player.distance_to(entry["pos"]), default=None)
        if survivor and self.player.distance_to(survivor["pos"]) < 65:
            self.survivors_on_map.remove(survivor)
            self.survivors, self.ammo = self.survivors + 1, self.ammo + 12
            return self.notice(f"{survivor['name']} joined the base. +12 ammo")
        if self.player.distance_to((WORLD_WIDTH / 2, WORLD_HEIGHT / 2)) < 155:
            if self.medicine and self.player_health < 100:
                self.medicine -= 1
                self.player_health = min(100, self.player_health + 35)
                return self.notice("You used medicine.")
            return self.notice("At base. Press B to reinforce it.")
        self.notice("Move closer to supplies or a survivor.")

    def upgrade_base(self):
        if self.phase != "day" or self.player.distance_to((WORLD_WIDTH / 2, WORLD_HEIGHT / 2)) > 180:
            return self.notice("Stand at the base to reinforce it.")
        if self.parts < 4:
            return self.notice("A wall upgrade needs 4 parts.")
        self.parts -= 4
        self.base_level += 1
        self.base_health = min(100, self.base_health + 25)
        self.notice("The base walls are stronger.")

    def shoot(self, screen_position):
        if self.phase != "night" or self.ammo <= 0 or self.player_health <= 0:
            return
        direction = pg.Vector2(screen_position) + self.camera() - self.player
        if direction.length_squared():
            self.ammo -= 1
            self.bullets.append({"pos": self.player.copy(), "velocity": direction.normalize() * 780, "life": 1.1})

    def start_night(self):
        self.phase, self.phase_time = "night", NIGHT_LENGTH
        self.player = pg.Vector2(WORLD_WIDTH / 2, WORLD_HEIGHT / 2 + 125)
        self.zombies = []
        for _ in range(10 + self.day * 4):
            edge = random.choice(("top", "bottom", "left", "right"))
            if edge == "top": position = pg.Vector2(random.randrange(WORLD_WIDTH), -20)
            elif edge == "bottom": position = pg.Vector2(random.randrange(WORLD_WIDTH), WORLD_HEIGHT + 20)
            elif edge == "left": position = pg.Vector2(-20, random.randrange(WORLD_HEIGHT))
            else: position = pg.Vector2(WORLD_WIDTH + 20, random.randrange(WORLD_HEIGHT))
            self.zombies.append({"pos": position, "health": 2 + self.day // 3, "hit": 0})
        self.notice(f"Night {self.day}: defend the base.")

    def finish_night(self):
        if self.base_health <= 0 or self.player_health <= 0:
            return self.notice("The base fell. Press R to begin again.", 999)
        self.day += 1
        self.phase, self.phase_time = "day", DAY_LENGTH
        food_cost = max(1, self.survivors // 2)
        self.food = max(0, self.food - food_cost)
        self.ammo += 8 + self.survivors * 3
        self.resources.extend(self.make_resources()[:7])
        self.notice(f"Morning {self.day}. The base used {food_cost} food.")

    def update(self, seconds):
        if self.message_time > 0:
            self.message_time -= seconds
        keys = pg.key.get_pressed()
        self.move_player((keys[pg.K_d] - keys[pg.K_a], keys[pg.K_s] - keys[pg.K_w]), seconds)
        if self.base_health <= 0 or self.player_health <= 0:
            return
        self.phase_time -= seconds
        if self.phase == "day" and self.phase_time <= 0:
            self.start_night()
        elif self.phase == "night":
            self.update_night(seconds)
            if self.phase_time <= 0 or not self.zombies:
                self.finish_night()

    def update_night(self, seconds):
        for bullet in self.bullets[:]:
            bullet["pos"] += bullet["velocity"] * seconds
            bullet["life"] -= seconds
            if bullet["life"] <= 0:
                self.bullets.remove(bullet)
                continue
            for zombie in self.zombies[:]:
                if bullet["pos"].distance_to(zombie["pos"]) < 24:
                    zombie["health"] -= 1
                    self.bullets.remove(bullet)
                    if zombie["health"] <= 0:
                        self.zombies.remove(zombie)
                        self.ammo += 1
                    break
        base = pg.Vector2(WORLD_WIDTH / 2, WORLD_HEIGHT / 2)
        for zombie in self.zombies:
            direction = base - zombie["pos"]
            if direction.length_squared():
                zombie["pos"] += direction.normalize() * (33 + self.day * 1.5) * seconds
            if zombie["pos"].distance_to(base) < 118 and zombie["hit"] <= 0:
                self.base_health = max(0, self.base_health - max(1, 4 - self.base_level))
                zombie["hit"] = 1.2
            zombie["hit"] -= seconds

    def notice(self, text, duration=3):
        self.message, self.message_time = text, duration

    def draw(self):
        camera = self.camera()
        self.screen.fill(NIGHT_GRASS if self.phase == "night" else GRASS)
        for x in range(0, WORLD_WIDTH + 1, 100):
            pg.draw.line(self.screen, GRID, (x - camera.x, -camera.y), (x - camera.x, WORLD_HEIGHT - camera.y), 1)
        for y in range(0, WORLD_HEIGHT + 1, 100):
            pg.draw.line(self.screen, GRID, (-camera.x, y - camera.y), (WORLD_WIDTH - camera.x, y - camera.y), 1)
        base = pg.Vector2(WORLD_WIDTH / 2, WORLD_HEIGHT / 2) - camera
        pg.draw.circle(self.screen, BASE_COLOR, base, 122 + self.base_level * 5)
        pg.draw.circle(self.screen, TEXT, base, 122 + self.base_level * 5, 3)
        self.label("BASE", base + (0, -15), self.small_font)
        for tree in self.trees:
            point = tree - camera
            pg.draw.circle(self.screen, (32, 64, 37), point, 20)
            pg.draw.circle(self.screen, (48, 82, 44), point + (4, -4), 16)
        if self.phase == "day":
            for item in self.resources:
                point = item["pos"] - camera
                pg.draw.rect(self.screen, RESOURCE_COLORS[item["kind"]], (point.x - 13, point.y - 11, 26, 22), border_radius=4)
            for survivor in self.survivors_on_map:
                point = survivor["pos"] - camera
                pg.draw.circle(self.screen, (237, 226, 190), point, 15)
                self.label("!", point + (0, -31), self.font)
        for bullet in self.bullets:
            pg.draw.circle(self.screen, (255, 244, 142), bullet["pos"] - camera, 4)
        for zombie in self.zombies:
            point = zombie["pos"] - camera
            pg.draw.circle(self.screen, ZOMBIE, point, 15)
            pg.draw.rect(self.screen, (83, 31, 31), (point.x - 14, point.y - 25, 28, 5))
            pg.draw.rect(self.screen, (125, 216, 104), (point.x - 14, point.y - 25, 28 * zombie["health"] / (2 + self.day // 3), 5))
        pg.draw.circle(self.screen, PLAYER, self.player - camera, 17)
        pg.draw.circle(self.screen, TEXT, self.player - camera, 17, 2)
        self.draw_hud()
        pg.display.flip()

    def draw_hud(self):
        panel = pg.Rect(12, 12, 440, 132)
        pg.draw.rect(self.screen, (17, 25, 28), panel, border_radius=10)
        pg.draw.rect(self.screen, TEXT, panel, 2, border_radius=10)
        phase = "DAY: EXPLORE" if self.phase == "day" else "NIGHT: DEFEND"
        self.text(f"DAY {self.day}  |  {phase}  |  {max(0, self.phase_time):04.1f}s", 25, 24, self.title_font)
        self.text(f"Base {self.base_health}/100    Health {self.player_health}/100    Ammo {self.ammo}", 25, 70, self.font)
        self.text(f"Food {self.food}    Parts {self.parts}    Medicine {self.medicine}    Survivors {self.survivors}", 25, 100, self.font)
        if self.message_time > 0:
            surface = self.font.render(self.message, True, TEXT)
            box = surface.get_rect(midbottom=(WIDTH // 2, HEIGHT - 20)).inflate(24, 16)
            pg.draw.rect(self.screen, (17, 25, 28), box, border_radius=7)
            self.screen.blit(surface, surface.get_rect(center=box.center))
        self.text("WASD move | E collect/rescue/heal | B reinforce | N begin night | Click fire | R restart", 15, HEIGHT - 25, self.small_font)

    def text(self, value, left, top, font):
        self.screen.blit(font.render(value, True, TEXT), (left, top))

    def label(self, value, center, font):
        surface = font.render(value, True, TEXT)
        self.screen.blit(surface, surface.get_rect(center=center))

    def run(self):
        while self.running:
            seconds = self.clock.tick(60) / 1000
            self.handle_events()
            self.update(seconds)
            self.draw()
        pg.quit()


if __name__ == "__main__":
    Game().run()
