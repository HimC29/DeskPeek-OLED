import sys
import websocket
import json
import psutil
from datetime import datetime
import threading
import os
import time

VERSION = "v0.2.2"

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
		return None

def connect_to_esp32():
	ip = load_ip()
	if ip is None:
		ip = ask_ip()
	while True:
		ws = websocket.WebSocket()  # create a new one every attempt
		try:
			ws.connect(f"ws://{ip}:81")
			print("Connected successfully!")
			ws.settimeout(0.1)
			return ws
		except (OSError, websocket.WebSocketAddressException, websocket.WebSocketTimeoutException, ConnectionRefusedError):
			ip = ask_ip()
			
latest_stats = {
	"cpu": "0%",
	"ram": "0%",
	"download": "0.00 KB/s",
	"upload": "0.00 KB/s"
}

def get_system_stats():
	net_before = psutil.net_io_counters()
	cpu = psutil.cpu_percent(interval=1)
	net_after = psutil.net_io_counters()
	download = (net_after.bytes_recv - net_before.bytes_recv) / 1024
	upload = (net_after.bytes_sent - net_before.bytes_sent) / 1024
	ram = psutil.virtual_memory().percent
	return {
		"cpu": f"{cpu}%",
		"ram": f"{ram}%",
		"download": f"{download:.2f} KB/s",
		"upload": f"{upload:.2f} KB/s"
	}

stats_lock = threading.Lock()

def collect_stats():
	while True:
		stats = get_system_stats()
		with stats_lock:
			latest_stats.update(stats)

page_changed = threading.Event()
reconnect_event = threading.Event()

def receiver(ws, page_ref, stop_event):
	while not stop_event.is_set():
		try:
			msg = ws.recv()
			page_ref[0] = int(msg)
			page_changed.set()
		except (websocket.WebSocketTimeoutException, ValueError):
			pass
		except (ConnectionResetError, websocket.WebSocketConnectionClosedException, OSError) as e:
			print(f"Receiver error: {e}")
			reconnect_event.set()
			break

def sender(ws, page_ref, stop_event):
	page_changed.wait(timeout=2)
	while not stop_event.is_set():
		page_changed.wait(timeout=0.1)
		page_changed.clear()
		p = page_ref[0]
		try:
			if p == 0:
				with stats_lock:
					data = dict(latest_stats)
				ws.send(json.dumps(data))
			elif p == 1:
				data = {"time": datetime.now().strftime("%H:%M:%S")}
				ws.send(json.dumps(data))
		except (ConnectionResetError, websocket.WebSocketConnectionClosedException, OSError) as e:
			print(f"Sender error: {e}")
			reconnect_event.set()
			break

def main():
	t = threading.Thread(target=collect_stats, daemon=True)
	t.start()
	try:
		while True:
			reconnect_event.clear()
			ws = connect_to_esp32()
			page_ref = [0]
			stop_event = threading.Event()

			t_recv = threading.Thread(target=receiver, args=(ws, page_ref, stop_event), daemon=True)
			t_send = threading.Thread(target=sender, args=(ws, page_ref, stop_event), daemon=True)
			t_recv.start()
			t_send.start()

			reconnect_event.wait()
			print("Lost connection to ESP32, reconnecting...")
			stop_event.set()  # tell threads to stop
			page_changed.set()  # unblock sender if it's waiting
			ws.close()

	except KeyboardInterrupt:
		ws.close()
		sys.exit(0)

if __name__ == "__main__":
	main()
