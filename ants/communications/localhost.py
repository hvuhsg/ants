from typing import List

from ..base_communication import BaseCommunication
from ..state import State


class LocalhostCommunication(BaseCommunication):
    NODES = 0
    nodes = {}

    def __init__(self):
        self.node_id = self.NODES
        self.NODES += 1

    def pull(self) -> List[State]:
        nodes_copy = self.nodes.copy()
        nodes_copy.pop(self.node_id, None)
        return list(nodes_copy.values())

    def broadcast(self, state):
        self.nodes[self.node_id] = state
