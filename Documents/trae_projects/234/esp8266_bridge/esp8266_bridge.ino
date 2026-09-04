#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

// ===================== CONFIGURE THESE =====================
const char* WIFI_SSID     = "Airtel_A_1306";      
const char* WIFI_PASSWORD = "0007176282308";  
const int   UDP_PORT      = 4210;
const int   SERIAL_BAUD   = 115200; // Increased to 115200
// ===========================================================

WiFiUDP udp;

void setup() {
  Serial.begin(SERIAL_BAUD);
  delay(500);
  Serial.println("");
  Serial.println("--- ESP8266 WIFI BRIDGE STARTING ---");

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.print("Connecting to ");
  Serial.println(WIFI_SSID);

  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print("."); // This shows you it's trying to connect
  }

  Serial.println("");
  Serial.println("WiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP()); // THIS IS WHAT YOU NEED
  
  udp.begin(UDP_PORT);
}

void loop() {
  int packetSize = udp.parsePacket();
  if (packetSize > 0) {
    uint8_t buf[64];
    int len = udp.read(buf, sizeof(buf));
    if (len > 0) {
      Serial.write(buf, len);
    }
  }
}