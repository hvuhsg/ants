from typing import List
from time import sleep
from random import choice

from pythonping import ping
from ants import BaseNode, Job, State
from ants.communications import SocketCommunication

from config import Config


HEARTBEAT_INTERVAL = 30


class Node(BaseNode):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.completed_jobs_set = set()

    def completed_jobs(self, done_jobs: List[Job]):
        for job in done_jobs:
            print(f'Log of {self.node_id}', job.name, job.payload, job.result)
            self.completed_jobs_set.add(job)

    def add_jobs(self) -> List[Job]:
        jobs = []
        for i in range(2):
            random_peer = choice(list(self.communication.peers))
            jobs.append(Job(name='ping', payload={'ip': random_peer[0]}))
        return jobs  # Add job to ping peer ip

    def assign_to_jobs(self, pending_jobs: List[Job]):
        print('pending jobs count', len(pending_jobs))
        allowed_assignment = self.config.max_assigned_jobs - self.assigned_jobs_count
        return pending_jobs[:allowed_assignment]

    def do_jobs(self, assigned_jobs: List[Job]):
        for job in assigned_jobs:
            if job.name == 'ping':
                try:
                    ping_result = any(ping(target=job.payload['ip'], timeout=5, count=2))
                except Exception:
                    job.set_result({'res': False, 'ip': job.payload['ip']})
                else:
                    job.set_result({'res': ping_result, 'ip': job.payload['ip']})


def run():
    node = Node(
        initial_config=Config(heartbeat_interval=HEARTBEAT_INTERVAL, max_assigned_jobs=1),
        communication=SocketCommunication(host=f'0.0.0.0', port=34687, pull_interval=12),
        initial_state=State(),
    )
    node.start()

    while True:  # IDLE
        sleep(10)
