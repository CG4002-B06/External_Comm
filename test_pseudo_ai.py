from threading import Thread


class PseudoAI(Thread):

    def __init__(self, metrics_queue, action_queue):
        super().__init__()
        self.metrics_queue = metrics_queue
        self.action_queue = action_queue

    def run(self):
        while True:
            data = self.metrics_queue.get()
            self.action_queue.put(data)
