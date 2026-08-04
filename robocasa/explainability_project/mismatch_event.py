from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import time


class MismatchCategory(Enum):
    SPATIAL = "spatial"
    SELECTIVE = "selective"
    SEQUENTIAL = "sequential"
    TEMPORAL = "temporal"


class Severity(Enum):
    LOW = "low"     # informational, user probably doesn't need to act
    MEDIUM = "medium"  # worth noting, robot made a judgement call
    HIGH = "high"    # user should verify or intervene


@dataclass
class MismatchEvent:
    category:    MismatchCategory
    severity:    Severity
    belief:      "ObjectBelief"       # what the robot perceived
    desire:      "Goal"               # which goal drove the decision
    intention:   "IntentionResult"    # what the robot committed to
    description: str                  # one-line machine description
    timestamp:   float = field(default_factory=time.time)


@dataclass
class WorldContext:
    # items the robot has loaded so far, in order
    load_history:     list[str] = field(default_factory=list)
    # items the user placed manually before the robot ran
    user_placed:      dict[str, str] = field(default_factory=dict)  # name→rack
    # items explicitly skipped this episode
    skipped_items:    list[str] = field(default_factory=list)
    # timestep of the last completed action
    last_action_step: int = 0
    # current timestep
    current_step:     int = 0
    # threshold: steps of inactivity before a temporal mismatch fires
    pause_threshold:  int = 50
