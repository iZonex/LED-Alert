#!/bin/bash

# Встановлення залежностей Python та PIP
sudo apt update
sudo apt install -y python3 python3-pip

# Встановлення залежностей PIP
sudo pip3 install aiohttp neopixel board

# Створюємо каталог для скриптів
sudo mkdir /opt/led_alerts

# Копіюємо скрипти в каталог
sudo cp led_strip_alert/agents/air_raids_alert.py led_strip_alert/agents/radiation_alert.py led_strip_alert/server.py /opt/led_alerts

# Створюємо файл служби для air_raids_alert
cat <<EOF | sudo tee /etc/systemd/system/air_raids_alert.service
[Unit]
Description=Air Raids Alert Service
After=network.target

[Service]
WorkingDirectory=/opt/led_alerts
ExecStart=/usr/bin/python3 air_raids_alert.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Створюємо файл служби для radiation_alert
cat <<EOF | sudo tee /etc/systemd/system/radiation_alert.service
[Unit]
Description=Radiation Alert Service
After=network.target

[Service]
WorkingDirectory=/opt/led_alerts
ExecStart=/usr/bin/python3 radiation_alert.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Створюємо файл служби для server
cat <<EOF | sudo tee /etc/systemd/system/led_server.service
[Unit]
Description=LED Server
After=network.target

[Service]
WorkingDirectory=/opt/led_alerts
ExecStart=/usr/bin/python3 server.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Перезавантажуємо SystemD та активуємо служби
sudo systemctl daemon-reload
sudo systemctl enable air_raids_alert.service
sudo systemctl enable radiation_alert.service
sudo systemctl enable led_server.service

# Запускаємо служби
sudo systemctl start air_raids_alert.service
sudo systemctl start radiation_alert.service
sudo systemctl start led_server.service
