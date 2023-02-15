from threading import Thread


class PseudoAI(Thread):

    def __init__(self, metrics_queue, action_queue):
        super().__init__()
        self.metrics_queue = metrics_queue
        self.action_queue = action_queue

    def run(self):
        print("ai is running...")
        while True:
            data = self.metrics_queue.get()
            print("ai passes data: " + str(data))
            self.action_queue.put(data)
            self.action_queue.put('none')
