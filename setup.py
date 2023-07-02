from setuptools import setup

setup(
    name='led_alerts',
    version='1.0.0',
    description='LED Alerts Package',
    author='Dmytro Chystiakov',
    packages=['led_alerts'],
    install_requires=[
        'aiohttp',
        'neopixel',
        'board',
    ],
    entry_points={
        'console_scripts': [
            'air_raids_alert = led_alerts.agents.air_raids_alert:main',
            'radiation_alert = led_alerts.agents.radiation_alert:main',
            'led_server = led_alerts.server:main',
        ],
    },
)
