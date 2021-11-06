from dataclasses import dataclass


@dataclass
class BaseConfig:
    heartbeat_interval: int  # In seconds

