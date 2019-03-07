from enum import Enum


class Direction(Enum):
    BIDIRECTIONAL = "-",
    LEFT_TO_RIGHT = "left_to_right",
    RIGHT_TO_LEFT = "right_to_left",
    NONE = None
