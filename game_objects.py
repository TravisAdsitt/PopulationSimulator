from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import random
from typing import List, Tuple
from desires import Desire, EatDesire, MoveDesire
from utils import CompassDirection, View
import logging

logger = logging.getLogger(__name__)


class IDCreator:
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(IDCreator, cls).__new__(cls)
        return cls.instance

    def get_next_id(self):
        if not hasattr(self, "id"):
            self.id = 0

        new_id = self.id
        self.id += 1
        return new_id


class GameObject(ABC):
    def __init__(self):
        self.id = IDCreator().get_next_id()
        self.Desires = list()
        self._init_attributes()

    def __hash__(self):
        return self.id

    @abstractmethod
    def _init_attributes(self):
        raise NotImplementedError()

    @abstractmethod
    def tick(self, view: View) -> List[Desire]:
        raise NotImplementedError()

    @abstractmethod
    def visible(self) -> bool:
        raise NotImplementedError()


class MovableGameObject(GameObject):
    def __init__(self):
        self.Energy = 100
        self.EnergyMax = 100
        self.Metabolism = 0.5

        super().__init__()

    def moved(self, count: int = 1):
        self.Energy -= self.Metabolism * count


class Person(MovableGameObject):
    def _init_attributes(self):
        self.StomachMax = 100
        self.Stomach = self.StomachMax
        
        self.Metabolism = 0.2

    @property
    def alive(self):
        if self.Energy > 0 or self.Stomach > 0:
            return True
        else:
            return False


    def look_for_food(self, view: View):
        list_of_directions_and_things = [(CompassDirection.Center, view.Center), (CompassDirection.North, view.North), (CompassDirection.South, view.South), (CompassDirection.East, view.East), (CompassDirection.West, view.West)]
        
        for direction, thing_list in list_of_directions_and_things:
            for thing in thing_list:
                if isinstance(thing, Food):
                    logger.debug("Person found food!")
                    return (thing, direction)
        
        return (None, None)

    def tick(self, view: View) -> List[Desire]:
        ret_desires = []
        food_obj, direction_for_food = self.look_for_food(view)
        
        if self.Energy < self.EnergyMax and self.Stomach > 0:
            remaining_stomach = self.Stomach
            energy_ullage = self.EnergyMax - self.Energy

            exchanged_value = min([remaining_stomach, energy_ullage])

            self.Stomach -= exchanged_value
            self.Energy += exchanged_value

        if self.Energy <= 0:
            self.Energy = 0
            return ret_desires

        if direction_for_food and direction_for_food == CompassDirection.Center:
            logger.debug(f"Person({self.id}) desires to eat!")
            ret_desires.append(EatDesire(self, food_obj))
        elif direction_for_food:
            logger.debug(f"Person({self.id}) sees food and wants it!")
            ret_desires.append(MoveDesire(self, direction_for_food))
        else:
            logger.debug(f"Person({self.id}) desires to move!")
            ret_desires.append(MoveDesire(self, CompassDirection.get_random_direction()))

        return ret_desires

    def visible(self):
        return True


class Food(GameObject):
    def _init_attributes(self):
        self.MaxAmount = 100
        self.Amount = self.MaxAmount
        self.RegenRate = 0.01

    def tick(self, view: View) -> List[Desire]:
        if self.Amount < self.MaxAmount:
            self.Amount += self.MaxAmount * self.RegenRate
        
        return []

    def visible(self):
        return bool(self.Amount > (self.MaxAmount * 0.2))



