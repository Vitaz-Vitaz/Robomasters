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