#include "pid.h"

void pid_init(float Kp, float Ki, float Kd, PID_TypeDef* PID)
{
    PID->Kp = Kp;
    PID->Ki = Ki;
    PID->Kd = Kd;
    PID->i_out = 0;
    PID->last_error = 0;
}

int pid(int present, u16 target, PID_TypeDef* PID)
{
    PID->error = target - present;
    PID->p_out = PID->Kp * PID->error;
    PID->i_out += PID->Ki * PID->error;

    if (PID->i_out > 500) PID->i_out = 500;
    else if (PID->i_out < -500) PID->i_out = -500;

    PID->d_out = PID->Kd * (PID->error - PID->last_error);
    PID->output = PID->p_out + PID->i_out + PID->d_out;

    if (PID->output > 1000) PID->output = 1000;
    else if (PID->output < -1000) PID->output = -1000;

    PID->last_error = PID->error;
    return PID->output;
}

int better_pid(int present, u16 target, PID_TypeDef* PID)
{
    PID->error = target - present;
    PID->p_out = PID->Kp * PID->error;
    PID->i_out += PID->Ki * PID->error;
    PID->d_out = PID->Kd * 1/16 * (PID->error + 3*PID->last_error + 2*PID->last_error2 -2*PID->last_error3 - 3*PID->last_error4 - PID->last_error5);
    PID->output = PID->p_out + PID->i_out + PID->d_out;

    PID->last_error5 = PID->last_error4;
    PID->last_error4 = PID->last_error3;
    PID->last_error3 = PID->last_error2;
    PID->last_error2 = PID->last_error;
    PID->last_error = PID->error;

    return PID->output;
}

int incre_pid(int present, u16 target, PID_TypeDef* PID)
{
    PID->error = target - present;
    PID->p_out = PID->Kp * (PID->error - PID->last_error);
    PID->i_out += PID->Ki * PID->error;
    PID->d_out = PID->Kd * (PID->error - 2*PID->last_error + PID->last_error2);
    PID->output += PID->p_out + PID->i_out + PID->d_out;

    PID->last_error2 = PID->last_error;
    PID->last_error = PID->error;

    return PID->output;
}