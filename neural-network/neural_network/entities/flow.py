from dataclasses import dataclass


@dataclass(frozen=True)
class Flow:
    src: str
    dst: str
    source_port: int
    dest_port: int
    proto: str
    start_time: float
    last_time: float
    pkts_fwd: int
    pkts_rev: int
    bytes_fwd: int
    bytes_rev: int
