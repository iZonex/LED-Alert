# Run Server
run-server:
	python led_strip_alert/server.py

# Run Air Raids Alert
run-air-raids-alert:
	python led_strip_alert/agents/air_raids_alert.py

# Run Radiation Alert
run-radiation-alert:
	python led_strip_alert/agents/radiation_alert.py

# Run Unit Tests
run-tests:
	python -m unittest discover -s tests

# Clear Cache
clean:
	find . -type f -name "*.pyc" -delete
	rm -rf __pycache__
