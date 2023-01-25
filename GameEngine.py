from threading import Thread
from Player import Player

class GameEngine(Thread):

    def __init__(self, action_queue, eval_queue, message_queue):
        self.players = [Player(), Player()]
        self.action_queue = action_queue
        self.eval_queue = eval_queue
        self.message_queue = message_queue

    
    def run(self):
        while True:
            new_action = action_queue.get()
            #TODO: figure out correct player performing the action,
            # and update state

            




    
    