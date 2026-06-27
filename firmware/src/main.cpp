#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <WiFi.h>
#include <WebSocketsServer.h>
#include <ArduinoJson.h>
#include "secrets.h"

#define SCREEN_WIDTH   128
#define SCREEN_HEIGHT  64
#define OLED_RESET     -1
#define SCREEN_ADDRESS 0x3c

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

WebSocketsServer webSocket(81);

const char* ssid = WIFI_SSID;
const char* pass = WIFI_PASS;

void onWebSocketEvent(uint8_t clientId, WStype_t type, uint8_t* payload, size_t length) {
	 if (type == WStype_CONNECTED) {
		Serial.println("client connected");
	 }
	 else if (type == WStype_TEXT) {
	 	JsonDocument doc;
	 	deserializeJson(doc, payload);
	 	display.setCursor(0, 0);
	 	display.setTextSize(2);
		display.clearDisplay();
	 	display.print("CPU: ");
	 	display.println(doc["cpu"].as<int>());
	 	display.print("RAM: ");
	 	display.println(doc["ram"].as<int>());
	 	display.display();
	 }
}

void setup() {
	Serial.begin(115200);

	if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
		Serial.println("Failed to init SSD1306");
		for(;;);
	}

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
}
