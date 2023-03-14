from enum import Enum

class Action(Enum):
    NONE = 'none'
    SHOOT = 'shoot'
    RELOAD = 'reload'
    GRENADE = 'grenade'
    SHIELD = 'shield'
    LOGOUT = 'logout'
    INACTIVE = 'inactive'
