from game_object import GameObject
from vision import create_marker_info_by_type, MARKER_TOKEN

class Token(GameObject):
    def __init__(s, arena, number):
        GameObject.__init__(s, arena)
        s.marker_info = create_marker_info_by_type(MARKER_TOKEN, number)
        s.surface_name = 'token.png'
