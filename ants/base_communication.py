from typing import List
from abc import ABC, abstractmethod

from .state import State


class BaseCommunication(ABC):

    @abstractmethod
    def pull(self) -> List[State]:
        """ Pull sent data from other nodes
        :return: list of State objects
        """
        raise NotImplementedError

    @abstractmethod
    def broadcast(self, state):
        """ Send my state to peers
        can be all of them, just connected ones or even geo close ones (if using bluetooth)
        :param state: state of my node
        """
        raise NotImplementedError
