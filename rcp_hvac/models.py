"""Small, explicit interfaces between synthetic sensors and controls."""

from dataclasses import dataclass
from enum import Enum


class DistributionMode(str, Enum):
    FACE = "face"
    FEET = "feet"
    DEFROST = "defrost"


@dataclass(frozen=True)
class SensorReadings:
    cabin_temp_c: float
    ambient_temp_c: float


@dataclass(frozen=True)
class ClimateRequest:
    target_cabin_c: float
    fan_percent: float
    distribution: DistributionMode


@dataclass(frozen=True)
class ActuatorCommands:
    blower_percent: float
    blend_flap_percent: float
    face_flap_percent: float
    feet_flap_percent: float
    defrost_flap_percent: float
