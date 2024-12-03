import threading
import time
import datetime
from database_driver import *

class Scheduler(threading.Thread):
    """
    Class to control the scheduler daemon thread for executing future posts and other tasks
    """

    def __init__(self, name):
        super().__init__()
        self.name = name
        self.daemon = True  # Set the thread as a daemon thread

    def run(self):
        while True:
            self.execute_queued_tasks()
            time.sleep(60)  # Wait for 60 seconds

    def execute_queued_tasks(self):
        # Refresh the queue from the database and call the functions to execute those tasks.
        print("Executing scheduled actions...")
        print("Tread function started at : " + str(datetime.datetime.now()))
        future_post_list = get_future_posts()
        for post in future_post_list:
            print("post : " + str(post.id) + " : " + post.txt)
            # if (post.queue_datetime < datetime.datetime.now() and post.queued == True):
            #     call Driver.create_skeet() (method to post with details from post object)
