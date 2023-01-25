import datetime
import json
from Actions import Action 

class Player:

    #basic status of players upon start or resurge
    max_hp = 100
    shield_max_hp = 30
    shield_active_time = 10
    max_shield_number = 3
    grenade_damage = 30
    max_grenade_number = 2
    bullet_damage = 10
    max_bullet_number = 6
    

    def __init__(self):
        self.hp = Player.max_hp
        self.remain_shield = Player.max_shield_number
        self.last_shield_active_time = datetime.datetime.min
        self.shield_remain_hp = Player.shield_max_hp
        self.remain_bullet = Player.max_bullet_number
        self.remain_grenade = Player.max_grenade_number
        self.action = Action.NONE
        self.num_death = 0
    
    def __str__(self):
        return "Player has hp: {}, grenade: {}, shield: {}, bullet: {} and action: {}. You have died {} times".format(
            self.hp, self.remain_grenade, self.remain_shield, self.remain_bullet, self.action, self.num_death)

    def get_status(self):
        status = {
            "hp": self.hp,
            "action": self.action,
            "bullets": self.remain_bullet,
            "grenades": self.remain_bullet,
            "shield_time": self.shield_active_time,
            "shield_health": self.shield_remain_hp,
            "num_deaths": self.num_death,
            "num_shield": self.remain_shield
        }
        return status

    def __resurge(self):
        self.hp = Player.max_hp
        self.remain_shield = Player.max_shield_number
        self.last_shield_active_time = datetime.datetime.min
        self.remain_bullet = Player.max_bullet_number
        self.remain_grenade = Player.max_grenade_number
        self.action = Action.NONE
        self.num_death += 1

    def process_action(self, action):
        if self.action == Action.LOGOUT:
            return

        
        if action == Action.RELOAD:
            self.__process_reload()

        elif action == Action.SHOOTING:
            self.__process_shooting()

        elif action == Action.SHOT:
            self.__process_shot()
        
        elif action == Action.GRENADING:
            self.__process_grenading()
        
        elif action == Action.GRENADED:
            self.__process_grenaded()
        
        elif action == Action.SHIELD:
            self.__process_shield()
        
        elif action == Action.LOGOUT:
            self.action == Action.LOGOUT
        
        else:
            self.action == Action.NONE

    def status_check(self, expected_status):
        #TODO: check and correct players' status
        #return true if update is needed. Otherwise, return false
        flag = False
        
        for key, value in expected_status.items():
            if self.get_status.get(key) != value: # If current status is not equal to the expected status
                flag = True
        
        return flag

    def __process_reload(self):
        if self.remain_bullet > 0: # Send warning message
            return
        self.remain_bullet = Player.max_bullet_number
        self.action = Action.RELOAD
    
    def __process_shooting(self): 
        if self.remain_bullet <= 0: # Send warning message
            return
        self.remain_bullet -= 1
        self.action = Action.SHOOTING

    def __process_shot(self):
        if self.hp <= Player.bullet_damage:
            self.__resurge()

        if self.shield_remain_hp == Player.bullet_damage: # Player shot with 10 shield_hp will lose the shield
            self.shield_remain_hp = 0
            self.remain_shield -= 1
            self.action = Action.SHOT
        elif self.shield_remain_hp < Player.bullet_damage: # Player shot with less than 10 shield_hp will lose the shield and lose some hp
            self.shield_remain_hp = 0
            self.remain_shield -= 1
            self.action = Action.SHOT
            self.hp -= Player.bullet_damage - self.shield_remain_hp
        elif self.shield_remain_hp > Player.bullet_damage: # Player shot with more than 10 shield_hp
            self.shield_remain_hp -= Player.bullet_damage 
            self.action = Action.SHOT

        else:
            self.hp -= Player.bullet_damage
            self.action = Action.SHOT
        
    def __process_grenading(self):
        if self.remain_grenade <= 0:
            return
        self.remain_grenade -= 1
        self.action = Action.GRENADING
      
    def __process_grenaded(self):
        if self.hp <= Player.grenade_damage:
            self.__resurge()
             
        if self.shield_remain_hp == Player.grenade_damage: # Player shot with 30 shield_hp will lose the shield
            self.shield_remain_hp = 0
            self.remain_shield -= 1
            self.action = Action.GRENADED
        elif self.shield_remain_hp < Player.grenade_damage: # Player shot with less than 30 shield_hp will lose the shield and lose some hp
            self.shield_remain_hp = 0
            self.remain_shield -= 1
            self.hp -= Player.grenade_damage - self.shield_remain_hp
            self.action = Action.GRENADED
        
        else:  
            self.hp -= Player.grenade_damage 
            self.action = Action.GRENADED
    
    def __process_shield(self):
        if self.remain_shield <= 0 or (datetime.datetime.now() - self.last_shield_active_time).total_seconds() <= 10:
            return
        self.remain_shield -= 1
        self.action = Action.SHIELD
        self.last_shield_active_time = datetime.datetime.now()
        self.shield_remain_hp = Player.shield_max_hp
        

    
    
