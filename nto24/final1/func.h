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
        // error = -error;
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


void new_command_handler() {
    if (buffer[0] = 0) {  // command move motors with power and accel
        byte par1[4] = {buffer[1], buffer[2], buffer[3], buffer[4]};
        byte par2[4] = {buffer[5], buffer[6], buffer[7], buffer[8]};
        byte par3[4] = {buffer[9], buffer[10], buffer[11], buffer[12]};
        byte par4[4] = {buffer[13], buffer[14], buffer[15], buffer[16]};
        byte par5[4] = {buffer[17], buffer[18], buffer[19], buffer[20]};
        memcpy(&lpower, &par1, 4);
        memcpy(&rpower, &par2, 4);
        memcpy(&accel, &par3, 4);
        memcpy(&start_power, &par4, 4);
        memcpy(&finish_power, &par5, 4);

        // parameters
        // lpower = 99;
        // rpower = 88;
        // accel = -1.2; // for faster motor
        // start_power = 20; // for slowest no stop motor
        // finish_power = 80; // for faster motor

        steps = false;
        start_accel_timer = millis();
    }
    else if (buffer[0] = 1) {  // command move motors with power and accel with encoders
        byte par1[4] = {buffer[1], buffer[2], buffer[3], buffer[4]};
        byte par2[4] = {buffer[5], buffer[6], buffer[7], buffer[8]};
        byte par3[4] = {buffer[9], buffer[10], buffer[11], buffer[12]};
        byte par4[4] = {buffer[13], buffer[14], buffer[15], buffer[16]};
        byte par5[4] = {buffer[17], buffer[18], buffer[19], buffer[20]};
        byte par6[4] = {buffer[21], buffer[22], buffer[23], buffer[24]};
        memcpy(&lpower, &par1, 4);
        memcpy(&rpower, &par2, 4);
        memcpy(&accel, &par3, 4);
        memcpy(&start_power, &par4, 4);
        memcpy(&finish_power, &par5, 4);
        memcpy(&need_steps, &par6, 4);

        // // parameters
        // lpower = 99;
        // rpower = 88;
        // accel = -1.2; // for faster motor
        // start_power = 20; // for slowest no stop motor
        // finish_power = 80; // for faster motor
        // need_steps = -105; // for fastest motor

        steps = true;
        start_accel_timer = millis();
    }
}