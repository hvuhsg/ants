import math
from datetime import datetime
from hashlib import sha256
from json import dumps
from enum import Enum


def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


class JobStatus(Enum):
    PENDING = 1
    ASSIGNED = 2
    DONE = 3


class Job:
    def __init__(
            self,
            name: str,
            payload: dict,
            created_at: datetime = None,
            status: JobStatus = JobStatus.PENDING,
            assigned_to: int = 0,
            result: dict = None
    ):
        if created_at is None:
            created_at = datetime.utcnow()
        self.name = name
        self.payload = payload
        self.created_at = created_at
        self.status = status
        self.assigned_to = assigned_to
        self.result = result

    def assign(self, node_id: int):
        self.assigned_to = node_id
        self.status = JobStatus.ASSIGNED

    def set_result(self, result: dict):
        self.result = result
        self.status = JobStatus.DONE

    @property
    def id(self) -> str:
        job_as_string = f'{self.name},{dumps(self.payload, sort_keys=True)}'.encode()
        return sha256(job_as_string).hexdigest()

    @property
    def vector(self) -> float:
        date_sigmoid = 1 - sigmoid(round(self.created_at.timestamp()))  # older the better
        date_weight = 10
        id_sigmoid = sigmoid(self.assigned_to)  # tie break
        id_weight = 1
        return (date_sigmoid * date_weight) + (id_sigmoid * id_weight) + self.status.value

    def __gt__(self, other):
        return self.vector > other.vector

    def __eq__(self, other):
        return self.vector == other.vector  # rarely happened

    def __repr__(self):
        return f'Job<id={self.id}, name={self.name}, status={self.status}>'

    def __str__(self):
        return f'Job<id={self.id}, name={self.name}, payload={self.payload} status={self.status}>'

    def __hash__(self):
        return hash(f'{self.id}:{self.created_at}:{self.status}:{self.assigned_to}:{self.result}')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'payload': self.payload,
            'created_at': self.created_at.isoformat(),
            'status': self.status.value,
            'assigned_to': self.assigned_to,
            'result': self.result,
        }

    @classmethod
    def from_dict(cls, job_dict: dict):
        job = cls(
            name=job_dict['name'],
            payload=job_dict['payload'],
            created_at=datetime.fromisoformat(job_dict['created_at']),
            status=JobStatus(job_dict['status']),
            assigned_to=job_dict['assigned_to'],
            result=job_dict['result'],
        )
        return job
