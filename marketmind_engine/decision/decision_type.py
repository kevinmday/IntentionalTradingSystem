from enum import Enum


class DecisionType(Enum):
    NO_ACTION = "no_action"
    ALLOW_BUY = "allow_buy"
    BLOCKED = "blocked"
    OVERRIDDEN = "overridden"
    DEFERRED = "deferred"