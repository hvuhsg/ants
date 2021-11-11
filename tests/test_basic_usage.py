from typing import List
from time import sleep

from ants import BaseNode, Job, Message, BaseConfig
from ants.communications import LocalhostCommunication


class Node(BaseNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.results = set()

    def process_messages(self, messages: List[Message]):
        pass

    def add_messages(self) -> List[Message]:
        return []

    def add_jobs(self) -> List[Job]:
        jobs = []
        for i in range(5):
            jobs.append(Job(name='add', payload={'a': i, 'b': i+1}))
        return jobs

    def assign_to_jobs(self, pending_jobs: List[Job]) -> List[Job]:
        return pending_jobs[:1]

    def do_jobs(self, my_assigned_jobs: List[Job]):
        for job in my_assigned_jobs:
            job.set_result(job.payload['a'] + job.payload['b'])

    def completed_jobs(self, done_jobs: List[Job]):
        for job in done_jobs:
            self.results.add(job.result)


def test_basic_use():
    nodes = []
    for i in range(3):
        node = Node(initial_config=BaseConfig(heartbeat_interval=0.5), communication=LocalhostCommunication())
        node.start()
        nodes.append(node)
        sleep(0.1)

    sleep(3)
    assert nodes[0].results == {1, 3, 5, 7}
    for node in nodes:
        node.shutdown()
