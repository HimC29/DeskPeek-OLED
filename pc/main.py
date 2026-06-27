import sys
import websocket
import json
import psutil

ws = websocket.WebSocket()
ws.connect("ws://192.168.100.119:81")

try:
	while True:
		cpu = psutil.cpu_percent(interval=1)
		ram = psutil.virtual_memory().percent
		data = {"cpu": cpu, "ram": ram}
		ws.send(json.dumps(data))
except KeyboardInterrupt:
	ws.close()
	sys.exit(0);
