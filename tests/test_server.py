import json
import unittest

from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from led_strip_alert.server import LedServer, app


class LedServerTestCase(unittest.TestCase):
    def setUp(self):
        self.led_server = LedServer(number=287)

    def test_set_priority_with_valid_priority(self):
        priority = 2
        self.led_server.set_priotiry(priority)
        self.assertEqual(
            self.led_server.color, (255, 255, 0)
        )  # Expected color for priority 2

    def test_set_priority_with_invalid_priority(self):
        priority = 6
        with self.assertRaises(ValueError):
            self.led_server.set_priotiry(priority)

    def test_set_rad_with_true(self):
        self.led_server.set_rad(True)
        self.assertTrue(self.led_server.rad)  # Expected True for rad=True

    def test_set_rad_with_false(self):
        self.led_server.set_rad(False)
        self.assertFalse(self.led_server.rad)  # Expected False for rad=False


class LedServerAppTestCase(AioHTTPTestCase):
    async def get_application(self):
        return app

    @unittest_run_loop
    async def test_get_alerts(self):
        resp = await self.client.request("GET", "/api/alerts")
        self.assertEqual(resp.status, 200)  # Expected 200 OK

        data = await resp.json()
        self.assertIn("number", data)  # Expected "number" key in the response
        self.assertIn(
            "priority_colors", data
        )  # Expected "priority_colors" key in the response

    @unittest_run_loop
    async def test_set_priority(self):
        priority = 2
        payload = json.dumps({"priority": priority})

        resp = await self.client.post("/api/alerts/priority", data=payload)
        self.assertEqual(resp.status, 200)  # Expected 200 OK

        text = await resp.text()
        self.assertEqual(
            text, "Alert priority updated successfully"
        )  # Expected success message

    @unittest_run_loop
    async def test_set_radiation(self):
        rad = True
        payload = json.dumps({"rad": rad})

        resp = await self.client.post("/api/alerts/rad", data=payload)
        self.assertEqual(resp.status, 200)  # Expected 200 OK

        text = await resp.text()
        self.assertEqual(
            text, "Alert radiation status updated successfully"
        )  # Expected success message


if __name__ == "__main__":
    unittest.main()
