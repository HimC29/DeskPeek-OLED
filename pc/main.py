import sys
import websocket
import json
import psutil

try:
	while True:
		cpu = psutil.cpu_percent(interval=1)
		ram = psutil.virtual_memory().percent

		data = {"cpu": cpu, "ram": ram}

		ws = websocket.WebSocket()

		ws.connect("ws://192.168.100.119:81")
		ws.send(json.dumps(data))
		ws.close()
except KeyboardInterrupt:
	sys.exit(0);
