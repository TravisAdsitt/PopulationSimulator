from typing import Tuple
import random
import logging
import argparse
from desires import Desire, EatDesire, MoveDesire

from game_objects import Food, GameObject, Person, View
from utils import CompassDirection

logger = logging.getLogger(__name__)


class LocationManager:
    def __init__(self, max_x: int = -1, max_y: int = -1):
        self.locations = {}
        self.things = {}
        self.max_x = max_x
        self.max_y = max_y

        if self.max_x < 1:
            self.max_x = random.randint(1, 100)
        if self.max_y < 1:
            self.max_y = random.randint(1, 100)

    def get_location_key(self, x: int, y: int):
        location_x = x % self.max_x
        location_y = y % self.max_y

        return f"{location_x},{location_y}"

    def get_thing_coordinates(self, thing: GameObject):
        if thing not in self.things:
            raise Exception("Cannot find that thing!")

        location_key = self.things[thing]

        x, y = location_key.split(",")

        return (int(x), int(y))

    def ensure_coordinates_inbounds(self, x, y) -> Tuple[int, int]:
        x %= self.max_x
        y %= self.max_y

        if x < 0:
            x += self.max_x
        if y < 0:
            y += self.max_y

        return (x, y)

    def get_things_at_location(self, x: int, y: int):
        location_key = self.get_location_key(x, y)

        if location_key not in self.locations:
            self.locations[location_key] = []

        return self.locations[location_key]

    def add_thing(self, new_thing: GameObject, x: int, y: int):
        location_key = self.get_location_key(x, y)

        if location_key not in self.locations:
            self.locations[location_key] = []
        if new_thing not in self.things:
            self.things[new_thing] = location_key

        for thing in self.locations[location_key]:
            if type(thing) == type(new_thing):
                raise Exception("Cannot place that there!")

        self.locations[location_key].append(new_thing)

    def remove_thing(self, thing: GameObject, x: int = -1, y: int = -1):
        location_key = None

        if thing and thing in self.things:
            location_key = self.things[thing]

            if thing in self.locations[location_key]:
                self.locations[location_key].remove(thing)

            self.things.pop(thing)

        if x >= 0 and y >= 0 and location_key != self.get_location_key(x, y):
            location_key = self.get_location_key(x, y)

            things_at_location = self.locations[location_key]

            if thing in things_at_location:
                things_at_location.remove(thing)

    def move_thing_in_direction(
        self, thing: GameObject, direction: CompassDirection, count: int = 1
    ):
        if thing not in self.things:
            raise Exception("Cannot find that thing!")

        x, y = self.get_thing_coordinates(thing)
        stepped_x, stepped_y = CompassDirection.step_coordinates_in_direction(
            x, y, direction, count
        )
        classname = thing.__class__.__name__
        id_str = ""
        if isinstance(thing, GameObject):
            id_str = f"({thing.id})"

        logger.debug(
            f"Moving {classname}{id_str} from ({x},{y}) to ({stepped_x},{stepped_y})"
        )

        self.remove_thing(thing)
        try:
            # If this raises then that spot is taken
            self.add_thing(thing, stepped_x, stepped_y)
        except Exception:
            # If it is taken then go back to where we were
            logger.debug(f"Couldn't move {classname}!")
            self.add_thing(thing, x, y)

        logger.debug(f"Moved {classname}!")

    def get_things_in_direction_from_thing(
        self, thing: GameObject, direction: CompassDirection, distance: int = 1
    ):
        ret_val = []

        if thing not in self.things:
            return ret_val

        x, y = self.get_thing_coordinates(thing)

        for _ in range(distance):
            new_x, new_y = CompassDirection.step_coordinates_in_direction(
                x, y, direction
            )
            ret_val.extend(self.get_things_at_location(new_x, new_y))

        return ret_val


class World:
    def __init__(self):
        self.world_width = 100
        self.world_height = 100

        self.location_manager = LocationManager(self.world_width, self.world_height)

        self.people_start = 5
        self.food_start = 10

        self._init_world()

    def add_thing_in_random_location(self, thing: GameObject, max_retry: int = 50):
        added = False
        retry = 0

        while not added and retry < max_retry:
            random_x = random.randint(0, self.world_width - 1)
            random_y = random.randint(0, self.world_height - 1)
            # If the following raises, it is because there is a thing at this location already
            try:
                self.location_manager.add_thing(thing(), random_x, random_y)
                added = True
            except Exception:
                retry += 1
                continue

            if added:
                logger.debug(
                    f"Added a {thing.__name__} at location ({str(random_x)},{str(random_y)})."
                )

    def cull_invisible(self, view: View):
        lists_to_check = [view.North, view.South, view.East, view.West, view.Center]
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
        
        return view

    def get_view(self, thing: GameObject, distance: int) -> View:
        east = self.location_manager.get_things_in_direction_from_thing(
            thing, CompassDirection.East, distance
        )
        west = self.location_manager.get_things_in_direction_from_thing(
            thing, CompassDirection.West, distance
        )
        north = self.location_manager.get_things_in_direction_from_thing(
            thing, CompassDirection.North, distance
        )
        south = self.location_manager.get_things_in_direction_from_thing(
            thing, CompassDirection.South, distance
        )
        center = self.location_manager.get_things_at_location(
            *self.location_manager.get_thing_coordinates(thing)
        )

        return View(north, south, east, west, center)

    def handle_desire(self, desire: Desire):
        desirer = desire.desirer
        if isinstance(desire, EatDesire):
            if not isinstance(desire.food, Food):
                return

            food_x, food_y = self.location_manager.get_thing_coordinates(desire.food)
            des_x, des_y = self.location_manager.get_thing_coordinates(desirer)

            if (
                isinstance(desirer, Person)
                and food_x == des_x
                and food_y == des_y
                and desire.food.Amount >= 1
            ):
                desirer.Stomach += 1
                desire.food.Amount -= 1
            
            logger.debug(f"Person({desirer.id}) has eaten! (Stomach: {desirer.Stomach}, food.Amount: {desire.food.Amount})")
        elif isinstance(desire, MoveDesire):
            self.location_manager.move_thing_in_direction(desire.desirer, desire.direction, desire.count)

    def tick(self):
        desires = []

        for thing in self.location_manager.things.keys():
            if not isinstance(thing, GameObject):
                continue
            desires.extend(thing.tick(self.cull_invisible(self.get_view(thing, 3))))

        random.shuffle(desires)

        for desire in desires:
            self.handle_desire(desire)

    def _init_world(self):

        for _ in range(self.people_start):
            self.add_thing_in_random_location(Person)

        for _ in range(self.food_start):
            self.add_thing_in_random_location(Food)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--debug", action="store_true", default=False, help="Print debug information"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    w = World()

    for _ in range(0, 1000):
        w.tick()
