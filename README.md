# DeskPeek-OLED

A wireless OLED system monitor powered by an ESP32. Your PC sends live stats over Wi-Fi via WebSockets and displays them on a small SSD1306 screen on your desk. Use the rotary encoder to switch between pages.

## Pages

- **System** — CPU %, RAM %, download and upload speed
- **Clock** — current time and date

## Hardware

- ESP32 board (any standard DevKit)
- SSD1306 OLED display (128x64, I2C)
- KY-040 rotary encoder

## Wiring

### OLED (I2C)

| OLED | ESP32 |
|------|-------|
| VCC  | 3.3V  |
| GND  | GND   |
| SDA  | GPIO 21 |
| SCL  | GPIO 22 |

### Rotary Encoder (KY-040)

| Encoder | ESP32 |
|---------|-------|
| VCC     | 3.3V  |
| GND     | GND   |
| CLK     | GPIO 32 |
| DT      | GPIO 33 |
| SW      | GPIO 25 |

## Requirements

### Firmware
- [PlatformIO CLI](https://docs.platformio.org/en/latest/core/installation/index.html)
- Libraries are declared in `platformio.ini` and installed automatically

### PC
- Python 3
- `psutil` — `pip install psutil`
- `websocket-client` — `pip install websocket-client`

## Setup

### 1. Firmware

Copy the example secrets file and fill in your Wi-Fi credentials:

```bash
cp firmware/include/secrets.h.example firmware/include/secrets.h
nano firmware/include/secrets.h
```

Then build and upload:

```bash
cd firmware
pio run -t upload
```

The OLED will show the ESP32's IP address once connected to Wi-Fi.

### 2. PC sender

On first run the script will prompt you to enter the ESP32 IP address shown on the OLED. This is saved to `config.json` automatically and reused on subsequent runs. To change the IP, delete `config.json` and restart the script.

Then run:

```bash
python pc/main.py
```

## Version

Press the rotary encoder button to display the current firmware version on the OLED for 1 second. The PC sender also prints its version to the terminal on startup.

## Changelog
> The firmware and PC script versions must match. Always update both together.

### v0.2.1
- Fixed page switch latency by moving send/receive into separate threads
- Fixed stale/null data briefly showing on page switch due to stats collection blocking the send loop
- Stats are now collected continuously in a background thread, independent of page state
- Fixed potential crash on malformed JSON in firmware WebSocket handler

### v0.2.0
- IP address prompt on first run, saved to config.json
- Auto-reconnect when connection to ESP32 is lost
- Refactored Python sender into proper functions

### v0.1.0
- Initial release
- Wi-Fi connection with status display on OLED
- WebSocket communication between ESP32 and PC
- System page — live CPU, RAM, download and upload speed
- Clock page — current time and date
- Rotary encoder page switching with wrap-around

## Project Structure

```
DeskPeek-OLED/
├── firmware/
│   ├── src/
│   │   └── main.cpp
│   ├── include/
│   │   ├── secrets.h          # your credentials (gitignored)
│   │   └── secrets.h.example
│   └── platformio.ini
└── pc/
    └── main.py
```
