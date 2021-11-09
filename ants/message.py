import math
from datetime import datetime
from json import dumps
from hashlib import sha256


def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


class Message:
    def __init__(self, sender: int, payload: dict, expiration_date: datetime, created_at: datetime = None):
        if created_at is None:
            created_at = datetime.now()
        self.sender = sender
        self.payload = payload
        self.expiration_date = expiration_date
        self.created_at = created_at

    @property
    def is_expired(self) -> bool:
        return datetime.now() >= self.expiration_date

    @property
    def id(self):
        message_as_string = (
            f"{self.sender}:{dumps(self.payload, sort_keys=True)}".encode()
        )
        return sha256(message_as_string).hexdigest()

    @property
    def vector(self):
        return sigmoid(self.created_at.timestamp())

    def to_dict(self) -> dict:
        return {
            "sender": self.sender,
            "payload": self.payload,
            "expiration_date": self.expiration_date.isoformat(),
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, dict_: dict):
        return cls(
            sender=dict_["sender"],
            payload=dict_["payload"],
            expiration_date=datetime.fromisoformat(dict_["expiration_date"]),
            created_at=datetime.fromisoformat(dict_["created_at"]),
        )

    def __gt__(self, other):
        return self.vector > other.vector

    def __eq__(self, other):
        return self.vector == other.vector
