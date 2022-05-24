from settings import *
import pygame as pg
from pygame.math import Vector2


def collide_hit_rect(sprite1, sprite2):
    """sub-function of collide function."""
    return sprite1.hit_rect.colliderect(sprite2.rect)


def collide_with_obstacles(sprite, dir):
    """collide with obstacles."""
    hits = pg.sprite.spritecollide(
        sprite, sprite.game.obstacles, False, collide_hit_rect)
    if hits:
        w = hits[0].rect
        if dir == 0:
            if sprite.vel.x > 0:
                sprite.hit_rect.right = w.left
            elif sprite.vel.x < 0:
                sprite.hit_rect.left = w.right
            elif sprite.vel.x == 0:
                pass
        elif dir == 1:
            if sprite.vel.y > 0:
                sprite.hit_rect.bottom = w.top
            elif sprite.vel.y < 0:
                sprite.hit_rect.top = w.bottom
            elif sprite.vel.y == 0:
                pass


def direction2rotation(dir):
    """Convert the direction vector to rotation."""
    rot = 0
    if dir.x == 0:
        if dir.y >= 0:
            rot = - 90
        else:
            rot = 90
    else:
        angle = math.atan(abs(dir.y / dir.x)) * PI_CONVERT
        if dir.x > 0 and dir.y < 0:
            rot = angle
        if dir.x > 0 and dir.y > 0:
            rot = - angle
        if dir.x < 0 and dir.y < 0:
            rot = 180 - angle
        if dir.x < 0 and dir.y > 0:
            rot = - (180 - angle)

    return rot


