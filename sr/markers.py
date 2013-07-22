from game_object import GameObject
from vision import create_marker_info_by_type, MARKER_TOKEN, MARKER_ARENA

class Token(GameObject):
    grabbable = True

    def __init__(self, arena, number):
        GameObject.__init__(self, arena)
        self.marker_info = create_marker_info_by_type(MARKER_TOKEN, number)
        self.grabbed = False

    def grab(self):
        self.grabbed = True

    def release(self):
        self.grabbed = False

    @property
    def surface_name(self):
        return 'sr/token{0}.png'.format('_grabbed' if self.grabbed else '')

class WallMarker(GameObject):
    surface_name = 'sr/wall_marker.png'

    def __init__(self, arena, number, location=(0,0), heading=0):
        GameObject.__init__(self, arena)
        self.marker_info = create_marker_info_by_type(MARKER_ARENA, number)
        self.location = location
        self.heading = heading

