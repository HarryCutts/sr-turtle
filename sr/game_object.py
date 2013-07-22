import threading

class GameObject(object):
    surface_name = None
    marker_info = None
    grabbable = False

    location = (0, 0)
    heading = 0

    def __init__(self, arena):
        self.arena = arena

        self.lock = threading.RLock()

