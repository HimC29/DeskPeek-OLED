import sys
import websocket
import json
import psutil
from datetime import datetime
import os

VERSION = "v0.2.0"

print(f"DeskPeek OLED {VERSION}")

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.json")

def ask_ip():	
	user_input = input("Enter ESP32 IP: ")
	config = {"esp32_ip": user_input}
	with open(config_path, "w") as f:
		json.dump(config, f)
	return config["esp32_ip"]

def load_ip():
	try:
		with open(config_path, "r") as f:
			config = json.load(f)
			return config["esp32_ip"]
	except FileNotFoundError:
		return None;

def connect_to_esp32():
	ip = load_ip()
	if ip is None:
		ip = ask_ip()

	ws = websocket.WebSocket()

	while True:
		try:
			ws.connect(f"ws://{ip}:81")
			print("Connected successfully!")
			break
		except (OSError, websocket.WebSocketAddressException,  websocket.WebSocketTimeoutException, ConnectionRefusedError):
		   	ip = ask_ip()
	ws.settimeout(0.1)
	return ws


def main():
	page = 0
	try:
		ws = connect_to_esp32()
		while True:
			try:
				try:
					msg = ws.recv()
					page = int(msg)
				except (websocket.WebSocketTimeoutException, ValueError):
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
			except ConnectionResetError:
				print("Lost connection to ESP32.")
				print("Retrying...")
				ws = connect_to_esp32()
	except KeyboardInterrupt:
		ws.close()
		sys.exit(0);

if __name__ == "__main__":
	main()
