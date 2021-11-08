import os
from typing import List
from time import sleep
from random import choice
from datetime import datetime, timedelta

from requests import get
from loguru import logger
from notifiers import get_notifier
from ants import BaseNode, Job, State, Message
from ants.communications import SocketCommunication

from config import Config


HEARTBEAT_INTERVAL = 30
TELEGRAM_CHAT_ID = '-1001574719922'
TELEGRAM_BOT_TOKEN = '2125627071:AAEoqEXo_r-unFGbHPCDXhJ6gBOk9xC9Xxc'
BANNER = '''\

-------------------------------------------------------------------------------------------------------------------
Welcome to the DecentralizedMonitor!!
We here to help you monitor your server operational status more reliably and free with our community based monitor.

The monitor will connect to our P2P network and will be monitored by the network,
check will be preformed every few minutes (average 3min)

Make sure that your server has public ip and can get income traffic on the port <{port}>
if you have ufw active use this command to allow the income traffic on this port:
$> sudo ufw allow {port}

Every down time will be notified at this channel:
https://t.me/decentralized_monitoring
-------------------------------------------------------------------------------------------------------------------

'''


def my_public_ip():
    try:
        ip = get('https://api.ipify.org').text
    except:
        ip = get('http://ip.42.pl/raw').text
    return ip


def get_user_mention_on_telegram():
    mention = input("If your server go down, how to mention on telegram? (Optional): ")
    if not mention.startswith('@'):
        mention = '@' + mention
        if mention == '@':
            mention = '#not_specified'
    return mention


class Node(BaseNode):

    def __init__(self, mention_on_telegram, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.completed_jobs_set = set()
        self.failed_pings = []

        self.mention_on_telegram = mention_on_telegram
        self.ip_to_telegram_mention = {}  # {node ip: telegram mention}
        self.my_public_ip = my_public_ip()

    def add_messages(self) -> List[Message]:
        if self.my_public_ip not in self.ip_to_telegram_mention:
            return [
                Message(
                    self.node_id,
                    payload={'mention_on_telegram': self.mention_on_telegram, 'ip': self.my_public_ip},
                    expiration_date=datetime.now() + timedelta(minutes=30)
                )
            ]
        return []

    def process_messages(self, messages: List[Message]):
        print(self.communication.peers)
        self.ip_to_telegram_mention.clear()
        for message in messages:
            print(message.to_dict())
            self.ip_to_telegram_mention[message.payload['ip']] = message.payload['mention_on_telegram']

    def completed_jobs(self, done_jobs: List[Job]):
        print(done_jobs)
        for job in done_jobs:
            logger.success(f'{job.name} job completed: payload={job.payload}, result={job.result}')
            self.completed_jobs_set.add(job)

    def add_jobs(self) -> List[Job]:
        jobs = []
        for i in range(2):
            ips = list(self.ip_to_telegram_mention.keys())
            if not ips:
                break
            random_peer = choice(ips)
            jobs.append(Job(name='ping', payload={'ip': random_peer}))
        for ping_data in self.failed_pings:
            jobs.append(
                Job(
                    name='notify',
                    payload={
                        'ip': ping_data['ip'],
                        'at': ping_data['date'],
                        'mention': self.ip_to_telegram_mention.get(ping_data['ip'], 'Not specified')
                    }
                )
            )
        self.failed_pings.clear()
        return jobs

    def assign_to_jobs(self, pending_jobs: List[Job]):
        print(pending_jobs)
        allowed_assignment = self.config.max_assigned_jobs - self.assigned_jobs_count
        return pending_jobs[:allowed_assignment]

    def do_jobs(self, assigned_jobs: List[Job]):
        for job in assigned_jobs:
            if job.name == 'ping':
                try:
                    logger.info(f'sending ping to {job.payload["ip"]}')
                    response = os.system("ping -c 1 " + job.payload['ip'] + '> /dev/null')
                    ping_result = not bool(response)
                except Exception:
                    job.set_result({'res': False, 'ip': job.payload['ip']})
                    self.failed_pings.append({'ip': job.payload['ip'], 'date': datetime.utcnow().isoformat()})
                else:
                    if not ping_result:
                        self.failed_pings.append({'ip': job.payload['ip'], 'date': datetime.utcnow().isoformat()})
                    job.set_result({'res': ping_result, 'ip': job.payload['ip']})
            elif job.name == 'notify':
                logger.info(f'sending telegram message')
                telegram_notifier = get_notifier('telegram')
                response = telegram_notifier.notify(
                    message=f'🟥🟥\n'
                            f'Attention: {job.payload["mention"]}\n'
                            f'{job.payload["ip"]} ware down at {job.payload["at"]}\n'
                            f'🟥🟥',
                    chat_id=TELEGRAM_CHAT_ID,
                    token=TELEGRAM_BOT_TOKEN,
                )
                job.set_result({'status': response.status, 'provider': response.provider})


def run():
    mention = get_user_mention_on_telegram()

    listen_port = 34687
    node = Node(
        initial_config=Config(heartbeat_interval=HEARTBEAT_INTERVAL, max_assigned_jobs=1),
        communication=SocketCommunication(
            host='0.0.0.0',
            port=listen_port,
            pull_interval=12,
            bootstrap_nodes=[('5.183.9.78', 34687)]
        ),
        initial_state=State(),
        mention_on_telegram=mention
    )
    node.start()

    print(BANNER.format(port=listen_port))

    while True:  # IDLE
        sleep(10)
