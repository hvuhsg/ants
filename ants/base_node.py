from threading import Thread
from typing import List
from abc import ABC, abstractmethod
from random import randrange

from .state import State
from .base_communication import BaseCommunication
from .heartbeat import Heartbeat
from .base_config import BaseConfig
from .job import Job


class BaseNode(ABC, Thread):
    def __init__(
            self,
            initial_config: BaseConfig,
            initial_state: State,
            communication: BaseCommunication,
    ):
        self.node_id = randrange(1, 9999999999)
        self.config = initial_config
        self.state = initial_state
        self.heartbeat = Heartbeat(interval=initial_config.heartbeat_interval)
        self.communication = communication

        super().__init__(name=f'Node {self.node_id}', daemon=True)

    @property
    def assigned_jobs_count(self) -> int:
        return len(list(filter(lambda job: job.assigned_to == self.node_id, self.state.assigned_jobs)))

    @abstractmethod
    def add_jobs(self):
        raise NotImplementedError

    @abstractmethod
    def assign_to_jobs(self, pending_jobs: List[Job]) -> List[Job]:
        raise NotImplementedError

    @abstractmethod
    def do_jobs(self, my_assigned_jobs: List[Job]):
        raise NotImplementedError

    @abstractmethod
    def completed_jobs(self, done_jobs: List[Job]):
        raise NotImplementedError

    def __merge_peers_state(self, peers_state: List[State]):
        for peer_state in peers_state:
            self.state.merge(peer_state)

    def __filter_my_assigned_jobs(self) -> List[Job]:
        return list(filter(lambda job: job.assigned_to == self.node_id, self.state.assigned_jobs))

    def __remove_done_jobs(self):
        for job in self.state.done_jobs:
            self.state.remove_job(job.id)

    def run(self):
        for beat_number in self.heartbeat:
            peers_state = self.communication.pull()
            self.__merge_peers_state(peers_state)

            self.completed_jobs(self.state.done_jobs)
            self.__remove_done_jobs()
            self.do_jobs(self.__filter_my_assigned_jobs())
            assigned_jobs = self.assign_to_jobs(self.state.pending_jobs)
            for job in assigned_jobs:
                job.assign(self.node_id)

            new_jobs = self.add_jobs()
            for new_job in new_jobs:
                self.state.add_job(new_job)

            self.communication.broadcast(self.state)
