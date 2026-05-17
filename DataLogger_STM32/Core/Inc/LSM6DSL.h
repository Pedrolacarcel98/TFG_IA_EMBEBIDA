/*
 * LSM6DSL.h
 *
 *  Created on: Feb 7, 2025
 *      Author: Angel Jimenez
 */

#ifndef INC_LSM6DSL_H_
#define INC_LSM6DSL_H_

#define LSM6DSL_ADDR 0xD4


#define REG_CTRL1_XL 	0x10	//Registo de control 1
#define REG_STATUS		0x1E	//Registro de estado
#define REG_OUTX_L_XL	0x28	//LSB del eje X del acelerometro

#define ODR_XL_PowerDown 0x00
#define ODR_XL_104Hz 0x40
#define ODR_XL_208Hz 0x50
#define ODR_XL_416Hz 0x60
#define ODR_XL_833Hz 0x70
#define ODR_XL_1660Hz 0x80
#define ODR_XL_3330Hz 0x90
#define ODR_XL_6660Hz 0xA0

#define MPU6050_ADDR         (0x68 << 1)
#define REG_CONFIG           0x1A
#define REG_GYRO_CONFIG      0x1B
#define REG_ACCEL_CONFIG     0x1C
#define REG_ACCEL_XOUT_H     0x3B
#define REG_PWR_MGMT_1       0x6B
#define REG_WHO_AM_I         0x75

void MPU6050_Init();
void LSM6DSL_Init();

uint8_t LSM6DSL_DataReady();

void LSM6DSL_ReadAccel(float accel[]);

void MPU6050_ReadAccel(float accel[]);
#endif /* INC_LSM6DSL_H_ */
