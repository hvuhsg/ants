from threading import Thread
from random import sample
from socket import socket, AF_INET, SOCK_STREAM
from time import sleep
from typing import List
from socketserver import ThreadingTCPServer, BaseRequestHandler
from json import loads, dumps

from ..state import State
from ..base_communication import BaseCommunication
from ..job import Job


__all__ = ['SocketCommunication']


def state_from_dict(state_dict: dict) -> State:
    jobs = {
        job_dict['id']: Job.from_dict(job_dict)
        for job_dict in state_dict['jobs']
    }
    return State(jobs=jobs)


def state_to_dict(state: State) -> dict:
    jobs_list = [job.to_dict() for job in state._jobs.values()]
    return {'jobs': jobs_list}


class EmptyPeersListError(Exception):
    pass


class RequestHandler(BaseRequestHandler):
    def handle(self):
        request_data = self.request.recv(100*1000)
        if not request_data:
            return
        request_dict = loads(request_data)

        if request_dict['port'] == 34688:  # Testing on localhost
            self.client_address = ('127.0.0.2', 34688)

        self.server.communication.peers.add((self.client_address[0], request_dict['port']))
        if request_dict['route'] == 'ips':
            json_peers = dumps(list(self.server.communication.peers))
            self.request.send(json_peers.encode())
        elif request_dict['route'] == 'pull_state':
            json_state = dumps(state_to_dict(self.server.communication.current_state))
            self.request.send(json_state.encode())


class SocketServer(ThreadingTCPServer):
    def __init__(self, communication, *args, **kwargs):
        self.communication = communication
        super().__init__(*args, **kwargs)


class SocketCommunication(BaseCommunication, Thread):

    SOCKET_TIMEOUT = 15

    def __init__(self, host='0.0.0.0', port=34687, pull_interval=10, bootstrap_nodes: list = None):
        if bootstrap_nodes is None:
            bootstrap_nodes = []
        self._run = True
        self._pull_interval = pull_interval

        self.server_address = (host, port)
        self.peers = set(bootstrap_nodes)  # bootstrap nodes
        self.pulled_states = []
        self.socket_server = SocketServer(self, self.server_address, RequestHandler)
        self.current_state = State()

        super().__init__(name='SocketCommunication', daemon=True)

        self.socket_server_thread = Thread(target=self.socket_server.serve_forever, daemon=True)

        self.socket_server_thread.start()
        self.start()
        print(f'started socket server on {self.server_address}...')

    def pull(self) -> List[State]:
        list_copy = self.pulled_states.copy()
        self.pulled_states.clear()
        return list_copy

    def broadcast(self, state: State):
        self.current_state = state

    def _random_peer(self) -> tuple:
        for try_count in range(10):
            random_peer = sample(list(self.peers), 1)
            if random_peer[0] == self.server_address:
                continue
            return random_peer[0]
        raise EmptyPeersListError()

    def _update_ips(self):
        peer_address = self._random_peer()
        sock = socket()
        sock.settimeout(self.SOCKET_TIMEOUT)
        sock.connect(peer_address)
        sock.send(dumps({'route': 'ips', 'port': self.server_address[1]}).encode())
        ips_json = sock.recv(1000*1000)
        ips = map(tuple, loads(ips_json))
        self.peers |= set(ips)

    def _pull_state(self):
        peer_address = self._random_peer()
        sock = socket(AF_INET, SOCK_STREAM)
        sock.settimeout(self.SOCKET_TIMEOUT)
        sock.connect(peer_address)
        sock.send(dumps({'route': 'pull_state', 'port': self.server_address[1]}).encode())
        state_json = sock.recv(1000 * 1000)
        state = state_from_dict(loads(state_json))
        self.pulled_states.append(state)

    def run(self) -> None:
        errors = 0
        while self._run:
            sleep(self._pull_interval)
            if not self._run:
                break
            try:
                self._update_ips()
                self._pull_state()
            except ConnectionError as CE:
                print('connection error', CE)
                errors += 1
                continue
            except EmptyPeersListError:
                continue

    def shutdown(self):
        self._run = False
        self.socket_server.shutdown()
