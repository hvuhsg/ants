from threading import Thread
from random import sample
from socket import socket, AF_INET, SOCK_STREAM, timeout as SocketTimeout
from collections import defaultdict
from time import sleep, time
from typing import List
from socketserver import ThreadingTCPServer, BaseRequestHandler
from json import loads, dumps

from ..state import State
from ..base_communication import BaseCommunication


__all__ = ['SocketCommunication']


PENALTY_THRESHOLD = 10
BLACK_LIST_MAX_TIME = 10*60  # in seconds


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
            json_state = dumps(self.server.communication.current_state.to_dict())
            self.request.send(json_state.encode())


class SocketServer(ThreadingTCPServer):
    def __init__(self, communication, *args, **kwargs):
        self.communication = communication
        super().__init__(*args, **kwargs)


class SocketCommunication(BaseCommunication, Thread):

    SOCKET_TIMEOUT = 15

    def __init__(self, my_public_ip: str = '255.255.255.255', host='0.0.0.0', port=34687, pull_interval=10, bootstrap_nodes: list = None):
        if bootstrap_nodes is None:
            bootstrap_nodes = []
        self._run = True
        self._pull_interval = pull_interval

        self.my_public_ip = my_public_ip
        self.server_address = (host, port)
        self.peers = set(bootstrap_nodes)  # bootstrap nodes
        self.black_listed_peers = {}
        self.peers_penalty = defaultdict(int)

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
            random_peer = tuple(sample(list(self.peers), 1)[0])
            if random_peer[0] == self.my_public_ip:
                continue
            if random_peer in self.black_listed_peers:
                if time() - self.black_listed_peers[random_peer[0]] >= BLACK_LIST_MAX_TIME:
                    del self.black_listed_peers[random_peer[0]]
                else:
                    continue
            return random_peer
        raise EmptyPeersListError()

    def _request_from_random_peer(self, request_dict: dict):
        peer_address = self._random_peer()
        sock = socket(AF_INET, SOCK_STREAM)
        sock.settimeout(self.SOCKET_TIMEOUT)
        try:
            sock.connect(peer_address)
            sock.send(dumps(request_dict).encode())
            response_json = sock.recv(1000 * 1000)
        except (ConnectionError, SocketTimeout):
            self.peers_penalty[peer_address] += 1
            if self.peers_penalty[peer_address[0]] > PENALTY_THRESHOLD:
                self.peers.remove(peer_address)
                self.black_listed_peers[peer_address[0]] = time()
                self.peers_penalty[peer_address[0]] -= 1
            return None
        else:
            self.peers_penalty[peer_address] = 0
        return loads(response_json)

    def _update_ips(self):
        ips = self._request_from_random_peer({'route': 'ips', 'port': self.server_address[1]})
        if ips is None:
            return
        ips = map(tuple, ips)
        self.peers |= set(ips)

    def _pull_state(self):
        state_dict = self._request_from_random_peer({'route': 'pull_state', 'port': self.server_address[1]})
        if state_dict is None:
            return
        state = State.from_dict(state_dict)
        self.pulled_states.append(state)

    def run(self) -> None:
        while self._run:
            sleep(self._pull_interval)
            if not self._run:
                break
            try:
                self._update_ips()
                self._pull_state()
            except EmptyPeersListError:
                continue

    def shutdown(self):
        self._run = False
        self.socket_server.shutdown()
