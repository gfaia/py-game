import pygame as pg
import os
from settings import *
from sprites import Player, Mob


class Game:

    version = "air-shooter v1.2"
    author = "Gfaia"
    date = "2018.2.24"

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

        self.score = 0

        self.load_data()
        self.new()

    def load_data(self):

        self.project_dir = os.path.dirname(__file__)
        self.assets_dir = os.path.join(self.project_dir, "assets")
        self.sounds_dir = os.path.join(self.assets_dir, "Sounds")
        self.images_dir = os.path.join(self.assets_dir, "PNG")

        # background
        self.background = pg.image.load(os.path.join(self.assets_dir, "Backgrounds", "starry.png"))
        self.background_rect = self.background.get_rect()

        # sound
        self.mob_explosion_sound = pg.mixer.Sound(os.path.join(self.sounds_dir, "explosion1.wav"))

        # player image
        self.player_image = pg.image.load(os.path.join(self.images_dir, "Players", "playerShip1_blue.png"))
        # player shooter sound
        self.shooter_sound_path = os.path.join(self.sounds_dir, "laser_shoot1.wav")
        self.shooter_sound = pg.mixer.Sound(self.shooter_sound_path)

        # bullet image
        self.bullet_image = pg.image.load(os.path.join(self.images_dir, "Lasers", "laserBlue01.png"))

        # mobs image path
        self.mob_dir = os.path.join(self.images_dir, "Meteors")
        self.mob_list = os.listdir(self.mob_dir)

        # mon explosion sound
        self.exp_sound_path = os.path.join(self.sounds_dir, "explosion1.wav")
        self.exp_sound = pg.mixer.Sound(self.exp_sound_path)

        # explosion animation
        self.exp_dir = os.path.join(self.images_dir, "Explosion_meteor")
        self.exp_list = os.listdir(self.exp_dir)

    def create_mob(self):
        """Create the mob"""
        m = Mob(self)
        self.mobs.add(m)
        self.all_sprites.add(m)

    def new(self):
        """Initialize the contains of objects in game."""
        self.all_sprites = pg.sprite.Group()

        self.player = Player(self)
        self.all_sprites.add(self.player)

        self.bullets = pg.sprite.Group()

        self.mobs = pg.sprite.Group()

        for i in range(8):
            self.create_mob()

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

    def events(self):
        """Global events."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.running = False
                if event.key == pg.K_o:
                    self.debug = ~self.debug

    def draw(self):
        """Main draw function."""
        self.screen.fill(BLACK)
        self.screen.blit(self.background, self.background_rect)
        self.all_sprites.draw(self.screen)
        # self.draw_debug()
        self.draw_text(str(self.score), 18, WIDTH / 2, 10)
        self.draw_player_shield_bar(20, 20)
        pg.display.flip()

    def draw_debug(self):
        pass

    def draw_text(self, text, size, x, y):
        """Draw the text in the screen."""
        font = pg.font.Font(self.font, size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)

    def draw_player_shield_bar(self, x, y):
        """Draw the bar of player shield"""
        pct = self.player.shields
        if pct < 0:
            pct = 0
        bar_length = 100
        bar_height = 10
        fill = (pct / 100) * bar_length
        outline_rect = pg.Rect(x, y, bar_length, bar_height)
        fill_rect = pg.Rect(x, y, fill, bar_height)
        pg.draw.rect(self.screen, GREEN, fill_rect)
        pg.draw.rect(self.screen, WHITE, outline_rect, 2)


if __name__ == "__main__":
    g = Game()
    g.run()
