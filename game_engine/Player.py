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
        self.shield_health = Player.max_shield_hp
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
        status = {
            "hp": self.hp,
            "action": self.action,
            "bullets": self.bullets,
            "grenades": self.bullets,
            "shield_time": self.shield_active_time,
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
        if action == Action.RELOAD:
            return self.__process_reload()
        elif action == Action.SHOOT:
            return self.__process_shoot()
        elif action == Action.GRENADE:
            return self.__process_grenade()
        elif action == Action.SHIELD:
            return self.__process_shield()
        elif action == Action.LOGOUT:
            return self.__process_logout()
        return self.__process_none()

    def correct_status(self, expected_status):
        self.hp = expected_status.get("hp")
        self.num_shield = expected_status.get("num_shield")
        self.bullets = expected_status.get("bullets")
        self.grenades = expected_status.get("grenades")
        self.action = expected_status.get("action")
        self.num_deaths = expected_status.get("num_deaths")
        self.last_shield_active_time = datetime.datetime.now() - \
                                       datetime.timedelta(seconds=expected_status.get("shield_time"))

    def __process_reload(self):
        result = {
            "action": Action.RELOAD
        }

        if self.bullets > 0:
            result["invalid_action"] = RELOAD_ERROR_MESSAGE
        else:
            self.bullets = Player.max_bullet_number
            self.action = Action.RELOAD
        return result

    def __process_shoot(self):
        # TODO: figure out if the shoot is a hit
        result = {
            "action": Action.RELOAD,
            "shot": True
        }
        if self.bullets <= 0:  # Send warning message
            result["invalid_action"] = SHOOT_ERROR_MESSAGE
        else:
            self.bullets -= 1
            self.action = Action.SHOOT
            self.opponent.shot()

        return result

    def __process_grenade(self):
        result = {
            "action": Action.GRENADE
        }
        if self.grenades <= 0:
            result["invalid_action"] = GRENADE_ERROR_MESSAGE
        else:
            self.grenades -= 1
            self.action = Action.GRENADE
            self.opponent.grenaded()
        return result

    def __process_shield(self):
        result = {
            "action": Action.SHIELD
        }
        if self.num_shield <= 0:
            result["invalid_action"] = SHIELD_ERROR_MESSAGE
        elif (datetime.datetime.now() - self.last_shield_active_time).total_seconds() <= 10:
            result["invalid_action"] = SHIELD_COOLDOWN_MESSAGE
        else:
            self.num_shield -= 1
            self.action = Action.SHIELD
            self.last_shield_active_time = datetime.datetime.now()
            self.shield_health = Player.max_shield_hp
        return result

    def __process_logout(self):
        result = {
            "action": Action.LOGOUT
        }
        self.action == Action.LOGOUT
        return result

    def __process_none(self):
        result = {
            "action": Action.NONE
        }
        self.action == Action.NONE
        return result

    def grenaded(self):
        if self.hp <= Player.grenade_damage:
            self.__resurge()

        if self.shield_health == Player.grenade_damage:  # Player shot with 30 shield_hp will lose the shield
            self.shield_health = 0
            self.num_shield -= 1
        elif self.shield_health < Player.grenade_damage:  # Player shot with less than 30 shield_hp will lose the shield and lose some hp
            self.shield_health = 0
            self.num_shield -= 1
            self.hp -= Player.grenade_damage - self.shield_health

        else:
            self.hp -= Player.grenade_damage

    def shot(self):
        if self.hp <= Player.bullet_damage:
            self.__resurge()

        if self.shield_health == Player.bullet_damage:  # Player shot with 10 shield_hp will lose the shield
            self.shield_health = 0
            self.num_shield -= 1
        elif self.shield_health < Player.bullet_damage:  # Player shot with less than 10 shield_hp will lose the shield and lose some hp
            self.shield_health = 0
            self.num_shield -= 1
            self.hp -= Player.bullet_damage - self.shield_health
        elif self.shield_health > Player.bullet_damage:  # Player shot with more than 10 shield_hp
            self.shield_health -= Player.bullet_damage

        else:
            self.hp -= Player.bullet_damage
