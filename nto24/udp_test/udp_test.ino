#include <WiFi.h>
#include <WiFiUdp.h>

const char* ssid = "ITMO-NTO-robot";
const char* password = "Pass-2503ntor";
// const char* ssid = "Mi_9TPro";
// const char* password = "password";

#define BUFFER_LEN 105

WiFiUDP udp;
const int udpPort = 11105;
uint8_t buffer[BUFFER_LEN];

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  delay(1000);

  WiFi.mode(WIFI_STA); //Optional
  WiFi.begin(ssid, password);
  Serial.println("\nConnecting");

  while(WiFi.status() != WL_CONNECTED){
    Serial.print(".");
    delay(100);
  }

  Serial.println("\nConnected to the WiFi network");
  Serial.print("Local ESP32 IP: ");
  Serial.println(WiFi.localIP());

  udp.begin(udpPort);
}

void loop() {
  udp.parsePacket();
  int a = udp.read(buffer, BUFFER_LEN);
  delay(100);
  if(a > 0) {
    Serial.println(a);
    Serial.println((char *)buffer);

    uint8_t type = buffer[0];
    Serial.println(type);
    
    float par1;
    memcpy(&par1, {buffer[1], buffer[2], buffer[3], buffer[4]}, 4);
    Serial.println(par1);

    Serial.println();
  }
}
