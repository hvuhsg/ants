import math
from datetime import datetime
from json import dumps
from hashlib import sha256


def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


class Message:
    def __init__(self, sender: int, payload: dict, expiration_date: datetime):
        self.sender = sender
        self.payload = payload
        self.expiration_date = expiration_date

    @property
    def is_expired(self) -> bool:
        return datetime.now() >= self.expiration_date

    @property
    def id(self):
        message_as_string = f'{self.sender}:{dumps(self.payload, sort_keys=True)}'.encode()
        return sha256(message_as_string).hexdigest()

    @property
    def vector(self):
        return sigmoid(self.expiration_date.timestamp())

    def to_dict(self) -> dict:
        return {
            'sender': self.sender,
            'payload': self.payload,
            'expiration_date': self.expiration_date.isoformat()
        }

    @classmethod
    def from_dict(cls, dict_: dict):
        return cls(
            sender=dict_['sender'],
            payload=dict_['payload'],
            expiration_date=datetime.fromisoformat(dict_['expiration_date'])
        )

    def __gt__(self, other):
        return self.expiration_date > other.expiration_date

    def __eq__(self, other):
        return self.expiration_date == other.expiration_date
