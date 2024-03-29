#include <WiFi.h>
#include <WiFiUdp.h>

const char* ssid = "ITMO-NTO-robot";
const char* password = "Pass-2503ntor";
// const char* ssid = "Mi_9TPro";
// const char* password = "password";

#define BUFFER_LEN 105

uint8_t pc_ip[4];

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
  if(udp.read(buffer, BUFFER_LEN) > 0) {
    Serial.println((char *)buffer);

    pc_ip[0] = buffer[0];
    pc_ip[1] = buffer[1];
    pc_ip[2] = buffer[2];
    pc_ip[3] = buffer[3];

    uint16_t port;
    byte data[2] = {buffer[4], buffer[5]};
    memcpy(&port, &data, 2);
    // Serial.println(pc_ip[0]);
    // Serial.println(pc_ip[1]);
    // Serial.println(pc_ip[2]);
    // Serial.println(pc_ip[3]);
    IPAddress ip(pc_ip[0], pc_ip[1], pc_ip[2], pc_ip[3]);
    
    // Serial.println(port);


    udp.beginPacket(ip, port);
    udp.write(0x51);
    udp.endPacket();
  }
}
