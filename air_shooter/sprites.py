"""sprites"""
import pygame as pg
from settings import *
import random
import os


class Player(pg.sprite.Sprite):
    """Player object"""


    def __init__(self, game):

        pg.sprite.Sprite.__init__(self)

        self.game = game

        self.image = pg.transform.scale(self.game.player_image, (40, 38))
        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT - 38 / 2)

        # Displacement change
        self.speed_x = 0
        self.speed_y = 0

        self.radius = int(self.rect.width * .85 / 2)

        # Shields: init to 100
        self.shields = 100

        self.shoot_delay = 250
        self.last_shoot = pg.time.get_ticks()

    def update(self):

        self.speed_x = 0
        self.speed_y = 0
        key_state = pg.key.get_pressed()

        if key_state[pg.K_LEFT] or key_state[pg.K_a]:
            self.speed_x = -5
        if key_state[pg.K_RIGHT] or key_state[pg.K_d]:
            self.speed_x = +5
        if key_state[pg.K_UP] or key_state[pg.K_w]:
            self.speed_y = -5
        if key_state[pg.K_DOWN] or key_state[pg.K_s]:
            self.speed_y = +5

        if key_state[pg.K_SPACE]:
            self.shoot()

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

        hits = pg.sprite.spritecollide(self, self.game.mobs, False, pg.sprite.collide_circle)
        for hit in hits:
            self.shields -= hit.radius * 0.3
            if self.shields <= 0:
                self.game.running = False

    def shoot(self):

        now_shoot = pg.time.get_ticks()

        if now_shoot - self.last_shoot > self.shoot_delay:
            bullet = Bullet(self.game, self.rect.centerx, self.rect.top)
            self.game.all_sprites.add(bullet)
            self.game.bullets.add(bullet)
            self.game.shooter_sound.play()
            self.last_shoot = now_shoot


class Bullet(pg.sprite.Sprite):
    """Bullet object."""

    def __init__(self, game, x, y):

        pg.sprite.Sprite.__init__(self)

        self.game = game

        self.image = self.game.bullet_image
        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speed_y = -10

    def update(self):

        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
            self.kill()

        hits = pg.sprite.groupcollide(self.game.mobs, self.game.bullets, True, True)
        for hit in hits:
            self.game.score += 100 - hit.radius
            self.game.exp_sound.play()
            exp = MobExplosion(self.game, hit.rect.center, hit.radius)
            self.game.all_sprites.add(exp)
            self.game.create_mob()


class Mob(pg.sprite.Sprite):
    """Meteor object."""

    def __init__(self, game):

        pg.sprite.Sprite.__init__(self)

        self.game = game

        self.image_file = random.choice(game.mob_list)
        self.image_path = os.path.join(game.mob_dir, self.image_file)
        self.image = pg.image.load(self.image_path)
        self.image_copy = self.image.copy()

        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)

        # Displacement change, set randomly
        self.speed_y = random.randrange(1, 8)
        self.speed_x = random.randrange(-3, 3)

        self.radius = int(self.rect.width / 2)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pg.time.get_ticks()

    def rotate(self):

        now = pg.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pg.transform.rotate(self.image_copy, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed_y = random.randrange(1, 8)


class MobExplosion(pg.sprite.Sprite):
    """The explosion animation of mob."""

    def __init__(self, game, center, size):

        pg.sprite.Sprite.__init__(self)

        self.game = game

        self.image_frame = 0
        self.image_size = size
        self.image_common_name = "regularExplosion0{0}.png"

        self.image_load()
        self.rect = self.image.get_rect()
        self.rect.center = center

        self.frame_rate = 50
        self.animation_frame_length = len(self.game.exp_list)
        self.last_frame_time = pg.time.get_ticks()

    def update(self):

        now_frame_time = pg.time.get_ticks()

        if now_frame_time - self.last_frame_time > self.frame_rate:
            self.last_frame_time = now_frame_time
            self.image_frame += 1

            if self.image_frame == self.animation_frame_length:
                self.kill()
            else:
                center = self.rect.center
                self.image_load()
                self.rect = self.image.get_rect()
                self.rect.center = center

    def image_load(self):

        self.image_file = self.image_common_name.format(self.image_frame)
        self.image_path = os.path.join(self.game.exp_dir, self.image_file)
        self.image_asset = pg.image.load(self.image_path)

        self.image = pg.transform.scale(self.image_asset, (2 * self.image_size, 2 * self.image_size))
