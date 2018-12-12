#include "can_raw.h"

#include "stm32f4xx_hal_can.h"
#include <stdint.h>

typedef HAL_StatusTypeDef CANlib_Transmit_Error_T;

HAL_StatusTypeDef CANlib_Init(uint32_t baudrate);
HAL_StatusTypeDef CANlib_TransmitFrame(Frame *frame);
