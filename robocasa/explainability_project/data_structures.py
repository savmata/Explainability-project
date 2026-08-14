from dataclasses import dataclass


@dataclass
class action:
    description: str
    type: str


@dataclass
class task:
    description: str
    type: str
    actions: list[action]


@dataclass
class plan:
    tasks: list[task]


@dataclass
class item:
    name: str
    size: str  # can be small, medium, large
    position: str  # can be left, middle, right
    isFragile: bool
    #  more item attributes can be added here
