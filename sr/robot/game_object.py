import threading

class GameObject(object):
    surface_name = None
    marker_info = None
    grabbable = False

    def __init__(self, arena):
        self.arena = arena

        self.location = (0, 0)
        self.heading = 0

        self.lock = threading.RLock()

