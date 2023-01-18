from enum import Enum

class Action(Enum):
    NONE = 'none'
    SHOOTING = 'shooting'
    SHOT = 'shot'
    RELOAD = 'reload'
    GRENADING = 'grenading'
    GRENADED = 'grenaded'
    SHIELD = 'shield'
    LOGOUT = 'logout'
