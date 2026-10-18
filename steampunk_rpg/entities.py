from dataclasses import dataclass


@dataclass
class Entity:
    name: str
    position: tuple[int, int]
    color: tuple[int, int, int]


@dataclass
class Player(Entity):
    max_health: int = 30
    health: int = 30
    attack: int = 10


@dataclass
class Mechanic(Entity):
    pass


@dataclass
class Sentinel(Entity):
    max_health: int = 20
    health: int = 20
    attack: int = 6

    @property
    def alive(self):
        return self.health > 0
