from threading import Thread
from time import sleep


def cron_sleep_one_day(func):

    def wrapper(*args):

        while True:

            t = Thread(target=func, args=args, daemon=True)
            t.start()
            sleep(86400)

    return wrapper
