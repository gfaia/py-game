import pygame as pg
import os
from settings import *
from sprites import Player, Cursor, Mob, Obstacle
from map import Camera, TiledMap


class Game:

    version = 'Tilemap v1.4.1'
    author = 'Gfaia'
    date = '2018.4.12'

    def __init__(self):
        """initialize game window, etc."""
        pg.init()
        pg.mixer.init()
        pg.display.set_caption(self.version)
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))

        self.clock = pg.time.Clock()
        self.running = True
        self.debug = False
        self.fps = FPS

        self.font = pg.font.match_font("Consolas", 15)

        self.load_data()
        self.new()

    def load_data(self):

        self.project_dir = os.path.dirname(__file__)
        self.assets_dir = os.path.join(
            self.project_dir, "assets")

        self.maps_dir = os.path.join(
            self.assets_dir, "Maps")
        self.map = TiledMap(os.path.join(
            self.maps_dir, "level1.tmx"))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()

        self.png_path = os.path.join(
            self.assets_dir, "PNG")

        # player image
        self.player_img_path = os.path.join(
            self.png_path, "Man Blue", "manBlue_gun.png")
        self.player_img = pg.image.load(
            self.player_img_path)

        # mobs image path
        self.mob_img_path = os.path.join(
            self.png_path, "Zombie 1", "zoimbie1_hold.png")
        self.mob_img = pg.image.load(
            self.mob_img_path)

    def new(self):
        """Initialize the contains of objects in game."""
        self.all_sprites = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.obstacles = pg.sprite.Group()

        for tile_object in self.map.tmxdata.objects:
            if tile_object.name == 'Player':
                self.player = Player(self, tile_object.x, tile_object.y,
                                     tile_object.width, tile_object.height)
                self.all_sprites.add(self.player)
            if tile_object.name == 'Zombie':
                mob = Mob(self, tile_object.x, tile_object.y,
                          tile_object.width, tile_object.height)
                self.all_sprites.add(mob)
            if tile_object.name == 'Wall':
                Obstacle(self, tile_object.x, tile_object.y,
                         tile_object.width, tile_object.height)
            if tile_object.name == 'Tree':
                Obstacle(self, tile_object.x, tile_object.y,
                         tile_object.width, tile_object.height)
            if tile_object.name == 'Sofa':
                Obstacle(self, tile_object.x, tile_object.y,
                         tile_object.width, tile_object.height)

        # self.all_sprites.add(self.player)
        self.cursor = Cursor(self, WHITE, 2)
        self.camera = Camera(self, WIDTH, HEIGHT)

    def run(self):
        """Game loop."""
        while self.running:
            self.clock.tick(self.fps)
            self.events()
            self.update()
            self.draw()
        pg.quit()

    def update(self):
        """Update the state of the game."""
        self.all_sprites.update()
        self.cursor.update()
        self.camera.update(self.player)

        # collusion detection
        bullets_with_obstacles = pg.sprite.groupcollide(
            self.bullets, self.obstacles, True, False)

    def events(self):
        """Global events."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.running = False
                if event.key == pg.K_o:
                    self.debug = ~ self.debug

    def draw_grid(self):
        """Draw the lines."""
        for x in range(0, WIDTH, TILE_SIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILE_SIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def draw(self):
        """Main draw function."""
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))

        for s in self.all_sprites:
            if isinstance(s, Mob):
                s.draw_health_bar()
            if isinstance(s, Player):
                s.draw_health_bar()
            self.screen.blit(s.image, self.camera.apply(s))
            if self.debug:
                if isinstance(s, Player) or isinstance(s, Mob):
                    pg.draw.rect(self.screen, LIGHTGREY,
                                 self.camera.apply_hit_rect(s.hit_rect), 1)

        if self.debug:
            for w in self.obstacles:
                pg.draw.rect(self.screen, LIGHTGREY,
                             self.camera.apply_rect(w.rect), 1)
            self.draw_debug()

        self.cursor.draw()
        pg.display.flip()

    def draw_debug(self):

        # draw the position of object
        self.draw_text("Player", 20, 50, 20)
        self.draw_text(str(self.player.l_pos), 20, 50, 60)
        self.draw_text(str(self.player.g_pos), 20, 50, 100)

    def draw_text(self, text, size, x, y):
        """Draw the text in the screen."""
        font = pg.font.Font(self.font, size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)


if __name__ == "__main__":
    g = Game()
    g.run()
