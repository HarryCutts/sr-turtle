from collections import namedtuple

MARKER_ARENA = 'arena'
MARKER_ROBOT = 'robot'

MARKER_PEDESTAL = 'pedestal'
MARKER_TOKEN = 'token'

MARKER_FLAG = 'token'
    # Old simulator versions used MARKER_TOKEN for flags. This retains backward
    # compatibility.

MARKER_TOKEN_GOLD   = 'token_gold'
MARKER_TOKEN_SILVER = 'token_silver'

marker_offsets = {
    MARKER_ARENA: 0,
    MARKER_ROBOT: 28,
}

marker_sizes = {
    MARKER_ARENA: 0.25 * (10.0/12),
    MARKER_ROBOT: 0.1 * (10.0/12),
}

def init_marker_info(arena_class):
    """
    Initialize the `marker_offsets` and `marker_sizes` dictionaries for the
    given arena. The dictionaries from the given arena class are combined with
    the default dictionaries.
    """
    marker_offsets.update(arena_class.marker_offsets)
    marker_sizes.update(arena_class.marker_sizes)

# MarkerInfo class
MarkerInfo = namedtuple( "MarkerInfo", "code marker_type offset size" )

def create_marker_info_by_type(marker_type, offset):
    return MarkerInfo(marker_type = marker_type,
                      offset = offset,
                      size = marker_sizes[marker_type],
                      code = marker_offsets[marker_type] + offset)

# Points
# TODO: World Coordinates
PolarCoord = namedtuple("PolarCoord", "length rot_y")
Point = namedtuple("Point", "polar")

# Marker class
MarkerBase = namedtuple( "Marker", "info res centre timestamp" )
class Marker(MarkerBase):
    def __init__(self, *a, **kwd):
        # Aliases
        self.dist = self.centre.polar.length
        self.rot_y = self.centre.polar.rot_y
