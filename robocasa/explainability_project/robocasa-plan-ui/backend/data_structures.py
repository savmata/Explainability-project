from dataclasses import dataclass


@dataclass
class Action:
    description: str
    type: str


@dataclass
class Item:
    name: str
    size: str  # can be small, medium, large
    position: str  # can be left, middle, right
    isFragile: bool
    #  more item attributes can be added here


@dataclass
class Task:
    description: str
    type: str
    actions: list[Action]
    target: Item | None  # The item that the task is performed on. Can be None if the task is not performed on an item.


@dataclass
class Plan:
    tasks: list[Task] 


@dataclass
class MismatchEntry:
    message:     str
    explanation: str
