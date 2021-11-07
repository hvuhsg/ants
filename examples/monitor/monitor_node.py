import os
from typing import List
from time import sleep
from random import choice
from datetime import datetime

from loguru import logger
from notifiers import get_notifier
from ants import BaseNode, Job, State
from ants.communications import SocketCommunication

from config import Config


HEARTBEAT_INTERVAL = 30
TELEGRAM_CHAT_ID = '-1001574719922'
TELEGRAM_BOT_TOKEN = '2125627071:AAEoqEXo_r-unFGbHPCDXhJ6gBOk9xC9Xxc'


class Node(BaseNode):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.completed_jobs_set = set()
        self.failed_pings = []

    def completed_jobs(self, done_jobs: List[Job]):
        for job in done_jobs:
            logger.success(f'{job.name} job completed: payload={job.payload}, result={job.result}')
            self.completed_jobs_set.add(job)

    def add_jobs(self) -> List[Job]:
        jobs = []
        for i in range(2):
            random_peer = choice(list(self.communication.peers))
            jobs.append(Job(name='ping', payload={'ip': random_peer[0]}))
        for ping_data in self.failed_pings:
            jobs.append(Job(name='notify', payload={'ip': ping_data['ip'], 'at': ping_data['date']}))
        self.failed_pings.clear()
        return jobs  # Add job to ping peer ip

    def assign_to_jobs(self, pending_jobs: List[Job]):
        allowed_assignment = self.config.max_assigned_jobs - self.assigned_jobs_count
        return pending_jobs[:allowed_assignment]

    def do_jobs(self, assigned_jobs: List[Job]):
        for job in assigned_jobs:
            if job.name == 'ping':
                try:
                    logger.info(f'sending ping to {job.payload["ip"]}')
                    response = os.system("ping -c 1 " + job.payload['ip'] + '> /dev/null')
                    ping_result = not bool(response)
                    # ping_result = any(ping(target=job.payload['ip'], timeout=5, count=2))
                except Exception:
                    job.set_result({'res': False, 'ip': job.payload['ip']})
                    self.failed_pings.append({'ip': job.payload['ip'], 'date': datetime.utcnow().isoformat()})
                else:
                    job.set_result({'res': ping_result, 'ip': job.payload['ip']})
            elif job.name == 'notify':
                telegram_notifier = get_notifier('telegram')
                response = telegram_notifier.notify(
                    message=f'🟥🟥 {job.payload["ip"]} ware down at {job.payload["at"]} 🟥🟥',
                    chat_id=TELEGRAM_CHAT_ID,
                    token=TELEGRAM_BOT_TOKEN,
                )
                job.set_result({'status': response.status, 'provider': response.provider})


def run():
    node = Node(
        initial_config=Config(heartbeat_interval=HEARTBEAT_INTERVAL, max_assigned_jobs=1),
        communication=SocketCommunication(
            host=f'0.0.0.0',
            port=34687,
            pull_interval=12,
            bootstrap_nodes=[('5.183.9.78', 34687)]
        ),
        initial_state=State(),
    )
    node.start()

    while True:  # IDLE
        sleep(10)
