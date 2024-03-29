#define RM1 32
#define RM2 4
#define RE1 14
#define RE2 12

#define LM1 18
#define LM2 19
#define LE1 15
#define LE2 5

#define pwm_freq 18000
#define LMChenel 0
#define LMChenel2 1
#define RMChenel 2
#define RMChenel2 3
#define pwm_resolution 10

#define sync_freq 100
#define accel_freq 1000

#define sync_smoothing_cof 0.5  // 0-1

#define sync_cof_p 0.5
#define sync_cof_i 0.001
#define sync_cof_d 10

#define stop_cof_p 1
#define stop_cof_i 0.001
#define stop_cof_d 15


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


float sync (float* sync_error, float power1, float power2, int32_t steps1, double last1, int32_t steps2, double last2, float* stop_i, float* stop_le, float* sync_i, float* sync_le) {
    if (power1 == 0) {
        float error = steps1 - last1;
        float p = error * stop_cof_p;
        *stop_i += error * stop_cof_i;
        float d = (error - *stop_le) * stop_cof_d;
        *stop_le = error;
        float u = p + *stop_i + d;
        return u;
    }
    else if (power2 == 0) {
        float u = *sync_i;
        return u;
        // float u = *sync_i * power1;
        // return power1 + u;
    }
    else {
        float error = (steps1 - last1) / power1 - (steps2 - last2) / power2;
        error = -error;
        *sync_error = sync_smoothing_cof * *sync_error + (1. - sync_smoothing_cof) * error;
        float p = *sync_error * sync_cof_p;
        *sync_i += *sync_error * sync_cof_i;
        float d = (*sync_error - *sync_le) * sync_cof_d;
        *sync_le = *sync_error;
        float u = p + *sync_i + d;
        return u;
        // float u = (p + *sync_i + d) * power1;
        // return power1 + u;
    }
}


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

uint32_t last_sync_tic = 0;
float lsync_error = 0, rsync_error = 0;
float lsync_le = 0, lsync_i = 0;
float lstop_le = 0, lstop_i = 0;
float rsync_le = 0, rsync_i = 0;
float rstop_le = 0, rstop_i = 0;
float lu = 0, ru = 0;

double last_le = 0;
double last_re = 0;
float lpower = 1;
float rpower = 1;

uint32_t last_accel_tic = 0;
float accel = 0;
float start_power = 70;
float finish_power = 70;
uint32_t start_accel_timer = 0;

bool steps = false;
float need_steps = 0;


void new_command_handler(int8_t command) {
    if (false) {  // command move motors with power and accel
        // parameters
        lpower = 99;
        rpower = 88;
        accel = -1.2; // for faster motor
        start_power = 20; // for slowest no stop motor
        finish_power = 80; // for faster motor

        steps = false;
        start_accel_timer = millis();
    }
    else if (false) {  // command move motors with power and accel with encoders
        // parameters
        lpower = 99;
        rpower = 88;
        accel = -1.2; // for faster motor
        start_power = 20; // for slowest no stop motor
        finish_power = 80; // for faster motor
        need_steps = -105; // for fastest motor

        steps = true;
        start_accel_timer = millis();
    }
}


void setup() {
    Serial.begin(115200);


    lm.init(LM1, LM2, pwm_freq, LMChenel, LMChenel2, pwm_resolution);
    // le.init(LE1, LE2);
    attachInterrupt(LE1, lstepper, RISING);
    rm.init(RM1, RM2, pwm_freq, RMChenel, RMChenel2, pwm_resolution);
    // re.init(RE1, RE2);
    attachInterrupt(RE1, rstepper, RISING);

    last_sync_tic = millis();
    last_accel_tic = millis();

    // lm.set_power(50);
    // rm.set_power(-50);
    // delay(10000);

    // while (true){
    //   //Serial.print(lsteps); Serial.print("\t"); Serial.println(rsteps);
    // }
}

// void loop() {
//   delay(100);
// }

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
            while (false) { // new commands cheker
                new_command_handler(105);
            }
        }
    }
    else if (false) {  // new commands cheker
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
        new_command_handler(7-8);

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

        Serial.println(lpower);
        Serial.println(rpower);
        Serial.println(new_lpower);
        Serial.println(new_rpower);
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
            // if too high power
            if (new_lpower > 100 || new_lpower < -100 || new_rpower > 100 || new_rpower < -100){
                float max;
                if (fabs(new_lpower) >= fabs(new_rpower)) max = fabs(new_lpower);
                else max = fabs(new_rpower);
                lm.set_power(new_lpower / max * 100);
                lm.set_power(new_rpower / max * 100);
            }
            else {
                lm.set_power(new_lpower);
                rm.set_power(new_rpower);
            }
        }
    }
}