float lpower = 1;
float rpower = 1;


class Motor {
    public:
    void init(uint8_t pin1, uint8_t pin2, uint32_t freq, uint8_t channel, uint8_t channel2, uint8_t resolution) {
        _channel2 = channel2;
        _channel = channel;
        _max_power = pow(2, resolution) - 1;

        ledcSetup(channel, freq, resolution);
        ledcAttachPin(pin1, channel);
        ledcAttachPin(pin2, channel2);
    }

    void set_power_raw(int16_t power) {
        if (power > _max_power) power = _max_power;
        else if (power < -_max_power) power = -_max_power;

        if (power >= 0) {
            ledcWrite(_channel2, 0);
            ledcWrite(_channel, power);
        }
        else {
            ledcWrite(_channel2, -power);
            ledcWrite(_channel, 0);
        }
    }

    void set_power(float power) {  // -100 - 100
        set_power_raw(power / 100 * _max_power);
    }

    private:
    uint8_t _channel2;
    uint8_t _channel;
    uint16_t _max_power;
};


#include <WiFi.h>
#include <WiFiUdp.h>

const char* ssid = "ITMO-NTO-robot";
const char* password = "Pass-2503ntor";
// const char* ssid = "Mi_9TPro";
// const char* password = "password";

#define BUFFER_LEN 105
#define udp_freq 1000

WiFiUDP udp;
const int udpPort = 11106;
uint8_t buffer[BUFFER_LEN];
uint32_t last_udp_tic = 0;


#define RM2 32
#define RM1 4
#define RE1 14
#define RE2 12

#define LM2 18
#define LM1 19
#define LE1 15
#define LE2 5

#define pwm_freq 20000
#define LMChenel 0
#define LMChenel2 1
#define RMChenel 2
#define RMChenel2 3
#define pwm_resolution 10


Motor lm;
// Encoder le;
volatile int32_t lsteps = 0;
void lstepper() {
    if (digitalRead(LE2)) lsteps += 1;
    else lsteps -= 1;
}
Motor rm;
// Encoder re;
volatile int32_t rsteps = 0;
void rstepper() {
    if (digitalRead(RE2)) rsteps += 1;
    else rsteps -= 1;
}


void setup() {
    Serial.begin(2000000);

    lm.init(LM1, LM2, pwm_freq, LMChenel, LMChenel2, pwm_resolution);
    // le.init(LE1, LE2);
    attachInterrupt(LE1, lstepper, RISING);
    rm.init(RM1, RM2, pwm_freq, RMChenel, RMChenel2, pwm_resolution);
    // re.init(RE1, RE2);
    attachInterrupt(RE1, rstepper, RISING);

    // lm.set_power(80);
    // rm.set_power(80);
    // delay(10000);

    // while (true){
    //   Serial.print(lsteps); Serial.print("\t"); Serial.println(rsteps);
    // }

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

    last_sync_tic = millis();
    last_accel_tic = millis();
    last_udp_tic = millis();
}

// void loop() {}


void loop() {
    if (millis() - last_udp_tic >= 1000. / udp_freq) {  // new commands cheker
        last_udp_tic += 1000. / udp_freq;
        udp.parsePacket();
        if (udp.read(buffer, BUFFER_LEN) > 0) {
            byte par1[4] = {buffer[1], buffer[2], buffer[3], buffer[4]};
            byte par2[4] = {buffer[5], buffer[6], buffer[7], buffer[8]};
            memcpy(&lpower, &par1, 4);
            memcpy(&rpower, &par2, 4);
            lm.set_power(lpower);
            rm.set_power(rpower);
        }
    }
}