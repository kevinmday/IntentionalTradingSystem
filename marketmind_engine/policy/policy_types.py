from enum import Enum


class PolicyAction(Enum):
    """
    Policy actions express permission and posture,
    not execution or trading intent.
    """

    ALLOW = "allow"
    WATCH = "watch"
    HOLD = "hold"
    BLOCK = "block"
    ESCALATE = "escalate"
