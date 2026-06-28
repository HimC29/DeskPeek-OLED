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
| SW      | GPIO 34 |

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

Edit `pc/main.py` and set the IP address shown on the OLED:

```python
ws.connect("ws://YOUR_ESP32_IP:81")
```

Then run:

```bash
python pc/main.py
```

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
