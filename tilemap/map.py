import pygame as pg
from settings import *
import pytmx


class TiledMap:
    def __init__(self, filename):

        tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm

    def render(self, surface):
        # load layer from tmxdata
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth,
                                            y * self.tmxdata.tileheight))

    def make_map(self):

        temp_surface = pg.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface


class Camera(object):

    def __init__(self, game, width, height):

        self.game = game

        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        """Modified the position of entity."""
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        """Modified the position of rect of objects."""
        return rect.move(self.camera.topleft)

    def apply_hit_rect(self, hit_rect):
        """Modified the position of hit rect of objects."""
        return hit_rect.move(self.camera.topleft)

    def update(self, target):

        target_rect = target.rect.center

        x = - target_rect[0] + int(self.width / 2)
        y = - target_rect[1] + int(self.height / 2)

        # Limit the position of the camera
        self.map = self.game.map
        self.map_width = self.map.width
        self.map_height = self.map.height

        if target_rect[0] <= int(self.width / 2):
            x = 0
        if target_rect[0] >= int(self.map_width - self.width / 2):
            x = - self.map_width + self.width
        if target_rect[1] <= int(self.height / 2):
            y = 0
        if target_rect[1] >= int(self.map_height - self.height / 2):
            y = - self.map_height + self.height

        self.camera = pg.Rect(x, y, self.width, self.height)
