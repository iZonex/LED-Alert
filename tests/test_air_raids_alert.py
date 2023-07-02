import unittest

from led_strip_alert.agents.air_raids_alert import LedAlerts


class LedAlertsTestCase(unittest.TestCase):
    def setUp(self):
        self.data = {
            0: ["м. Київ"],
            1: ["Київська область"],
            2: [
                "Житомирська область",
                "Вінницька область",
                "Черкаська область",
                "Полтавська область",
                "Чернігівська область",
            ],
        }

    def test_get_danger_level_by_with_matching_regions(self):
        led_alerts = LedAlerts(self.data)
        regions = {"м. Київ", "Київська область"}
        result = led_alerts.get_danger_level_by(regions)
        self.assertEqual(result, 0)  # Expected danger level for matching regions

    def test_get_danger_level_by_with_non_matching_regions(self):
        led_alerts = LedAlerts(self.data)
        regions = {"Харківська область", "Одеська область"}
        result = led_alerts.get_danger_level_by(regions)
        self.assertEqual(result, -1)  # Expected -1 when no matching regions found


if __name__ == "__main__":
    unittest.main()
