import asyncio
import unittest

import aiohttp

from led_strip_alert.agents.radiation_alert import Location, RadiationAnalyzer


class RadiationAnalyzerTestCase(unittest.TestCase):
    def test_in_radius_with_in_radius_coordinates(self):
        lat1, lon1 = 51.3890, 30.0997  # Chernobyl NPP coordinates
        lat2, lon2 = 51.3893, 30.0999  # Coordinates within the radius
        radius = 40
        result = RadiationAnalyzer.in_radius(lat1, lon1, lat2, lon2, radius)
        self.assertTrue(result)  # Expected True when within the radius

    def test_in_radius_with_outside_radius_coordinates(self):
        lat1, lon1 = 51.3890, 30.0997  # Chernobyl NPP coordinates
        lat2, lon2 = 51.5000, 30.5000  # Coordinates outside the radius
        radius = 40
        result = RadiationAnalyzer.in_radius(lat1, lon1, lat2, lon2, radius)
        self.assertFalse(result)  # Expected False when outside the radius

    # ... add more test cases for the in_radius method

    def test_analyze_with_normal_radiation(self):
        async def mock_load_data(session):
            return {"devices": [{"a": "51.3893", "n": "30.0999", "gamma": "200"}]}

        async def mock_set_radiation(rad):
            pass

        analyzer = RadiationAnalyzer()
        analyzer.load_data = mock_load_data
        analyzer.set_radiation = mock_set_radiation

        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(analyzer.analyze(None))
        self.assertFalse(result)  # Expected False for normal radiation

    def test_analyze_with_high_radiation(self):
        async def mock_load_data(session):
            return {"devices": [{"a": "51.3893", "n": "30.0999", "gamma": "500"}]}

        async def mock_set_radiation(rad):
            pass

        analyzer = RadiationAnalyzer()
        analyzer.load_data = mock_load_data
        analyzer.set_radiation = mock_set_radiation

        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(analyzer.analyze(None))
        self.assertTrue(result)  # Expected True for high radiation


if __name__ == "__main__":
    unittest.main()
