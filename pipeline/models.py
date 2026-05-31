from dataclasses import dataclass

@dataclass
class FacilityNode:
    id: str
    name: str
    in_degree: int = 0
    out_degree: int = 0

@dataclass
class CorridorEdge:
    source: str
    destination: str
    route_type: str
    time_of_day: str
    median_delay_ratio: float
    total_trips: int
