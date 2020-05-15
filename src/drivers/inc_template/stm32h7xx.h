#ifndef __STM32H7XX_CAN_H
#define __STM32H7XX_CAN_H

#include "static.h"
#include "stm32h7xx_hal.h"
#include "bus.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif // __cplusplus

// BUILD CAN_Raw_Bus_T

typedef uint32_t Time_T; // in ms
typedef HAL_StatusTypeDef CANlib_Transmit_Error_T;
typedef HAL_StatusTypeDef CANlib_Init_Error_T;

CANlib_Transmit_Error_T CANlib_TransmitFrame(Frame *frame, CANlib_Bus_T bus);
void CANlib_ReadFrame(Frame *frame, CANlib_Bus_T bus);

#ifdef __cplusplus
} // extern "C"
#endif // __cplusplus

#endif // __STM32H7XX_CAN_H
