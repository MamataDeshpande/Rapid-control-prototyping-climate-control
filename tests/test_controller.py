import unittest

from rcp_hvac.controller import ClimateController
from rcp_hvac.models import ClimateRequest, DistributionMode, SensorReadings


class ClimateControllerTests(unittest.TestCase):
    def setUp(self):
        self.controller = ClimateController()
        self.sensors = SensorReadings(cabin_temp_c=17.0, ambient_temp_c=5.0)

    def test_airflow_routes_to_selected_mode(self):
        for mode, expected in [
            (DistributionMode.FACE, (100, 0, 0)),
            (DistributionMode.FEET, (0, 100, 0)),
            (DistributionMode.DEFROST, (0, 0, 100)),
        ]:
            with self.subTest(mode=mode):
                c = self.controller.compute(self.sensors, ClimateRequest(22, 50, mode))
                self.assertEqual(
                    (c.face_flap_percent, c.feet_flap_percent, c.defrost_flap_percent),
                    expected,
                )

    def test_blower_command_clamped(self):
        c = self.controller.compute(self.sensors, ClimateRequest(22, 130, DistributionMode.FACE))
        self.assertEqual(c.blower_percent, 100)

    def test_warmer_request_increases_blend(self):
        cool = self.controller.compute(self.sensors, ClimateRequest(18, 50, DistributionMode.FACE))
        warm = self.controller.compute(self.sensors, ClimateRequest(24, 50, DistributionMode.FACE))
        self.assertGreater(warm.blend_flap_percent, cool.blend_flap_percent)

    def test_invalid_sensor_rejected(self):
        with self.assertRaises(ValueError):
            self.controller.compute(SensorReadings(float("nan"), 5), ClimateRequest(22, 50, DistributionMode.FACE))


if __name__ == "__main__":
    unittest.main()
