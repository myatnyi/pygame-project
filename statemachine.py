from enum import Enum


class StateMachine(Enum):
    IDLE = 0
    WALK = 1
    ATTACK = 2
    SHIELD = 3
    STUN = 4
    DEATH = 5