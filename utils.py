from dataclasses import dataclass, field
from enum import Enum
import random
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
    
    @classmethod
    def get_random_direction(cls):
        return random.choice([cls.North, cls.South, cls.East, cls.West])

@dataclass(init=True)
class View:
    North: List = field(default_factory=list)
    South: List = field(default_factory=list)
    East: List = field(default_factory=list)
    West: List = field(default_factory=list)
    Center: List = field(default_factory=list)

    def shuffle_all_but_center(self):
        ret_list = [(CompassDirection.Center, self.Center)]

        remaining_items = [(CompassDirection.North, self.North), (CompassDirection.South, self.South), (CompassDirection.East, self.East), (CompassDirection.West, self.West)]
        random.shuffle(remaining_items)

        ret_list.extend(remaining_items)

        return ret_list
