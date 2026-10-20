"""Simplified, original cabin-temperature / air-distribution controller.

This is educational control logic, NOT production automotive software.
Percentages are abstract actuator positions, not OEM LIN messages.
"""

import math

from .models import ActuatorCommands, ClimateRequest, DistributionMode, SensorReadings


def clamp(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return max(lower, min(upper, value))


class ClimateController:
    """Compute desired blower and flap positions from simulated measurements."""

    def __init__(self, proportional_gain: float = 4.5, warm_air_c: float = 45.0):
        self.proportional_gain = proportional_gain
        self.warm_air_c = warm_air_c

    def compute(self, sensors: SensorReadings, request: ClimateRequest) -> ActuatorCommands:
        quantities = (
            sensors.cabin_temp_c, sensors.ambient_temp_c,
            request.target_cabin_c, request.fan_percent,
        )
        if not all(math.isfinite(v) for v in quantities):
            raise ValueError("Inputs must be finite numeric values")
        if not isinstance(request.distribution, DistributionMode):
            raise ValueError("Unknown air distribution mode")

        # A simple warm/cold blending estimate plus proportional feedback.
        # This intentionally omits refrigerant controls and OEM calibrations.
        span = max(self.warm_air_c - sensors.ambient_temp_c, 1.0)
        feedforward_pct = 100.0 * (request.target_cabin_c - sensors.ambient_temp_c) / span
        error_c = request.target_cabin_c - sensors.cabin_temp_c
        blend = clamp(feedforward_pct + self.proportional_gain * error_c)

        modes = {
            DistributionMode.FACE: (100.0, 0.0, 0.0),
            DistributionMode.FEET: (0.0, 100.0, 0.0),
            DistributionMode.DEFROST: (0.0, 0.0, 100.0),
        }
        face, feet, defrost = modes[request.distribution]
        return ActuatorCommands(
            blower_percent=clamp(request.fan_percent),
            blend_flap_percent=blend,
            face_flap_percent=face,
            feet_flap_percent=feet,
            defrost_flap_percent=defrost,
        )
