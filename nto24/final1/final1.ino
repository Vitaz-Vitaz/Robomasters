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
#define accel_freq 1000

#define sync_smoothing_cof 0  // 0-1

#define sync_cof_p 0.1
#define sync_cof_i 0//0.001
#define sync_cof_d 0//10

#define stop_cof_p 1
#define stop_cof_i 0.001
#define stop_cof_d 15


#include "init.h"
#include "func.h"

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
    if (steps) {  // waiting encoders or new command
        bool finish = false;
        if (fabs(lpower) >= fabs(rpower)) {
            if (lsteps - last_le >= need_steps) finish = true;
        }
        else {
            if (rsteps - last_re >= need_steps) finish = true;
        }

        if (finish){
            // save last error
            if (lpower != 0 && rpower != 0) {
                if (fabs(lpower) >= fabs(rpower)) {
                    last_le += need_steps;
                    last_re += need_steps * (rpower / lpower);
                }
                else {
                    last_le += need_steps * (lpower / rpower);
                    last_re += need_steps;
                }
            }
            else {
                if (lpower != 0) last_le += need_steps;
                else if (rpower != 0) last_re += need_steps;
            }

            // waiting new command
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
                    float dist = ((lsteps - last_le) / lpower + (rsteps - last_re) / rpower) / 2;
                    last_le += dist * lpower;
                    last_re += dist * rpower;
                }
                else {
                    if (lpower != 0) last_le = lsteps;
                    else if (rpower != 0) last_re = rsteps;
                }

                // for reset pid cheker
                float last_lpower = lpower;
                float last_rpower = rpower;

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
            }
        }
    }

    if (millis() - last_sync_tic >= 1000. / sync_freq) {  // sync tic
        //last_sync_tic == millis();
        last_sync_tic += 1000. / sync_freq;

        // calculating control action
        lu = sync(&lsync_error, lpower, rpower, lsteps, last_le, rsteps, last_re, &lstop_i, &lstop_le, &lsync_i, &lsync_le);
        ru = sync(&rsync_error, rpower, lpower, rsteps, last_re, lsteps, last_le, &rstop_i, &rstop_le, &rsync_i, &rsync_le);
    }

    if (millis() - last_accel_tic >= 1000. / accel_freq) {  // accel tic
        //last_sync_tic == millis();
        last_accel_tic += 1000. / accel_freq;

        // calculating new power with accel
        float speed_bonus = accel * (millis() - start_accel_timer);
        float new_lpower = 0, new_rpower = 0;
        if (fabs(lpower) >= fabs(rpower)) {
            if (lpower != 0) {
                if (rpower != 0) {
                    new_lpower = start_power * (lpower / rpower) + speed_bonus;
                    new_rpower = start_power + speed_bonus * (rpower / lpower);
                    if ((accel >= 0 && new_lpower > finish_power) || (accel < 0 && new_lpower < finish_power)) {
                        new_lpower = finish_power;
                        new_rpower = finish_power * (rpower / lpower);
                    }
                }
                else {
                    new_lpower = start_power + speed_bonus;
                    if ((accel >= 0 && new_lpower > finish_power) || (accel < 0 && new_lpower < finish_power)) new_lpower = finish_power;
                }
            }
        }
        else {
            if (lpower != 0) {
                new_lpower = start_power + speed_bonus * (lpower / rpower);
                new_rpower = start_power * (rpower / lpower) + speed_bonus;
                if ((accel >= 0 && new_rpower > finish_power) || (accel < 0 && new_rpower < finish_power)) {
                    new_lpower = finish_power * (lpower / rpower);
                    new_rpower = finish_power;
                }
            }
            else {
                new_rpower = start_power + speed_bonus;
                if ((accel >= 0 && new_rpower > finish_power) || (accel < 0 && new_rpower < finish_power)) new_rpower = finish_power;
            }
        }

        // apply control action
        new_lpower += lu * new_lpower;
        new_rpower += ru * new_rpower;

        // Serial.println(lpower);
        // Serial.println(rpower);
        Serial.print(new_lpower);
        Serial.print("\t");
        Serial.print(new_rpower);
        Serial.println();

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
                lm.set_power(new_lpower);
                rm.set_power(new_rpower);
            // if too high power
            // if (new_lpower > 100 || new_lpower < -100 || new_rpower > 100 || new_rpower < -100){
            //     float max;
            //     if (fabs(new_lpower) >= fabs(new_rpower)) max = fabs(new_lpower);
            //     else max = fabs(new_rpower);
            //     lm.set_power(new_lpower / max * 100);
            //     lm.set_power(new_rpower / max * 100);
            // }
            // else {
            //     lm.set_power(new_lpower);
            //     rm.set_power(new_rpower);
            // }
        }
    }
}