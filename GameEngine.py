from threading import Thread
from Player import Player


class GameEngine(Thread):

    def __init__(self, eval_client, action_queue, visualizer_queue):
        self.players = [Player(), Player()]
        self.action_queue = action_queue
        self.visualizer_queue = visualizer_queue
        self.eval_client = eval_client
    

    def __process_action(self, action):
        #TODO: add action process login
        pass
    

    def __status_check_and_correct(self, status_after_process, expected_status):
        #TODO: correct status from eval server
        pass
        
    

    def run(self):
        while True:
            new_action = action_queue.get()
            status_after_process = self.__process_action(action)
            expected_status = self.eval_client.send_and_receive(status_after_process)
            self.__status_check_and_correct(status_after_process, expected_status)
            
            #TODO: protocol and payload format communicating with MQ
            self.visualizer_queue.put()



            




    
    