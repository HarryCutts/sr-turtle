from game_object import GameObject

class Token(GameObject):
    def __init__(s, arena, marker_info):
        GameObject.__init__(s, arena)
        s.marker_info = marker_info
        s.surface_name = 'token.png'
