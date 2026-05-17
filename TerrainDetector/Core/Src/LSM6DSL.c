/*
 * LSM6DSL.c
 *
 *  Created on: Feb 7, 2025
 *      Author: Angel Jimenez
 */




#include "stm32l4xx_hal.h"
#include "LSM6DSL.h"

extern I2C_HandleTypeDef hi2c1;

void LSM6DSL_Init(){

	uint8_t buffer[1];
	buffer[0] = ODR_XL_416Hz;
	HAL_I2C_Mem_Write(&hi2c1, LSM6DSL_ADDR, REG_CTRL1_XL, I2C_MEMADD_SIZE_8BIT, buffer, 1, 1000);

}

uint8_t LSM6DSL_DataReady(){

	uint8_t buffer[1];
    HAL_I2C_Mem_Read(&hi2c1, LSM6DSL_ADDR, REG_STATUS, I2C_MEMADD_SIZE_8BIT, buffer, 1, 1000);
    return ((buffer[0] & 0x01) != 0);

}

void LSM6DSL_ReadAccel(float accel[]){

	uint8_t buffer[6];

	HAL_I2C_Mem_Read(&hi2c1, LSM6DSL_ADDR, REG_OUTX_L_XL, I2C_MEMADD_SIZE_8BIT, buffer, 6, 1000);

	for(uint8_t i = 0; i < 3; i++){
		accel[i] = ((int16_t)(buffer[2*i+1]<<8) | buffer[2*i])*0.061f;
	}

}


void MPU6050_Init() {
    uint8_t check, data;

    // 1. Comprobar si el sensor responde (Who Am I)
    HAL_I2C_Mem_Read(&hi2c1, MPU6050_ADDR, REG_WHO_AM_I, 1, &check, 1, 1000);

    if (check == 0x68) { // 0x68 es el ID por defecto del MPU6050
        // 2. Despertar el sensor (Escribir 0 en PWR_MGMT_1)
        data = 0;
        HAL_I2C_Mem_Write(&hi2c1, MPU6050_ADDR, REG_PWR_MGMT_1, 1, &data, 1, 1000);

        // 3. Configurar Acelerómetro a +/- 2g (Escribir 0 en ACCEL_CONFIG)
        data = 0x00;
        HAL_I2C_Mem_Write(&hi2c1, MPU6050_ADDR, REG_ACCEL_CONFIG, 1, &data, 1, 1000);
    }
}


void MPU6050_ReadAccel(float accel[]) {
    uint8_t buffer[6];

    // Leemos los 6 registros de aceleración (Xh, Xl, Yh, Yl, Zh, Zl)
    if (HAL_I2C_Mem_Read(&hi2c1, MPU6050_ADDR, REG_ACCEL_XOUT_H, 1, buffer, 6, 1000) == HAL_OK) {

        // Reconstrucción: Shift 8 bits al primero y OR con el segundo
        int16_t rawX = (int16_t)(buffer[0] << 8 | buffer[1]);
        int16_t rawY = (int16_t)(buffer[2] << 8 | buffer[3]);
        int16_t rawZ = (int16_t)(buffer[4] << 8 | buffer[5]);

        // Sensibilidad para +/- 2g es 16384 LSB/g
        accel[0] = rawX / 16384.0f;
        accel[1] = rawY / 16384.0f;
        accel[2] = rawZ / 16384.0f;
    }
}
