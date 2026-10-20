import unittest

from rcp_hvac.simulator import simulate


class SimulatorTests(unittest.TestCase):
    def test_simulation_returns_expected_number_of_rows(self):
        rows = simulate(duration_s=30, seed=10)
        self.assertEqual(len(rows), 30)
        self.assertEqual(rows[0]["time_s"], 0)
        self.assertEqual(rows[-1]["time_s"], 29)

    def test_results_are_reproducible(self):
        self.assertEqual(simulate(duration_s=20, seed=42), simulate(duration_s=20, seed=42))

    def test_air_heating_increases_initial_cabin_temp(self):
        rows = simulate(duration_s=100)
        self.assertGreater(rows[-1]["cabin_actual_c"], rows[0]["cabin_actual_c"])

    def test_distribution_profile_changes(self):
        rows = simulate(duration_s=260)
        self.assertEqual(rows[0]["distribution"], "face")
        self.assertEqual(rows[125]["distribution"], "feet")
        self.assertEqual(rows[245]["distribution"], "defrost")

    def test_stuck_flap_creates_mismatch(self):
        rows = simulate(duration_s=360, stuck_blend=True, fault_at_s=190)
        self.assertTrue(any(r["blend_mismatch_flag"] for r in rows))
        self.assertTrue(all(not r["fault_active"] for r in rows[:190]))

    def test_normal_operation_no_persistent_mismatch(self):
        rows = simulate(duration_s=360)
        self.assertFalse(any(r["blend_mismatch_flag"] for r in rows))


if __name__ == "__main__":
    unittest.main()
