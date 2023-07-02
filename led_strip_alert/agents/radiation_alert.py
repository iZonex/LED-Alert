import aiohttp
import asyncio
import json
import math
from dataclasses import dataclass
from typing import List


@dataclass
class Location:
    name: str
    coordinates: List[float]
    radius: int
    rad_normal: int


class RadiationAnalyzer:
    IGNORED_LOCATION = Location("Чернобыльская АЭС", [51.3890, 30.0997], 40, 60500)
    NORMAL_RAD = 300

    def __init__(self):
        self.url = "https://www.saveecobot.com/storage/maps_data.js"

    async def load_data(self, session):
        async with session.get(self.url) as resp:
            text = await resp.text()
            return json.loads(text)

    @staticmethod
    def in_radius(lat1, lon1, lat2, lon2, radius):
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        r = 6371
        distance = r * c
        return distance <= radius

    async def set_radiation(self, rad: bool):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://127.0.0.1:8343/api/alerts/rad", json={"rad": rad}
            ) as resp:
                print(await resp.text())

    async def analyze(self, session):
        data = await self.load_data(session)
        extracted_data = []
        lat, lon = self.IGNORED_LOCATION.coordinates
        for device in data["devices"]:
            if not "gamma" in device:
                continue
            if self.in_radius(
                lat,
                lon,
                float(device["a"]),
                float(device["n"]),
                self.IGNORED_LOCATION.radius,
            ):
                continue
            if int(device["gamma"]) > self.NORMAL_RAD:
                extracted_data.append(int(device["gamma"]))
        top_10 = sorted(extracted_data, reverse=True)[:10]
        if len(top_10) >= 10:
            print(f"Обнаружен всплеск радиации {max(top_10)} нЗв/год")
            await self.set_radiation(True)
            return True
        print("Всплесков радиации не обнаружено")
        await self.set_radiation(False)
        return False

    async def run(self):
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    await self.analyze(session)
                    await asyncio.sleep(5)
                except Exception as e:
                    print(f"An error occurred: {e}")
                    await asyncio.sleep(5)


analyzer = RadiationAnalyzer()
asyncio.run(analyzer.run())
