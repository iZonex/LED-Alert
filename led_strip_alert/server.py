import json
import logging
from typing import Dict, Tuple

import board
import neopixel
from aiohttp import web

# Настроим logging для вывода отладочной информации
logging.basicConfig(level=logging.DEBUG)


class LedServer:
    def __init__(self, number: int = 287):
        """
        Initializes the LedAlerts class.

        Args:
            number (int): The total number of pixels/LEDs.
        """
        self.priority_colors: Dict[int, Tuple[int, int, int]] = {
            -1: (0, 0, 0),  # Off (no alerts)
            0: (255, 0, 0), # Red (highest priority)
            1: (255, 51, 20),  
            2: (255, 102, 40),  
            3: (255, 153, 60),  
            4: (255, 204, 80),  
            5: (255, 255, 100),  # Yellow (lowest priority)
        }
        self.number: int = number
        self.priority: int = -1
        self.color: Tuple[int, int, int] = (0, 0, 0)
        self.rad: bool = False
        logging.debug(f"Number of pixels: {self.number}")
        self.pixels = neopixel.NeoPixel(board.D18, number, auto_write=False)
        self.pixels.fill((0, 0, 0))
        self.pixels.show()

    def _set_radiation_color(self) -> None:
        """
        A helper method to set the radiation color of all the pixels.
        """
        logging.debug("Setting radiation color.")
        for i in range(self.number):
            if i // 3 % 2 == 0:
                self.pixels[i] = self.priority_colors[0]
            else:
                self.pixels[i] = (255, 255, 255)
        self.pixels.show()

    def _set_color(self) -> None:
        """
        A helper method to set the color of all the pixels.

        Args:
            color (Tuple[int, int, int]): The color to set.
        """
        logging.debug(f"Setting color to: {self.color}")
        self.pixels.fill(self.color)
        self.pixels.show()

    def set_priotiry(self, priority: int) -> bool:
        if self.priority == priority:
            return False
            
        if priority not in self.priority_colors:
            raise ValueError("Invalid priority")
        
        self.priority = priority
        self.color = self.priority_colors[priority]
        return True

    def set_rad(self, rad: bool) -> bool:
        if self.rad == rad:
            return False
        
        self.rad = rad
        return True

    def render(self) -> None:
        if self.rad:
            self._set_radiation_color()
        else:
            self._set_color()


app = web.Application()
routes = web.RouteTableDef()

led_alerts = LedServer()


@routes.get("/api/alerts")
async def get_alerts(request):
    data = {"number": led_alerts.number, "priority_colors": led_alerts.priority_colors}
    return web.Response(text=json.dumps(data), content_type="application/json")


@routes.post("/api/alerts/priority")
async def set_priority(request):
    data = await request.json()
    try:
        priority = int(data.get("priority"))
    except (TypeError, ValueError):
        return web.Response(text="Bad Request", status=400)

    if led_alerts.set_priotiry(priority):
        led_alerts.render()
        return web.Response(text="Alert priority updated successfully")
    
    return web.Response(text="Alert priority not changed")

    


@routes.post("/api/alerts/rad")
async def set_radiation(request):
    data = await request.json()
    try:
        rad = bool(data.get("rad"))
    except (TypeError, ValueError):
        return web.Response(text="Bad Request", status=400)

    if led_alerts.set_rad(rad):
        led_alerts.render()
        return web.Response(text="Alert radiation status updated successfully")
    
    return web.Response(text="Alert radiation status not changed")


app.add_routes(routes)

if __name__ == "__main__":
    web.run_app(app, host="127.0.0.1", port=8343)
