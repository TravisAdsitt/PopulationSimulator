from dataclasses import dataclass, field
from typing import List, Tuple
from enum import Enum
from abc import ABC, abstractclassmethod
import random

class IDCreator:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(IDCreator, cls).__new__(cls)
        return cls.instance
    
    def get_next_id(self):
        if not hasattr(self, "id"):
            self.id = 0

        new_id = self.id
        self.id += 1
        return new_id

class CompassDirection(Enum):
    North = "North"
    South = "South"
    East = "East"
    West = "West"

    @classmethod
    def step_coordinates_in_direction(cls, x: int, y: int, direction: "CompassDirection", count: int = 1):
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

class TypesofDesire(Enum):
    Move = "Move"

class Desire:
    pass

@dataclass
class MoveDesire:
    direction: CompassDirection
    count: int = 1
    type: TypesofDesire = TypesofDesire.Move
    

@dataclass
class View:
    North: List = field(default_factory=list)
    South: List = field(default_factory=list)
    East: List = field(default_factory=list)
    West: List = field(default_factory=list)

class GameObject(ABC):
    def __init__(self):
        self.id = IDCreator().get_next_id()
        self._init_attributes()
    
    def __hash__(self):
        return self.id

    @abstractclassmethod
    def _init_attributes(self):
        raise NotImplemented()


class Person(GameObject):
    def _init_attributes(self):
        self.HP = 100
        self.Energy = 100
        self.Stomach = 100
        self.Metabolism = 0.2
        self.Desires = list()

    def tick(self, view: View):
        pass
    
    def visible(self):
        return True

class Food(GameObject):
    def _init_attributes(self):
        self.MaxAmount = 100
        self.Amount = 100
        self.RegenRate = 1.5

    def tick(self):
        if self.Amount < self.MaxAmount:
            self.Amount += (self.MaxAmount * self.RegenRate)

    def visible(self):
        return bool(self.Amount > (self.MaxAmount * 0.2))

class LocationManager:
    def __init__(self, max_x: int = -1, max_y: int = -1):
        self.locations = {}
        self.things = {}
        self.max_x = max_x
        self.max_y = max_y

        if self.max_x < 1:
            self.max_x = random.randint(1,100)
        if self.max_y < 1:
            self.max_y = random.randint(1,100)
    
    def get_location_key(self, x: int, y: int):
        location_x = x % self.max_x
        location_y = y % self.max_y

        return f"{location_x},{location_y}"
    
    def get_thing_coordinates(self, thing: object):
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
        return self.locations[location_key]

    def add_thing(self, new_thing: object, x: int, y: int):
        location_key = self.get_location_key(x, y)

        if location_key not in self.locations:
            self.locations[location_key] = []
        if new_thing not in self.things:
            self.things[new_thing] = location_key
        
        for thing in self.locations[location_key]:
            if type(thing) == type(new_thing):
                raise Exception("Cannot place that there!")
        
        self.locations[location_key].append(new_thing)
    
    def remove_thing(self, thing: object, x: int = -1, y: int = -1):
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
    
    def move_thing_in_direction(self, thing: object, direction: CompassDirection, count: int = 1):
        if thing not in self.things:
            raise Exception("Cannot find that thing!")
        
        x, y = self.get_thing_coordinates(thing)
        stepped_x, stepped_y = CompassDirection.step_coordinates_in_direction(x, y, direction, count)
        
        self.remove_thing(thing)
        try:
            # If this raises then that spot is taken
            self.add_thing(thing, stepped_x, stepped_y)
        except:
            # If it is taken then go back to where we were
            self.add_thing(thing, x, y)

    def get_things_in_direction_from_thing(self, thing: object, direction: CompassDirection, distance: int = 1):
        ret_val = []

        if thing not in self.things:
            return ret_val
        
        x, y = self.get_thing_coordinates(thing)

        for _ in range(distance):
            new_x, new_y = CompassDirection.step_coordinates_in_direction(x, y, direction)
            ret_val.extend(self.get_things_at_location(new_x, new_y))
        
        return ret_val


class World:
    def __init__(self):
        self.world_width = 100
        self.world_height = 100

        self.location_manager = LocationManager(self.world_width, self.world_height)

        self.people_start = 5
        self.food_start = 10

        self.init_world()
    
    def add_thing_in_random_location(self, thing: object, max_retry: int = 50):
        added = False
        retry = 0

        while not added and retry < max_retry:
            random_x = random.randint(0, self.world_width - 1)
            random_y = random.randint(0, self.world_height - 1)
            # If the following raises, it is because there is a thing at this location already
            # try:
            self.location_manager.add_thing(thing(), random_x, random_y)
            added = True
            # except:
            #     retry += 1
            #     continue

    def init_world(self):
        
        for _ in range(self.people_start):
            self.add_thing_in_random_location(Person)
        
        for _ in range(self.food_start):
            self.add_thing_in_random_location(Food)
        


        
if __name__ == "__main__":
    World()

    
