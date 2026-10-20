"""Synthetic sensors, simplified HVAC physics, first-order actuator response.

Every value is fictitious. This simulation does not model a specific vehicle.
"""

import math
import random
from dataclasses import dataclass

from .controller import ClimateController, clamp
from .models import ActuatorCommands, ClimateRequest, DistributionMode, SensorReadings


@dataclass
class SimulatedVehicle:
    cabin_temp_c: float = 12.0
    ambient_temp_c: float = 5.0
    blower_percent: float = 0.0
    blend_flap_percent: float = 0.0
    face_flap_percent: float = 100.0
    feet_flap_percent: float = 0.0
    defrost_flap_percent: float = 0.0
    warm_air_c: float = 45.0

    def observe(self, rng: random.Random) -> SensorReadings:
        """Synthetic sensor values with small Gaussian measurement noise."""
        return SensorReadings(
            cabin_temp_c=self.cabin_temp_c + rng.gauss(0.0, 0.03),
            ambient_temp_c=self.ambient_temp_c + rng.gauss(0.0, 0.02),
        )

    def step(self, command: ActuatorCommands, dt_s: float, stuck_blend: bool) -> None:
        if dt_s <= 0 or not math.isfinite(dt_s):
            raise ValueError("dt_s must be a positive, finite number")

        # Idealized bounded actuator movement, not a hardware bus simulation.
        def follow(actual: float, target: float, slew_pct_per_s: float) -> float:
            delta = clamp(target - actual, -slew_pct_per_s * dt_s, slew_pct_per_s * dt_s)
            return clamp(actual + delta)

        self.blower_percent = follow(self.blower_percent, command.blower_percent, 35.0)
        if not stuck_blend:
            self.blend_flap_percent = follow(self.blend_flap_percent, command.blend_flap_percent, 18.0)
        self.face_flap_percent = follow(self.face_flap_percent, command.face_flap_percent, 25.0)
        self.feet_flap_percent = follow(self.feet_flap_percent, command.feet_flap_percent, 25.0)
        self.defrost_flap_percent = follow(self.defrost_flap_percent, command.defrost_flap_percent, 25.0)

        mixed_air_c = (
            self.ambient_temp_c * (1.0 - self.blend_flap_percent / 100.0)
            + self.warm_air_c * self.blend_flap_percent / 100.0
        )
        # Simplified cabin heat balance: cabin-to-ambient loss + forced-air heating.
        heat_loss_c_per_s = (self.ambient_temp_c - self.cabin_temp_c) / 420.0
        air_exchange_c_per_s = (
            (mixed_air_c - self.cabin_temp_c) * (self.blower_percent / 100.0) / 75.0
        )
        self.cabin_temp_c += dt_s * (heat_loss_c_per_s + air_exchange_c_per_s)


def request_profile(elapsed_s: float) -> ClimateRequest:
    """A reproducible demo of user requests changing during a drive."""
    if elapsed_s < 120:
        return ClimateRequest(21.0, 50.0, DistributionMode.FACE)
    if elapsed_s < 240:
        return ClimateRequest(24.0, 60.0, DistributionMode.FEET)
    return ClimateRequest(18.0, 70.0, DistributionMode.DEFROST)


def simulate(
    duration_s: int = 360,
    dt_s: float = 1.0,
    *,
    stuck_blend: bool = False,
    fault_at_s: float = 190.0,
    seed: int = 7,
) -> list[dict[str, float | str | bool]]:
    """Return time-series records for normal or stuck-blend demo.

    The mismatch flag uses a simple consecutive-duration counter and should
    not be interpreted as a production fault-detection algorithm.
    """
    if duration_s <= 0 or dt_s <= 0:
        raise ValueError("duration_s and dt_s must be positive")

    rng = random.Random(seed)
    plant = SimulatedVehicle()
    control = ClimateController(warm_air_c=plant.warm_air_c)
    mismatched_seconds = 0.0
    rows: list[dict[str, float | str | bool]] = []
    step_count = math.ceil(duration_s / dt_s)

    for tick in range(step_count):
        elapsed_s = tick * dt_s
        if elapsed_s >= duration_s:
            break
        request = request_profile(elapsed_s)
        measured = plant.observe(rng)
        command = control.compute(measured, request)
        fault_active = stuck_blend and elapsed_s >= fault_at_s
        plant.step(command, dt_s, stuck_blend=fault_active)

        mismatch = abs(command.blend_flap_percent - plant.blend_flap_percent) > 12.0
        mismatched_seconds = mismatched_seconds + dt_s if mismatch else 0.0
        diagnostic_flag = mismatched_seconds >= 6.0

        rows.append({
            "time_s": round(elapsed_s, 3),
            "cabin_sensor_c": round(measured.cabin_temp_c, 3),
            "cabin_actual_c": round(plant.cabin_temp_c, 3),
            "ambient_sensor_c": round(measured.ambient_temp_c, 3),
            "target_cabin_c": request.target_cabin_c,
            "distribution": request.distribution.value,
            "blower_command_pct": round(command.blower_percent, 3),
            "blower_actual_pct": round(plant.blower_percent, 3),
            "blend_command_pct": round(command.blend_flap_percent, 3),
            "blend_actual_pct": round(plant.blend_flap_percent, 3),
            "face_flap_actual_pct": round(plant.face_flap_percent, 3),
            "feet_flap_actual_pct": round(plant.feet_flap_percent, 3),
            "defrost_flap_actual_pct": round(plant.defrost_flap_percent, 3),
            "fault_active": bool(fault_active),
            "blend_mismatch_flag": bool(diagnostic_flag),
        })
    return rows
