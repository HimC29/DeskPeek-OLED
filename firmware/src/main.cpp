#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <WiFi.h>
#include <WebSocketsServer.h>
#include <ArduinoJson.h>
#include "secrets.h"

const char* VERSION = "v0.2.0";

#define SCREEN_WIDTH   128
#define SCREEN_HEIGHT  64
#define OLED_RESET     -1
#define SCREEN_ADDRESS 0x3c

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

WebSocketsServer webSocket(81);

const char* ssid = WIFI_SSID;
const char* pass = WIFI_PASS;

enum Pages {
	SYSTEM_INFO,
	CLOCK,
	NUM_PAGES
};

inline Pages operator++(Pages& p, int) {
    Pages original = p;
    p = static_cast<Pages>((p + 1) % NUM_PAGES);
    return original;
}

inline Pages operator--(Pages& p, int) {
    Pages original = p;
    p = static_cast<Pages>((p + NUM_PAGES - 1) % NUM_PAGES);
    return original;
}

Pages page = SYSTEM_INFO;

uint8_t connectedClient = 0;

const byte CLK_PIN = 32;
const byte DT_PIN = 33;
const byte SW_PIN = 25;

static volatile int rotaryDelta = 0;
static int lastState = 0;
static int8_t accumulator = 0;

static void IRAM_ATTR encoderISR() {
    static const int8_t enc_states[] = {
        0, -1, 1, 0,
        1,  0, 0, -1,
       -1,  0, 0,  1,
        0,  1, -1,  0
    };
    int currentState = (digitalRead(CLK_PIN) << 1) | digitalRead(DT_PIN);
    int8_t step = enc_states[(lastState << 2) | currentState];
    lastState = currentState;
    if (step != 0) {
        accumulator += step;
        if (accumulator >= 4) {
            accumulator = 0;
            rotaryDelta++;
        } else if (accumulator <= -4) {
            accumulator = 0;
            rotaryDelta--;
        }
    }
}

void initRotaryInterrupt() {
    pinMode(CLK_PIN, INPUT_PULLUP);
    pinMode(DT_PIN, INPUT_PULLUP);
    lastState = (digitalRead(CLK_PIN) << 1) | digitalRead(DT_PIN);
    accumulator = 0;
    attachInterrupt(digitalPinToInterrupt(CLK_PIN), encoderISR, CHANGE);
    attachInterrupt(digitalPinToInterrupt(DT_PIN), encoderISR, CHANGE);
}

int readRotary() {
    if (rotaryDelta == 0) return 0;
    noInterrupts();
    int delta = rotaryDelta;
    rotaryDelta = 0;
    interrupts();
    return delta;
}

void printInfo(const char* key, JsonVariant value) {
	display.print(key);
	display.print(": ");
 	display.println(value.as<String>());
}

void systemInfo(JsonDocument doc) {
	display.setCursor(0, 0);
 	display.setTextSize(2);
	display.clearDisplay();
	printInfo("CPU", doc["cpu"]);
 	printInfo("RAM", doc["ram"]);
 	display.setTextSize(1);
 	printInfo("Download", doc["download"]);
 	printInfo("Upload", doc["upload"]);
	display.display();
}

void showClock(JsonDocument doc) {
	display.setCursor(0, 0);
	display.setTextSize(2);
	display.clearDisplay();
	display.print(doc["time"].as<String>());
	display.display();
}

void onWebSocketEvent(uint8_t clientId, WStype_t type, uint8_t* payload, size_t length) {
	 if (type == WStype_CONNECTED) {
		Serial.println("client connected");
		connectedClient = clientId;
		String pageStr = String((int)page);
		webSocket.sendTXT(connectedClient, pageStr);
	 } else if (type == WStype_TEXT) {
	 	JsonDocument doc;
	 	deserializeJson(doc, payload);
	 	if (page == SYSTEM_INFO) {
			systemInfo(doc);
	 	}
	 	else if (page == CLOCK) {
			showClock(doc);
	 	}
	 }
}

void setup() {
	Serial.begin(115200);

	if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
		Serial.println("Failed to init SSD1306");
		for(;;);
	}

	initRotaryInterrupt();
	pinMode(SW_PIN, INPUT_PULLUP);

	display.clearDisplay();

	display.setTextSize(1);
	display.setTextColor(SSD1306_WHITE);
	display.setCursor(0, 0);
	display.println("Connecting to wifi");
	display.display();

	WiFi.begin(ssid, pass);
	while (WiFi.status() != WL_CONNECTED) {
		display.print(".");
		display.display();
		delay(500);
	}
	display.println();

	display.print("Connected to ");
	display.print(ssid);
	display.println("!");

	display.print("\nIP:");
	display.println(WiFi.localIP());

	display.display();

	webSocket.begin();
	webSocket.onEvent(onWebSocketEvent);
}

void loop() {
	webSocket.loop();

	int delta = readRotary();
	if (delta != 0) {
		if (delta > 0) {
			page++;
		} else if (delta < 0) {
			page--;
		}
		String pageStr = String((int)page);
		webSocket.sendTXT(connectedClient, pageStr);
	}
	if (digitalRead(SW_PIN) == LOW) {
		display.clearDisplay();
		display.setCursor(0, 0);
		display.println(VERSION);
		display.display();
		delay(1000);
	}
}
