from dataclasses import dataclass


@dataclass
class BaseConfig:
    heartbeat_interval: float  # In seconds
