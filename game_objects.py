from abc import ABC, abstractmethod
from typing import List
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
        super().__init__()

    def moved(self, count: int = 1):
        self.Energy -= 5 * count


class Person(MovableGameObject):
    def _init_attributes(self):
        self.HP = 100
        self.Stomach = 100
        self.Metabolism = 0.2

    def tick(self, view: View) -> List[Desire]:
        ret_desires = []
        food_obj, direction_for_food = view.get_direction_for_thing(Food)

        if direction_for_food and direction_for_food == CompassDirection.Center:
            logger.debug("Person desires to eat!")
            ret_desires.append(EatDesire(self, food_obj))
        elif direction_for_food:
            logger.debug("Person desires to move!")
            ret_desires.append(MoveDesire(self, direction_for_food))

        return ret_desires

    def visible(self):
        return True


class Food(GameObject):
    def _init_attributes(self):
        self.MaxAmount = 5
        self.Amount = 5
        self.RegenRate = 0.5

    def tick(self, view: View) -> List[Desire]:
        if self.Amount < self.MaxAmount:
            self.Amount += self.MaxAmount * self.RegenRate

    def visible(self):
        return bool(self.Amount > (self.MaxAmount * 0.2))
