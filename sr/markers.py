from game_object import GameObject
from vision import create_marker_info_by_type, MARKER_TOKEN, MARKER_ARENA

class Token(GameObject):
    surface_name = 'sr/token.png'
    grabbable = True

    def __init__(self, arena, number):
        GameObject.__init__(self, arena)
        self.marker_info = create_marker_info_by_type(MARKER_TOKEN, number)

    def grab(self):
        self.surface_name = 'sr/token_grabbed.png'

    def release(self):
        self.surface_name = 'sr/token.png'

class WallMarker(GameObject):
    surface_name = 'sr/wall_marker.png'

    def __init__(self, arena, number, location=(0,0), heading=0):
        GameObject.__init__(self, arena)
        self.marker_info = create_marker_info_by_type(MARKER_ARENA, number)
        self.location = location
        self.heading = heading

