import asyncio
import json
import re
from typing import Dict, List, Optional, Set, Tuple

import aiohttp
import websockets


class LedAlerts:
    def __init__(self, data: Dict[int, List[str]]):
        """
        Initializes the LedAlerts class.

        Args:
            data (Dict[int, List[str]]): The mapping of zone numbers to a list of region names.
        """
        self.data: Dict[int, List[str]] = data
        self.flipped_zones = {
            city: key for key, values in data.items() for city in values
        }

    def get_danger_level_by(self, regions: Set[str]) -> List[Tuple[int, int, int]]:
        alerts: Set[str] = regions.intersection(self.flipped_zones.keys())
        if not alerts:
            return -1
        else:
            danger_level: int = min([self.flipped_zones[alert] for alert in alerts])
            return danger_level


ZONES: Dict[int, List[str]] = {
    0: ["м. Київ"],
    1: ["Київська область"],
    2: [
        "Житомирська область",
        "Вінницька область",
        "Черкаська область",
        "Полтавська область",
        "Чернігівська область",
    ],
    3: [
        "Рівненська область",
        "Хмельницька область",
        "Чернівецька область",
        "Одеська область",
        "Кіровоградська область",
        "Сумська область",
        "Дніпропетровська область",
        "Харківська область",
    ],
    4: [
        "Волинська область",
        "Львівська область",
        "Івано-Франківська область",
        "Тернопільська область",
        "Донецька область",
        # "Луганська область",
        "Запорізька область",
        "Миколаївська область",
        "Херсонська область",
    ],
    5: ["Закарпатська область"],  # , "Автономна Республіка Крим"],
}

led_alerts = LedAlerts(ZONES)


class Connection:
    def __init__(self):
        self.url: str = "https://map.ukrainealarm.com"
        self.headers: dict = {
            ":method": "GET",
            ":scheme": "https",
            ":authority": "map.ukrainealarm.com",
            ":path": "/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-GB,en;q=0.9",
            "Connection": "keep-alive",
            "Cookie": "_ga=GA1.1.1289612607.1685736470; _ga_9QLR0Q6YVH=GS1.1.1685736484.1.1.1685737479.0.0.0; _ga_EVB2DKW5H7=GS1.1.1685736470.1.1.1685736478.0.0.0; cf_clearance=1snWBN.HITbixxizDWYPsm2m2FXFxWSKMg7mebFpnWg-1685736454-0-250",
            "Host": "map.ukrainealarm.com",
            "Referer": "https://api.ukrainealarm.com/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
        }
        self.api_token: str = ""
        self.auth: dict = {
            "params": {
                "token": "",
                "name": "js",
            },
            "id": 1,
        }

    async def fetch_html(self) -> bytes:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(self.url) as response:
                return await response.read()

    async def extract_api_token(self, html: bytes) -> Optional[str]:
        pattern = rb'<input\s+id="centrifugo-token"\s+type="hidden"\s+value="([^"]+)"'
        match = re.search(pattern, html)

        if match:
            return match.group(1).decode("utf-8")
        return None

    async def ws_client(self):
        uri = "wss://ws.ukrainealarm.com/connection/websocket"
        async with websockets.connect(uri) as websocket:
            last_message_id = 0
            await websocket.send(json.dumps(self.auth))
            last_message_id += 1
            while True:
                try:
                    response = await websocket.recv()
                    response = json.loads(response)
                    if response.get("id") == 1:
                        await websocket.send(
                            json.dumps(
                                {
                                    "method": 1,
                                    "params": {"channel": "updateMap"},
                                    "id": 2,
                                }
                            )
                        )
                        last_message_id = 2
                    elif response.get("id") in (2, 3):
                        last_message_id = int(response.get("id")) + 1
                        await websocket.send(
                            json.dumps(
                                {
                                    "method": 6,
                                    "params": {
                                        "channel": "updateMap",
                                        "since": {"offset": 0, "epoch": "xyz"},
                                        "limit": 1,
                                    },
                                    "id": last_message_id,
                                }
                            )
                        )
                    elif response.get("result"):
                        if response["result"].get("channel", "") == "updateMap":
                            data = response["result"]["data"]["data"]["alerts"]
                        else:
                            data = response["result"]["publications"][0]["data"][
                                "alerts"
                            ]

                        alerts_by_region: Set[str] = {
                            alert["regionName"] for alert in data
                        }

                        print(f"Alerts:\n {alerts_by_region}\n")
                        priority = led_alerts.get_danger_level_by(alerts_by_region)
                        await self.set_color_by(priority)

                except (
                    asyncio.TimeoutError,
                    websockets.exceptions.ConnectionClosedError,
                ) as error:
                    break
                except json.decoder.JSONDecodeError:
                    pass

    async def set_color_by(self, priority: int):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://127.0.0.1:8343/api/alerts/priority", json={"priority": priority}
            ) as resp:
                print(await resp.text())

    async def main(self):
        while True:
            html = await self.fetch_html()
            api_token = await self.extract_api_token(html)
            if api_token:
                self.auth["params"]["token"] = api_token
                try:
                    await self.ws_client()
                except Exception:
                    print("Reconnecting...")
            else:
                print("API token extraction failed. Retrying...")

            await asyncio.sleep(10)  # Wait before retrying

    async def run(self):
        try:
            await self.main()
        finally:
            await aiohttp.ClientSession().close()
            await asyncio.sleep(0.250)  # Allow time for graceful shutdown
            asyncio.get_running_loop().shutdown_asyncgens()


connection = Connection()
asyncio.run(connection.run())
