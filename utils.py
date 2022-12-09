from enum import Enum
from typing import List


class CompassDirection(Enum):
    North = "North"
    South = "South"
    East = "East"
    West = "West"
    Center = "Center"

    @classmethod
    def step_coordinates_in_direction(
        cls, x: int, y: int, direction: "CompassDirection", count: int = 1
    ):
        delta_x = 0
        delta_y = 0

        if direction == CompassDirection.North:
            delta_y = -count
        elif direction == CompassDirection.South:
            delta_y = count
        elif direction == CompassDirection.East:
            delta_x = count
        else:
            delta_x = -count

        return (x + delta_x, y + delta_y)
