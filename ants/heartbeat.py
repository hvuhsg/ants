from time import sleep


class Heartbeat:
    def __init__(self, interval: float):
        self.interval = interval
        self.__heartbeat_counter = 0
        self.__run = True

    def __iter__(self):
        while self.__run:
            self.__heartbeat_counter += 1
            yield self.__heartbeat_counter
            sleep(self.interval)

    def stop(self):
        self.__run = False
