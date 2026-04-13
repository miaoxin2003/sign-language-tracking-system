#include "stm32f10x.h"
#include "led.h"
#include "delay.h"
#include "key.h"
#include "sys.h"
#include "usart.h"
#include "serial.h"
#include "timer.h"
#include "pid.h"

PID_TypeDef PID_x, PID_y;

int coords[2];

u16 targetX = 320;
u16 targetY = 240;

int main(void)
{
    u16 pwmval_x, pwmval_y;

    delay_init();
    NVIC_PriorityGroupConfig(NVIC_PriorityGroup_2);
    uart_init(115200);
    LED_Init();
    KEY_Init();
    TIM3_PWM_Init(9999,143);

    pid_init(0.04, 0, 0.30, &PID_x);
    pid_init(0.05, 0, 0.30, &PID_y);

    coords[0] = 320;
    coords[1] = 240;

    pwmval_x = 650;
    pwmval_y = 650;

    while(1)
    {
        recieveData();
        if(USART_RX_STA & 0x8000)
        {
            printf("Received: %s\r\n", USART_RX_BUF);
            printf("Parsed Coords: X=%d, Y=%d\r\n", coords[0], coords[1]);
        }
        delay_ms(50);

        pwmval_x = pwmval_x + pid(coords[0],targetX, &PID_x);
        pwmval_y = pwmval_y - pid(coords[1],targetY, &PID_y);

        if(pwmval_x>300 && pwmval_x<1200)
            TIM_SetCompare1(TIM3,pwmval_x);
        if(pwmval_y>300 && pwmval_y<1000)
            TIM_SetCompare2(TIM3,pwmval_y);
        printf("PWM Values: X=%d, Y=%d\r\n", pwmval_x, pwmval_y);
        delay_ms(50);
    }
}