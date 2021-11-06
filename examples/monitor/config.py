from dataclasses import dataclass


from ants import BaseConfig


@dataclass
class Config(BaseConfig):
    max_assigned_jobs: int
