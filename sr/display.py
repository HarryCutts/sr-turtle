from __future__ import division
from math import degrees

import pygame

PIXELS_PER_METER = 100

ARENA_FLOOR_COLOR = (0x11, 0x18, 0x33)
ARENA_MARKINGS_COLOR = (0xD0, 0xD0, 0xD0)
ARENA_MARKINGS_WIDTH = 2

def to_pixel_coord(world_coord, arena):
    offset_x = arena.size[0] / 2
    offset_y = arena.size[1] / 2
    x, y = world_coord
    x, y = ((x + offset_x) * PIXELS_PER_METER, (y + offset_y) * PIXELS_PER_METER)
    return (x, y)

sprites = {}

def get_surface(name):
    if name not in sprites:
        sprites[name] = pygame.image.load(name).convert_alpha()

    return sprites[name]

class Display(object):
    def __init__(self, arena):
        self.arena = arena
        arena_w, arena_h = self.arena.size
        self.size = (arena_w * PIXELS_PER_METER, arena_h * PIXELS_PER_METER)

        pygame.display.init()
        self._window = pygame.display.set_mode(self.size)
        pygame.display.set_caption("SR Turtle Robot Simulator")
        self._screen = pygame.display.get_surface()
        self._draw_background()
        self._draw()

    def __del__(self):
        pygame.display.quit()

    def _draw_background(self):
        self._background = pygame.Surface(self.size)
        self._background.fill(ARENA_FLOOR_COLOR)
        a = self.arena
        # Corners of the inside square
        top_left     = to_pixel_coord((a.left + a.zone_size, a.top + a.zone_size), a)
        top_right    = to_pixel_coord((a.right - a.zone_size, a.top + a.zone_size), a)
        bottom_right = to_pixel_coord((a.right - a.zone_size, a.bottom - a.zone_size), a)
        bottom_left  = to_pixel_coord((a.left + a.zone_size, a.bottom - a.zone_size), a)

        # Lines separating zones
        def line(start, end):
            pygame.draw.line(self._background, ARENA_MARKINGS_COLOR, \
                             start, end, ARENA_MARKINGS_WIDTH)

        line((0, 0), top_left)
        line((self.size[0], 0), top_right)
        line(self.size, bottom_right)
        line((0, self.size[1]), bottom_left)

        # Square separating zones from centre
        pygame.draw.polygon(self._background, ARENA_MARKINGS_COLOR, \
                            [top_left, top_right, bottom_right, bottom_left], 2)

        # Motif
        motif = get_surface(a.motif_name)
        x, y = to_pixel_coord((0, 0), self.arena)
        w, h = motif.get_size()
        self._background.blit(motif, (x - w / 2, y - h / 2))

    def _draw(self):
        self._screen.blit(self._background, (0, 0))

        for obj in self.arena.objects:
            if obj.surface_name is None:
                continue
            with obj.lock:
                surface = get_surface(obj.surface_name)
                surface = pygame.transform.rotate(surface, -degrees(obj.heading))
                object_width, object_height = surface.get_size()
                x, y = to_pixel_coord(obj.location, self.arena)
                screen_location = (x - object_width / 2, y - object_height / 2)
                self._screen.blit(surface, screen_location)

        pygame.display.flip()

    ## Public Methods ##

    def tick(self, time_passed):
        self.arena.tick(time_passed)
        # TODO: Allow multiple displays on one arena without them all ticking it
        self._draw()
