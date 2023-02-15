import datetime
from constants.Actions import Action
from constants.player_constant import *

class Player:
    # basic status of players upon start or resurge
    max_hp = 100
    max_shield_hp = 30
    shield_active_time = 10
    max_shield_number = 3
    grenade_damage = 30
    max_grenade_number = 2
    bullet_damage = 10
    max_bullet_number = 6

    def __init__(self):
        self.opponent = None
        self.hp = Player.max_hp
        self.num_shield = Player.max_shield_number
        self.last_shield_active_time = datetime.datetime.min
        self.shield_health = 0
        self.bullets = Player.max_bullet_number
        self.grenades = Player.max_grenade_number
        self.action = Action.NONE
        self.num_deaths = 0

    def __str__(self):
        return "Player has hp: {}, grenade: {}, shield: {}, bullet: {} and action: {}. You have died {} times".format(
            self.hp, self.grenades, self.num_shield, self.bullets, self.action, self.num_deaths)

    def set_opponent(self, opponent):
        self.opponent = opponent

    def get_status(self):
        # To calculate the cooldown
        second_diff = (datetime.datetime.now() - self.last_shield_active_time).total_seconds()
        shield_remain_time = Player.shield_active_time - second_diff if 0 <= second_diff <= Player.shield_active_time else 0

        self.shield_health = self.shield_health if self.__is_active_shield() else 0
        status = {
            "hp": self.hp,
            "action": self.action.value,
            "bullets": self.bullets,
            "grenades": self.grenades,
            "shield_time": shield_remain_time,
            "shield_health": self.shield_health,
            "num_deaths": self.num_deaths,
            "num_shield": self.num_shield
        }
        return status

    def __resurge(self):
        self.hp = Player.max_hp
        self.num_shield = Player.max_shield_number
        self.last_shield_active_time = datetime.datetime.min
        self.bullets = Player.max_bullet_number
        self.grenades = Player.max_grenade_number
        self.action = Action.NONE
        self.num_deaths += 1

    def process_action(self, action):
        if action == Action.RELOAD.value:
            return self.__process_reload()
        elif action == Action.SHOOT.value:
            return self.__process_shoot()
        elif action == Action.GRENADE.value:
            return self.__process_grenade()
        elif action == Action.SHIELD.value:
            return self.__process_shield()
        elif action == Action.LOGOUT.value:
            return self.__process_logout()
        return self.__process_none()

    def correct_status(self, expected_status):
        self.hp = expected_status.get("hp")
        self.num_shield = expected_status.get("num_shield")
        self.bullets = expected_status.get("bullets")
        self.grenades = expected_status.get("grenades")
        self.action = Action(expected_status.get("action"))
        self.num_deaths = expected_status.get("num_deaths")
        if expected_status.get("shield_time") != 0:
            self.last_shield_active_time = datetime.datetime.now() - \
                                       datetime.timedelta(seconds=expected_status.get("shield_time"))

    def __process_reload(self):
        result = {
            "action": Action.RELOAD.value
        }
        self.action = Action.RELOAD

        if self.bullets > 0: # Send warning message
            result["invalid_action"] = RELOAD_ERROR_MESSAGE
        else:
            self.bullets = Player.max_bullet_number
        return result

    def __process_shoot(self):
        # TODO: figure out if the shoot is a hit
        result = {
            "action": Action.SHOOT.value,
            "shot": True
        }
        self.action = Action.SHOOT

        if self.bullets <= 0:  # Send warning message
            result["invalid_action"] = SHOOT_ERROR_MESSAGE
        else:
            self.bullets -= 1
            self.opponent.shot()

        return result

    def __process_grenade(self):
        result = {
            "action": Action.GRENADE.value
        }
        self.action = Action.GRENADE

        if self.grenades <= 0: # Send warning message
            result["invalid_action"] = GRENADE_ERROR_MESSAGE
        else:
            self.grenades -= 1
            self.opponent.grenaded()

        return result

    def __process_shield(self):
        result = {
            "action": Action.SHIELD.value
        }
        self.action = Action.SHIELD

        if self.num_shield <= 0: # Send warning message
            result["invalid_action"] = SHIELD_ERROR_MESSAGE
        elif (datetime.datetime.now() - self.last_shield_active_time).total_seconds() <= 10: # Send warning message
            result["invalid_action"] = SHIELD_COOLDOWN_MESSAGE
        else:
            self.num_shield -= 1
            self.last_shield_active_time = datetime.datetime.now()
            self.shield_health = Player.max_shield_hp
        return result

    def __process_logout(self):
        result = {
            "action": Action.LOGOUT.value
        }
        self.action = Action.LOGOUT
        return result

    def __process_none(self):
        result = {
            "action": Action.NONE.value
        }
        self.action = Action.NONE
        return result

    def __is_active_shield(self):
        return (datetime.datetime.now() - self.last_shield_active_time).total_seconds() <= Player.shield_active_time \
               and self.shield_health > 0

    def grenaded(self):
        if self.__is_active_shield():
            if self.shield_health >= Player.grenade_damage:  # Player shot with 30 shield_hp will lose the shield
                self.shield_health = 0
                self.num_shield -= 1
            else:  # Player shot with less than 30 shield_hp will lose the shield and lose some hp
                self.shield_health = 0
                self.num_shield -= 1
                self.hp -= Player.grenade_damage - self.shield_health
        else:
            self.shield_health = 0
            self.hp -= Player.grenade_damage

        if self.hp <= 0:
            self.__resurge()

    def shot(self):
        if self.__is_active_shield():
            if self.shield_health == Player.bullet_damage:  # Player shot with 10 shield_hp will lose the shield
                self.shield_health = 0
                self.num_shield -= 1
            elif self.shield_health < Player.bullet_damage:  # Player shot with less than 10 shield_hp will lose the shield and lose some hp
                self.shield_health = 0
                self.num_shield -= 1
                self.hp -= Player.bullet_damage - self.shield_health
            else:  # Player shot with more than 10 shield_hp
                self.shield_health -= Player.bullet_damage
        else:
            self.hp -= Player.bullet_damage
            self.shield_health = 0

        if self.hp <= 0:
            self.__resurge()
