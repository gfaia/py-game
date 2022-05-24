from settings import *
import pygame as pg
from math import Vector2


class Player(pg.sprite.Sprite):
    """Player object."""

    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)

        self.image = pg.Surface((30, 30))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)

        self.vel = Vector2()
        self.acc = Vector2(y=GRAVITY)

        # Whether player standing on the platform.
        self.standing = False

        # The game app reference
        self.game = game

    def update(self):
        self.acc = Vector2(y=GRAVITY)

        key_state = pg.key.get_pressed()

        if key_state[pg.K_LEFT] or key_state[pg.K_a]:
            self.acc.x -= 0.1
        if key_state[pg.K_RIGHT] or key_state[pg.K_d]:
            self.acc.x += 0.1

        # Only jumper when player is standing on the platform.
        if self.standing == True:
            if key_state[pg.K_SPACE]:
                self.vel.y = -5

        # Detect collusion.
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        if hits:
            for hit in hits:
                # If player above the platforms
                if self.rect.bottom < hit.rect.bottom:
                    self.rect.bottom = hit.rect.top
                    self.vel.y = 0
                    self.standing = True

                # If player under the platforms
                if self.rect.top > hit.rect.top:
                    self.rect.top = hit.rect.bottom
                    self.vel.y = 0
                    self.standing = False
        else:
            self.standing = False

        # Change the vel of object.
        self.vel += self.acc
        self.rect.x += self.vel.x
        self.rect.y += self.vel.y

        self.rect.right = self.rect.right % WIDTH
        self.rect.left = self.rect.left % WIDTH


class Platform(pg.sprite.Sprite):
    """Platform object."""

    def __init__(self, x, y, w, h):
        pg.sprite.Sprite.__init__(self)

        self.image = pg.Surface((w, h))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
