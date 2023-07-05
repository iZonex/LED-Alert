#!/bin/bash

# Копіюємо скрипти в каталог
sudo cp led_strip_alert/agents/air_raids_alert.py led_strip_alert/agents/radiation_alert.py led_strip_alert/server.py /opt/led_alerts

# Запускаємо служби
sudo systemctl restart air_raids_alert.service
sudo systemctl restart radiation_alert.service
sudo systemctl restart led_server.service
