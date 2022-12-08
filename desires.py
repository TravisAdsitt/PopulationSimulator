from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from game_objects import Food, GameObject

from utils import CompassDirection


class TypesofDesire(Enum):
    Move = "Move"
    Eat = "Eat"


class Desire(ABC):
    def __init__(self, desirer: GameObject, desire_type: TypesofDesire):
        self.desirer = desirer
        self.desire_type = desire_type


class MoveDesire(Desire):
    def __init__(
        self, desirer: GameObject, direction: CompassDirection, count: int = 1
    ):
        super().__init__(desirer, TypesofDesire.Move)
        self.direction = direction
        self.count = count


class EatDesire(Desire):
    def __init__(self, desirer: GameObject, food: Food):
        super().__init__(desirer, TypesofDesire.Eat)
        self.food = food

    @property
    def amount(self):
        if isinstance(self.food, Food):
            return 1
