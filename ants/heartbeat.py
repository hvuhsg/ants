from time import sleep


class Heartbeat:
    def __init__(self, interval: int):
        self.interval = interval
        self.__heartbeat_counter = 0

    def __iter__(self):
        while True:
            self.__heartbeat_counter += 1
            yield self.__heartbeat_counter
            sleep(self.interval)
