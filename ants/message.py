from datetime import datetime
from json import dumps

from .state import State


class Message:
    def __init__(self, sender: str, created_at: datetime, state: State):
        self.sender = sender
        self.created_at = created_at
        self.state = state

    def to_json(self) -> str:
        return dumps({
            'sender': self.sender,
            'created_at': self.created_at.isoformat(),
            'state': self.state.to_dict()
        })

    @classmethod
    def from_dict(cls):
        pass
