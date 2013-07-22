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
    if not name in sprites:
        sprites[name] = pygame.image.load(name).convert_alpha()

    return sprites[name]

class Display(object):

    def __init__(s, arena):
        s.arena = arena
        arena_w, arena_h = s.arena.size
        s.size = (arena_w * PIXELS_PER_METER, arena_h * PIXELS_PER_METER)

        pygame.display.init()
        s._window = pygame.display.set_mode(s.size)
        pygame.display.set_caption("SR Turtle Robot Simulator")
        s._screen = pygame.display.get_surface()
        s._draw_background()
        s._draw()

    def __del__(s):
        pygame.display.quit()

    def _draw_background(s):
        s._background = pygame.Surface(s.size)
        s._background.fill(ARENA_FLOOR_COLOR)
        a = s.arena
        # Corners of the inside square
        top_left     = to_pixel_coord((a.left + a.zone_size, a.top + a.zone_size), a)
        top_right    = to_pixel_coord((a.right - a.zone_size, a.top + a.zone_size), a)
        bottom_right = to_pixel_coord((a.right - a.zone_size, a.bottom - a.zone_size), a)
        bottom_left  = to_pixel_coord((a.left + a.zone_size, a.bottom - a.zone_size), a)

        # Lines separating zones
        def line(start, end):
            pygame.draw.line(s._background, ARENA_MARKINGS_COLOR, \
                             start, end, ARENA_MARKINGS_WIDTH)

        line((0, 0), top_left)
        line((s.size[0], 0), top_right)
        line(s.size, bottom_right)
        line((0, s.size[1]), bottom_left)

        # Square separating zones from centre
        pygame.draw.polygon(s._background, ARENA_MARKINGS_COLOR, \
                            [top_left, top_right, bottom_right, bottom_left], 2)

        # Motif
        motif = get_surface(a.motif_name)
        x, y = to_pixel_coord((0, 0), s.arena)
        w, h = motif.get_size()
        s._background.blit(motif, (x - w / 2, y - h / 2))

    def _draw(s):
        s._screen.blit(s._background, (0, 0))

        for o in s.arena.objects:
            if o.surface_name != None:
                with o.lock:
                    surface = get_surface(o.surface_name)
                    surface = pygame.transform.rotate(surface, -degrees(o.heading))
                    object_width, object_height = surface.get_size()
                    x, y = to_pixel_coord(o.location, s.arena)
                    screen_location = (x - object_width / 2, y - object_height / 2)
                    s._screen.blit(surface, screen_location)

        pygame.display.flip()

    ## Public Methods ##

    def tick(s, time_passed):
        s.arena.tick(time_passed)
        # TODO: Allow multiple displays on one arena without them all ticking it
        s._draw()
