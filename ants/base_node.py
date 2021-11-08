from threading import Thread
from typing import List
from abc import ABC, abstractmethod
from random import randrange

from .state import State
from .base_communication import BaseCommunication
from .heartbeat import Heartbeat
from .base_config import BaseConfig
from .job import Job, JobStatus
from .message import Message


class BaseNode(ABC, Thread):
    def __init__(
            self,
            initial_config: BaseConfig,
            initial_state: State,
            communication: BaseCommunication,
    ):
        self.node_id = randrange(1, 2**64)
        self.config = initial_config
        self.state = initial_state
        self.heartbeat = Heartbeat(interval=initial_config.heartbeat_interval)
        self.communication = communication

        super().__init__(name=f'Node {self.node_id}', daemon=True)

    @property
    def assigned_jobs_count(self) -> int:
        return len(self.__filter_my_assigned_jobs())

    @abstractmethod
    def add_messages(self) -> List[Message]:
        raise NotImplementedError

    @abstractmethod
    def process_messages(self, messages: List[Message]):
        raise NotImplementedError

    @abstractmethod
    def add_jobs(self) -> List[Job]:
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

    def _filter_jobs_by_status(self, status: JobStatus):
        return list(filter(lambda job: job.status == status, self.state.jobs.values()))

    def __filter_my_assigned_jobs(self) -> List[Job]:
        return list(
            filter(
                lambda job: job.assigned_to == self.node_id,
                self._filter_jobs_by_status(JobStatus.ASSIGNED)
            )
        )

    def __remove_done_jobs(self):
        for job in self._filter_jobs_by_status(JobStatus.DONE):
            del self.state.jobs[job.id]

    def __remove_expired_messages(self):
        for message in self.state.messages.copy().values():
            if message.is_expired:
                del self.state.messages[message.id]

    def run(self):
        for beat_number in self.heartbeat:
            peers_state = self.communication.pull()
            self.__merge_peers_state(peers_state)

            self.completed_jobs(self._filter_jobs_by_status(JobStatus.DONE))

            self.__remove_done_jobs()
            self.__remove_expired_messages()

            self.process_messages(self.state.messages.values())

            self.do_jobs(self.__filter_my_assigned_jobs())

            assigned_jobs = self.assign_to_jobs(self._filter_jobs_by_status(JobStatus.PENDING))
            for job in assigned_jobs:
                job.assign(self.node_id)

            new_jobs = self.add_jobs()
            for new_job in new_jobs:
                if new_job.id in self.state.jobs:
                    continue
                self.state.jobs[new_job.id] = new_job

            new_messages = self.add_messages()
            for new_message in new_messages:
                self.state.messages[new_message.id] = new_message

            self.communication.broadcast(self.state)
