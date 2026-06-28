import sys
import websocket
import json
import psutil
from datetime import datetime

VERSION = "v0.1.0"

print(f"DeskPeek OLED {VERSION}")

ws = websocket.WebSocket()
ws.connect("ws://192.168.100.119:81")
ws.settimeout(0.1)

try:
	while True:
		try:
			msg = ws.recv()
			page = int(msg)
		except:
			pass

		if page == 0:
			net_before = psutil.net_io_counters()
			cpu = psutil.cpu_percent(interval=1)
			net_after = psutil.net_io_counters()
			download = (net_after.bytes_recv - net_before.bytes_recv) / 1024
			upload = (net_after.bytes_sent - net_before.bytes_sent) / 1024  
			ram = psutil.virtual_memory().percent
			data = {
				"cpu": f"{cpu}%",
				"ram": f"{ram}%",
				"download": f"{download:.2f} KB/s",
				"upload": f"{upload:.2f} KB/s"
			}
		elif page == 1:
			now = datetime.now()
			data = {
				"time": now.strftime("%H:%M:%S")
			}

		ws.send(json.dumps(data))
except KeyboardInterrupt:
	ws.close()
	sys.exit(0);
