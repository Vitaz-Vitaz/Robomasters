#include <WiFi.h>
#include <WiFiUdp.h>

const char* ssid = "ITMO-NTO-robot";
const char* password = "Pass-2503ntor";
// const char* ssid = "Mi_9TPro";
// const char* password = "password";

#define BUFFER_LEN 105
#define udp_freq 1000

WiFiUDP udp;
const int udpPort = 11105;
uint8_t buffer[BUFFER_LEN];
uint32_t last_udp_tic = 0;
byte pc_ip[4];
uint16_t port;


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

#define sync_freq 100

#define sync_smoothing 4

#define sync_cof_p 1 //1.5
#define sync_cof_i 0.03
#define sync_cof_d 2

#define stop_cof_p 10
#define stop_cof_i 0.1
#define stop_cof_d 10


#include "init.h"
#include "func.h"

Smoother lsync_error;
Smoother rsync_error;

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
    
    lsync_error.init();
    rsync_error.init();

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
    last_udp_tic = millis();
    delay(1000);
}

// void loop() {}


void loop() {
    if (steps) {  // waiting encoders or new command
        bool finish = false;
        if (fabs(lpower) >= fabs(rpower)) {
            if (fabs(lsteps - last_le) >= need_steps) finish = true;
        }
        else {
            if (fabs(rsteps - last_re) >= need_steps) finish = true;
        }

        if (finish){
            // save last error
            if (lpower != 0 && rpower != 0) {
                if (fabs(lpower) >= fabs(rpower)) {
                    if (lpower >= 0) last_le += need_steps;
                    else last_le -= need_steps;
                    if (rpower >= 0) last_re += need_steps * fabs(rpower / lpower);
                    else last_re -= need_steps * fabs(rpower / lpower);
                }
                else {
                    if (lpower >= 0) last_le += need_steps * fabs(lpower / rpower);
                    else last_le -= need_steps * fabs(lpower / rpower);
                    if (rpower >= 0) last_re += need_steps;
                    else last_re -= need_steps;
                }
            }
            else {
                if (lpower != 0) {
                  if (lpower >= 0) last_le += need_steps;
                  else last_le -= need_steps;
                }
                else if (rpower != 0) {
                  if (rpower >= 0) last_re += need_steps;
                  else last_re -= need_steps;
                }
            }

            // waiting new command
            IPAddress ip(pc_ip[0], pc_ip[1], pc_ip[2], pc_ip[3]);
            udp.beginPacket(ip, port);
            udp.write(0x00);
            udp.endPacket();
            while (udp.read(buffer, BUFFER_LEN) == 0) udp.parsePacket(); // new commands cheker
            new_command_handler();
        }
    }
    else {
        if (millis() - last_udp_tic >= 1000. / udp_freq) {  // new commands cheker
            last_udp_tic += 1000. / udp_freq;
            udp.parsePacket();
            if (udp.read(buffer, BUFFER_LEN) > 0) {
                // save last error
                if (lpower != 0 && rpower != 0) {
                    double enc1 = (lsteps - last_le) / lpower;
                    double enc2 = (rsteps - last_re) / rpower;
                    double dist = (enc1 + enc2) / 2.;
                    last_le += dist * lpower;
                    last_re += dist * rpower;
                }
                else {
                    if (lpower != 0) last_le = lsteps;
                    else if (rpower != 0) last_re = rsteps;
                }

                // for reset pid cheker
                double last_lpower = lpower;
                double last_rpower = rpower;

                // get new command
                new_command_handler();

                // reset stop pid if need it
                if (lpower == 0 && last_lpower != 0) {
                    lstop_le = 0;
                    lstop_i = 0;
                }
                if (rpower == 0 && last_rpower != 0) {
                    rstop_le = 0;
                    rstop_i = 0;
                }
                Serial.println();
            }
        }
    }

    if (millis() - last_sync_tic >= 1000. / sync_freq) {  // sync tic
        last_sync_tic += 1000. / sync_freq;

        // calculating control action
        lu = sync(&lsync_error, lpower, rpower, lsteps, last_le, rsteps, last_re, &lstop_i, &lstop_le, &lsync_i, &lsync_le);
        // Serial.println(2);
        ru = sync(&rsync_error, rpower, lpower, rsteps, last_re, lsteps, last_le, &rstop_i, &rstop_le, &rsync_i, &rsync_le);
        // Serial.println(3);


        // apply control action
        double new_lpower = lpower + lu * lpower;
        double new_rpower = rpower + ru * rpower;

        Serial.print(lsync_error.get(), 10);
        Serial.print("\t");
        Serial.println(rsync_error.get(), 10);

        // Serial.print(new_lpower, 4);
        // Serial.print("\t");
        // Serial.print(new_rpower, 4);
        // Serial.print("\t");

        // set power to motors
        if (lpower == 0) {
            lm.set_power(lu);
            if (rpower == 0) rm.set_power(ru);
            else rm.set_power(new_rpower);
        }
        else if (rpower == 0) {
            lm.set_power(new_lpower);
            rm.set_power(ru);
        }
        else {
            // if too high power
            if (new_lpower > 100 || new_lpower < -100 || new_rpower > 100 || new_rpower < -100) {
                double max;
                if (fabs(new_lpower) >= fabs(new_rpower)) max = fabs(new_lpower);
                else max = fabs(new_rpower);
                new_lpower = (new_lpower / max) * 100.;
                new_rpower = (new_rpower / max) * 100.;
            }

            // Serial.print(new_lpower, 4);
            // Serial.print("\t");
            // Serial.println(new_rpower, 4);

            lm.set_power(new_lpower);
            rm.set_power(new_rpower);
        }
    }
}