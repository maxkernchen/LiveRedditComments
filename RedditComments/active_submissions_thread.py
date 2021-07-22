import time
from threading import Thread
from . import active_submissions

class ActiveSubmissionsThread(Thread):

    def __init__(self, interval=5*60):
        self.interval = interval
        self.thread = Thread(target=self.run)
        self.thread.daemon = True

    def run(self):
        while True:
            active_submissions.get_active_submissions()
            time.sleep(self.interval)