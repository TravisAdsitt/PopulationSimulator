from dataclasses import dataclass, field
from enum import Enum
import random
from typing import List, Tuple

from game_objects import GameObject


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


@dataclass(init=True)
class View:
    North: List = field(default_factory=list)
    South: List = field(default_factory=list)
    East: List = field(default_factory=list)
    West: List = field(default_factory=list)
    Center: List = field(default_factory=list)

    def __post_init__(self):
        lists_to_check = [self.North, self.South, self.East, self.West, self.Center]
        for curr_list in lists_to_check:
            things_to_remove = []

            for thing in curr_list:
                if not isinstance(thing, GameObject):
                    things_to_remove.append(thing)
                    continue
                if not thing.visible():
                    things_to_remove.append(thing)
                    continue

            for thing in things_to_remove:
                curr_list.remove(thing)

    def get_direction_for_thing(
        self, find: GameObject
    ) -> Tuple[GameObject, CompassDirection] or Tuple[None, None]:
        for thing in self.Center:
            if find.__name__ == thing.__name__:
                return (thing, CompassDirection.Center)
        remaining_directions = [
            (CompassDirection.North, self.North),
            (CompassDirection.South, self.South),
            (CompassDirection.East, self.East),
            (CompassDirection.West, self.West),
        ]
        random.shuffle(remaining_directions)

        for direction, thing_list in remaining_directions:
            for thing in thing_list:
                if find.__name__ == thing.__name__:
                    return (thing, direction)

        return (None, None)
