import pygame as pg
from sprits import Platform, Player


class Constants:

    # Colors
    white = 255, 255, 255
    black = 0, 0, 0
    blue = 0, 0, 200
    yellow = 255, 255, 0
    green = 0, 255, 0
    lightgrey = 100, 100, 100

    # Directions
    up = 0
    down = 1
    left = 2
    right = 3


class Settings:

    # The basic information
    author = "Gfaia"
    version = "Jumper v1.4"
    date = "2018.8.21"

    # Common settings for game.
    width, height = 400, 600
    fps = 60
    background_color = Constants.black

    grid_size = 20
    grid_width = width / grid_size
    grid_height = height / grid_size
    grid_color = Constants.lightgrey

    # Font settings
    font_face = "Consolas"
    font_size = 15
    font_color = Constants.white


class Game(object):
    def __init__(self):

        """initialize game window, etc."""
        pg.init()
        pg.mixer.init()
        pg.display.set_caption(Settings.version)
        self.screen = pg.display.set_mode((Settings.width, Settings.height))

        self.clock = pg.time.Clock()
        self.running = True
        self.debug = False
        self.fps = Settings.fps

        self.font = pg.font.match_font(Settings.font_face, Settings.font_size)

        self.new()

    def new(self):
        self.all_sprites = pg.sprite.Group()
        self.player = Player(self)
        self.all_sprites.add(self.player)

        self.platforms = pg.sprite.Group()
        self.platform = Platform(100, 500, 300, 20)
        self.platforms.add(self.platform)

    def run(self):
        """Game loop."""
        self.clock.tick(self.fps)
        while self.running:
            self.events()
            self.update()
            self.draw()
        pg.quit()

    def events(self):
        """User's events."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.running = False
                if event.key == pg.K_o:
                    self.debug = ~self.debug

    def update(self):
        """Update the state of the game."""
        self.all_sprites.update()
        self.platforms.update()

    def draw(self):
        """Main draw function."""
        self.screen.fill(Settings.background_color)

        for x in range(0, Settings.width, Settings.grid_size):
            pg.draw.line(self.screen, Settings.grid_color, (x, 0), (x, Settings.height))
        for y in range(0, Settings.height, Settings.grid_size):
            pg.draw.line(self.screen, Settings.grid_color, (0, y), (Settings.width, y))

        self.all_sprites.draw(self.screen)
        self.platforms.draw(self.screen)

        pg.display.flip()


if __name__ == "__main__":
    g = Game()
    g.run()
