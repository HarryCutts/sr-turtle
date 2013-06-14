from game_object import GameObject
from vision import create_marker_info_by_type, MARKER_TOKEN, MARKER_ARENA

class Token(GameObject):
    def __init__(s, arena, number):
        GameObject.__init__(s, arena)
        s.marker_info = create_marker_info_by_type(MARKER_TOKEN, number)
        s.surface_name = 'token.png'

class WallMarker(GameObject):
    def __init__(s, arena, number, location=(0,0), heading=0):
        GameObject.__init__(s, arena)
        s.marker_info = create_marker_info_by_type(MARKER_ARENA, number)
        s.surface_name = 'wall_marker.png'
        s.location = location
        s.heading = heading
