import datetime
from constants.Actions import Action
from constants.constant import *


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

    def __init__(self, player_id, relay_queue, has_logout):
        self.player_id = player_id
        self.opponent = None
        self.hp = Player.max_hp
        self.num_shield = Player.max_shield_number
        self.last_shield_active_time = datetime.datetime.min
        self.shield_health = 0
        self.bullets = Player.max_bullet_number
        self.grenades = Player.max_grenade_number
        self.action = Action.NONE
        self.num_deaths = 0
        self.relay_queue = relay_queue
        self.has_logout = has_logout

    def set_opponent(self, opponent):
        self.opponent = opponent

    def get_status(self, need_shield_time=True):
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
            "num_shield": self.num_shield,
        }

        if not need_shield_time:
            status.pop("shield_time")
        return status

    def process_action(self, action, query_result=None):
        if query_result is None:
            query_result = {}
        if action.value == Action.SHOOT.value:
            self.__process_shoot(query_result)
        elif action.value == Action.RELOAD.value:
            self.__process_reload()
        elif action.value == Action.GRENADE.value:
            self.__process_grenade(query_result)
        elif action.value == Action.SHIELD.value:
            self.__process_shield()
        elif action.value == Action.LOGOUT.value:
            self.__process_logout()
        self.__process_none()

    def correct_status(self, expected_status):
        update_message = {}
        if self.hp != expected_status.get("hp"):
            update_message["health"] = expected_status.get("hp")
            self.hp = expected_status.get("hp")

        if self.bullets != expected_status.get("bullets"):
            update_message["bullets"] = expected_status.get("bullets")
            self.bullets = expected_status.get("bullets")

        if expected_status.get("shield_time") != 0:
            self.last_shield_active_time = datetime.datetime.now() - \
                                        datetime.timedelta(seconds=expected_status.get("shield_time"))

        self.num_shield = expected_status.get("num_shield")
        self.grenades = expected_status.get("grenades")
        self.action = Action(expected_status.get("action"))
        self.num_deaths = expected_status.get("num_deaths")

        if len(update_message) > 0:
            self.relay_queue.put(str({self.player_id: update_message}))

    def check_action(self, action):
        self.action = action
        if action == Action.SHOOT:
            return SHOOT_ERROR_MESSAGE if self.bullets <= 0 else None
        if action == Action.NONE:
            return None
        if action == Action.RELOAD:
            return RELOAD_ERROR_MESSAGE if self.bullets > 0 else None
        if action == Action.GRENADE:
            return GRENADE_ERROR_MESSAGE if self.grenades <= 0 else None
        if action == Action.SHIELD:
            if self.num_shield <= 0:
                return SHIELD_ERROR_MESSAGE
            elif (datetime.datetime.now() - self.last_shield_active_time).total_seconds() < 10:
                return SHIELD_COOLDOWN_MESSAGE
            return None
        return None

    def check_logout(self):
        if self.action == Action.LOGOUT:
            self.relay_queue.put(str({
                self.player_id: {
                    "action": 'logout'
                }
            }))
            self.has_logout.set()

    def __process_reload(self):
        self.bullets = Player.max_bullet_number
        self.relay_queue.put(str({
            self.player_id: {
                "bullets": str(self.bullets).zfill(3)
            }
        }))

    def __process_shoot(self, query_result):
        is_hit = bool(query_result.get(self.player_id))
        self.bullets -= 1

        if is_hit:
            self.opponent.shot()

    def __process_grenade(self, query_result):
        self.grenades -= 1
        is_hit = bool(query_result.get(self.player_id))
        
        if is_hit:
            self.opponent.grenaded()

    def __process_shield(self):
        self.num_shield -= 1
        self.last_shield_active_time = datetime.datetime.now()
        self.shield_health = Player.max_shield_hp

    def __process_logout(self):
        pass

    def __process_none(self):
        pass

    def __is_active_shield(self):
        return (datetime.datetime.now() - self.last_shield_active_time).total_seconds() <= Player.shield_active_time \
               and self.shield_health > 0

    def grenaded(self):
        if self.__is_active_shield():
            # Player shot with 30 shield_hp will lose the shield
            if self.shield_health >= Player.grenade_damage:
                self.shield_health = 0
                return

            # Player shot with less than 30 shield_hp will lose the shield and lose some hp
            self.shield_health = 0
            self.hp -= Player.grenade_damage - self.shield_health
        else:
            self.hp -= Player.grenade_damage
            self.shield_health = 0

        if self.hp <= 0:
            self.__resurge()
        self.relay_queue.put(str({
            self.player_id: {
                "health": str(self.hp).zfill(3)
            }
        }))

    def shot(self):
        if self.__is_active_shield():
            # Player shot with more than or equal to 10 shield_hp
            if self.shield_health >= Player.bullet_damage:
                self.shield_health -= Player.bullet_damage
                return

            # Player shot with less than 10 shield_hp will lose the shield and lose some hp
            else:
                self.shield_health = 0
                self.hp -= Player.bullet_damage - self.shield_health

        else:
            self.hp -= Player.bullet_damage
            self.shield_health = 0

        if self.hp <= 0:
            self.__resurge()

        self.relay_queue.put(str({
            self.player_id: {
                "health": str(self.hp).zfill(3)
            }
        }))

    def __resurge(self):
        self.hp = Player.max_hp
        self.num_shield = Player.max_shield_number
        self.last_shield_active_time = datetime.datetime.min
        self.bullets = Player.max_bullet_number
        self.grenades = Player.max_grenade_number
        self.num_deaths += 1
        self.relay_queue.put(str({
            self.player_id: {
                "bullets": str(self.bullets).zfill(3),
                "health": str(self.hp).zfill(3)
            }
        }))
