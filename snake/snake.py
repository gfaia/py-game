"""A very simple snake game."""
import pygame as pg
import random
import os
import sys


class Constants:

    # Colors
    white = 255, 255, 255
    black = 0, 0, 0
    blue = 0, 0, 200
    yellow = 255, 255, 0
    green = 0, 255, 0
    lightgrey= 100, 100, 100

    # Directions
    up = 0
    down = 1
    left = 2
    right = 3


class Settings:

    # The basic information
    author = 'Gfaia'
    version = 'Snaker v1.3'
    date = '2018.8.19'

    # Common settings for game.
    width, height = 400, 400
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
    font_x = width / 2 - 20
    font_y = 10

    # Snake settings
    snake_color = Constants.blue
    snake_init_length = 4
    snake_move_feq = 10

    # Food settings
    food_nums = 1
    food_color = Constants.yellow


def random_locate():
    x = random.randint(0, Settings.grid_width - 1)
    y = random.randint(0, Settings.grid_height - 1)
    return x, y


class SnakeBodyPart(object):

    def __init__(self, screen, pos, dir, color):
        self.screen = screen
        self.dir = dir
        self.color = color
        self.grid_size = Settings.grid_size
        self.width, self.height = self.grid_size, self.grid_size

        x = (pos[0] + Settings.grid_width) % Settings.grid_width
        y = (pos[1] + Settings.grid_height) % Settings.grid_height
        self.x = x * self.grid_size
        self.y = y * self.grid_size
        self.pos = x, y

        self.prior_part = None
        self.next_part = None

    def update(self):

        if self.dir == 0:
            pos = (self.pos[0], self.pos[1] - 1)
        if self.dir == 1:
            pos = (self.pos[0], self.pos[1] + 1)
        if self.dir == 2:
            pos = (self.pos[0] - 1, self.pos[1])
        if self.dir == 3:
            pos = (self.pos[0] + 1, self.pos[1])

        x = (pos[0] + Settings.grid_width) % Settings.grid_width
        y = (pos[1] + Settings.grid_height) % Settings.grid_height
        self.x = x * self.grid_size
        self.y = y * self.grid_size
        self.pos = x, y

    def draw(self):
        rect_size = (self.x, self.y, self.width, self.height)
        pg.draw.rect(self.screen, self.color, rect_size, 0)

    def duplicate_prior(self):
        if self.prior_part:
            pos = self.prior_part.pos
            x = (pos[0] + Settings.grid_width) % Settings.grid_width
            y = (pos[1] + Settings.grid_height) % Settings.grid_height
            self.x = x * self.grid_size
            self.y = y * self.grid_size
            self.pos = x, y
            self.dir = self.prior_part.dir


class Snake(object):

    def __init__(self, screen, color, init_length):
        self.screen = screen
        self.color = color
        self.length = init_length
        self.body_part = []
        self.init_snake_body()

    def init_snake_body(self):
        pos = random_locate()
        dir = random.randint(0, 3)
        for i in range(self.length):
            snake_part = SnakeBodyPart(self.screen, pos, dir, self.color)
            if dir == 0:
                pos = (pos[0], pos[1] + 1)
            if dir == 1:
                pos = (pos[0], pos[1] - 1)
            if dir == 2:
                pos = (pos[0] + 1, pos[1])
            if dir == 3:
                pos = (pos[0] - 1, pos[1])
            if i != 0:
                prior_part.next_part = snake_part
                snake_part.prior_part = prior_part
            prior_part = snake_part
            self.body_part.append(snake_part)
        self.snake_head = self.body_part[0]
        self.snake_tail = self.body_part[-1]

    def events(self):
        key_state = pg.key.get_pressed()
        # Change the direction of the head of the snake.
        if key_state[pg.K_LEFT] or key_state[pg.K_a]:
            if self.snake_head.dir != 3:
                self.snake_head.dir = 2
        if key_state[pg.K_RIGHT] or key_state[pg.K_d]:
            if self.snake_head.dir != 2:
                self.snake_head.dir = 3
        if key_state[pg.K_UP] or key_state[pg.K_w]:
            if self.snake_head.dir != 1:
                self.snake_head.dir = 0
        if key_state[pg.K_DOWN] or key_state[pg.K_s]:
            if self.snake_head.dir != 0:
                self.snake_head.dir = 1

    def update(self):
        part = self.snake_tail
        while part:
            part.duplicate_prior()
            part = part.prior_part
        self.snake_head.update()

    def detect_head_body(self):
        part = self.snake_head.next_part
        is_collision = False
        while part:
            if part.pos == self.snake_head.pos:
                is_collision = True
            part = part.next_part
        return is_collision

    def draw(self):
        for o in self.body_part:
            o.draw()

    def add_body_part(self):
        """Add a new body part follow the tail."""
        pos = self.snake_tail.pos
        dir = self.snake_tail.dir
        snake_part = SnakeBodyPart(self.screen, pos, dir, self.color)
        self.snake_tail.next_part = snake_part
        snake_part.prior_part = self.snake_tail
        self.snake_tail = snake_part
        self.body_part.append(self.snake_tail)


class Food(object):

    def __init__(self, screen, color):
        self.screen = screen
        self.width, self.height = Settings.grid_size, Settings.grid_size
        self.color = color
        pos = random_locate()
        x = (pos[0] + Settings.grid_width) % Settings.grid_width
        y = (pos[1] + Settings.grid_height) % Settings.grid_height
        self.grid_size = Settings.grid_size
        self.x = x * self.grid_size
        self.y = y * self.grid_size
        self.pos = x, y

    def draw(self):
        rect_size = (self.x, self.y, self.width, self.height)
        pg.draw.rect(self.screen, self.color, rect_size, 0)


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
        """Initialize the contains of objects in game."""
        self.snake = Snake(self.screen, Settings.snake_color, Settings.snake_init_length)
        self.foods = []

    def run(self):
        """Game loop."""
        self.count = 0
        self.score = 0
        self.clock.tick(self.fps)
        while self.running:
            # self.clock.tick(self.fps)
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
                    self.debug = ~ self.debug
        # Snake's events.
        self.snake.events()

    def update(self):
        """Update the state of the game."""
        # Update the data of snake.
        if self.count % Settings.snake_move_feq == 0:
            self.snake.update()
            self.count = 0
        self.count += 1

        # Locate the foods on the map.
        n_foods = len(self.foods)
        if n_foods < Settings.food_nums:
            for i in range(Settings.food_nums - n_foods):
                f = Food(self.screen, Settings.food_color)
                self.foods.append(f)

        # Detect whether the snake eat food.
        for f in self.foods:
            if f.pos == self.snake.snake_head.pos:
                self.foods.remove(f)
                self.score += 1
                self.snake.add_body_part()

        if self.snake.detect_head_body():
            self.running = False

    def draw(self):
        """Main draw function."""
        self.screen.fill(Settings.background_color)

        for x in range(0, Settings.width, Settings.grid_size):
            pg.draw.line(self.screen, Settings.grid_color, (x, 0), (x, Settings.height))
        for y in range(0, Settings.height, Settings.grid_size):
            pg.draw.line(self.screen, Settings.grid_color, (0, y), (Settings.width, y))

        self.snake.draw()

        for f in self.foods:
            f.draw()

        score_text = "Score %d" % self.score
        self.draw_text(score_text, Settings.font_size, Settings.font_x, Settings.font_y, Settings.font_color)
        pg.display.flip()

    def draw_text(self, text, size, x, y, color):
        """Draw the text in the screen."""
        font = pg.font.Font(self.font, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)


if __name__ == "__main__":
    g = Game()
    g.run()