class Player(pg.sprite.Sprite):
    """Player object."""
    def __init__(self, game, x, y, w, h):

        self.game = game
        pg.sprite.Sprite.__init__(self)

        self.original_image = pg.transform.scale(
            self.game.player_img, (TILE_SIZE, TILE_SIZE))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.hit_rect = pg.Rect(x, y, w, h)

        # Initial the state of the player.
        self.acc_rate = PLAYER_ACC_RATE
        self.acc = Vector2()
        self.vel = Vector2()

        # the position of player in the screen
        self.l_pos = Vector2()
        self.g_pos = Vector2()

        # shooter delay
        self.shoot_delay = PLAYER_SHOOT_DELAY
        self.last_time = pg.time.get_ticks()

        self.rot = 0

        self.health = PLAYER_HEALTH

    def update(self):

        self.vel = Vector2()
        self.acc = Vector2()
        key_state = pg.key.get_pressed()

        if key_state[pg.K_LEFT] or key_state[pg.K_a]:
            self.acc.x = - self.acc_rate
        if key_state[pg.K_RIGHT] or key_state[pg.K_d]:
            self.acc.x = self.acc_rate
        if key_state[pg.K_UP] or key_state[pg.K_w]:
            self.acc.y = - self.acc_rate
        if key_state[pg.K_DOWN] or key_state[pg.K_s]:
            self.acc.y = self.acc_rate

        self.collide_with_mobs()

        self.vel += self.acc

        if key_state[pg.K_SPACE]:
            self.shoot()

        self.rotate()

        self.hit_rect.centerx += self.vel.x
        collide_with_obstacles(self, 0)
        self.hit_rect.centery += self.vel.y
        collide_with_obstacles(self, 1)

        self.rect.center = self.hit_rect.center
        self.g_pos = Vector2(self.rect.centerx, self.rect.centery)

        # update the real position in the screen
        camera = self.game.camera.camera
        self.l_pos = Vector2(self.rect.centerx + camera.x,
                             self.rect.centery + camera.y)

    def rotate(self):
        """rotate function"""
        m_pos = self.game.cursor.l_pos
        self.dir = m_pos - self.l_pos

        # keep the position of image center
        old_center = self.rect.center
        self.rot = direction2rotation(self.dir)
        self.image = pg.transform.rotate(self.original_image, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = old_center

    def shoot(self):
        """shoot operation"""
        now = pg.time.get_ticks()

        if now - self.last_time > self.shoot_delay:
            bullet = Bullet(self.game, self.rect.centerx,
                            self.rect.centery, self.rot)
            self.game.bullets.add(bullet)
            self.game.all_sprites.add(bullet)
            self.last_time = now

    def collide_with_mobs(self):

        mobs = pg.sprite.spritecollide(
            self, self.game.mobs, False, collide_hit_rect)
        for mob in mobs:
            dir = self.g_pos - mob.g_pos
            dir.scale_to_length(8)
            self.acc += dir
            self.health -= mob.damage
            if self.health <= 0:
                self.kill()

    def draw_health_bar(self):

        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED
        width = int(self.hit_rect.width * self.health / PLAYER_HEALTH)
        self.health_bar = pg.Rect(0, 0, width, 7)
        if self.health < PLAYER_HEALTH:
            pg.draw.rect(self.image, col, self.health_bar)


class Bullet(pg.sprite.Sprite):
    """bullet object"""

    def __init__(self, game, x, y, rot):

        pg.sprite.Sprite.__init__(self)

        self.game = game

        self.image = pg.Surface((5, 5))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        # math.cos and sin use the radian system
        pi = math.pi
        self.rot = rot * pi / 180
        self.vel_rate = 10
        vx = abs(math.cos(self.rot))
        vy = abs(math.sin(self.rot))
        if self.rot >= 0 and self.rot <= pi / 2:
            vy = - vy
        if self.rot >= pi / 2 and self.rot <= pi:
            vy = - vy
            vx = - vx
        if self.rot <= - pi / 2 and self.rot >= - pi:
            vx = - vx
        self.vel = Vector2(vx, vy) * self.vel_rate

        self.damage = 10

    def update(self):

        self.rect.centerx += self.vel.x
        self.rect.centery += self.vel.y


class Mob(pg.sprite.Sprite):
    """enemy object"""

    def __init__(self, game, x, y, w, h):

        self.game = game
        self.groups = self.game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)

        self.original_image = pg.transform.scale(
            self.game.mob_img, (TILE_SIZE, TILE_SIZE))
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.hit_rect = pg.Rect(x, y, w, h)

        self.g_pos = Vector2()

        self.rot = 0
        self.per_dis = ZOMBIE_PERCEPTION_DISTANCE

        self.acc_rate = ZOMBIE_ACC_RATE
        self.acc = Vector2()
        self.vel = Vector2()

        self.health = ZOMBIE_HEALTH
        self.damage = ZOMBIE_DAMAGE

    def update(self):
        # the position of player
        self.acc = Vector2()
        self.vel = Vector2()
        self.update_dir()
        self.update_vel()

        self.hit_rect.centerx += self.vel.x
        collide_with_obstacles(self, 0)
        self.hit_rect.centery += self.vel.y
        collide_with_obstacles(self, 1)

        self.hits_with_bullets()

        self.rect.center = self.hit_rect.center
        self.g_pos = Vector2(self.rect.centerx, self.rect.centery)

    def update_dir(self):
        """Update the dir of the mob."""
        p_pos = self.game.player.g_pos
        self.dir = dir = p_pos - self.g_pos
        # distance = math.sqrt(dir.x ** 2 + dir.y ** 2)

        if p_pos.distance_to(self.g_pos) <= self.per_dis:
            old_center = self.rect.center
            self.rot = direction2rotation(self.dir)
            self.image = pg.transform.rotate(self.original_image, self.rot)
            self.rect = self.image.get_rect()
            self.rect.center = old_center
            self.acc_rate = ZOMBIE_ACC_RATE
        else:
            self.acc_rate = 0
            self.vel = Vector2()

    def update_vel(self):
        """Change the position of mod."""
        if self.acc_rate != 0:
            self.acc = self.dir
            self.acc.scale_to_length(self.acc_rate)
            self.vel += self.acc

    def hits_with_bullets(self):

        hits = pg.sprite.spritecollide(
            self, self.game.bullets, True, collide_hit_rect)
        if hits:
            self.health -= 30
            if self.health <= 0:
                self.kill()

    def draw_health_bar(self):

        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED
        width = int(self.hit_rect.width * self.health / 100)
        self.health_bar = pg.Rect(0, 0, width, 7)
        if self.health < 100:
            pg.draw.rect(self.image, col, self.health_bar)


class Obstacle(pg.sprite.Sprite):

    def __init__(self, game, x, y, w, h):

        self.game = game
        self.groups = self.game.obstacles
        pg.sprite.Sprite.__init__(self, self.groups)
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y


class Cursor(pg.sprite.Sprite):
    """Cursor object."""

    def __init__(self, game, color, radius):

        pg.sprite.Sprite.__init__(self)

        self.game = game
        self.color = color

        # local position, not global position
        x, y = pg.mouse.get_pos()
        self.l_pos = Vector2(x, y)

        self.radius = radius

    def update(self):

        self.l_pos = Vector2(pg.mouse.get_pos())

    def draw(self):
        pg.draw.circle(self.game.screen, self.color,
                       (int(self.l_pos.x), int(self.l_pos.y)), self.radius)
