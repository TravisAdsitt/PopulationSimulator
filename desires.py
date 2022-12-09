from abc import ABC
from utils import CompassDirection


class Desire(ABC):
    def __init__(self, desirer: object):
        self.desirer = desirer


class MoveDesire(Desire):
    def __init__(self, desirer: object, direction: CompassDirection, count: int = 1):
        super().__init__(desirer)
        self.direction = direction
        self.count = count


class EatDesire(Desire):
    def __init__(self, desirer: object, food: object):
        super().__init__(desirer)
        self.food = food
