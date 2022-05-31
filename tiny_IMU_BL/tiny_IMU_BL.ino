/*
  SAMBA 9-axis IMU with sensor fusion
  Communication using BLE
*/


#define  SERIAL_PORT_SPEED  115200

#if defined(ARDUINO_ARCH_SAMD)
  #define SerialMonitorInterface SerialUSB
#else
  #define SerialMonitorInterface Serial
#endif

#define BLE_DEBUG false

#include <SPI.h>
#include "lib_aci.h"
#include "aci_setup.h"
#include "uart_over_ble.h"
#include "services.h"

uint8_t ble_rx_buffer[21];
uint8_t ble_rx_buffer_len = 0;
uint8_t ble_connection_state = false;

#include <Wire.h>
#include "RTIMUSettings.h"
#include "RTIMU.h"
#include "RTFusionRTQF.h"
#ifndef ARDUINO_ARCH_SAMD
#include <EEPROM.h>
#endif

RTIMU *imu;                                           // the IMU object
RTFusionRTQF fusion;                                  // the fusion object
RTIMUSettings settings;                               // the settings object

unsigned long lastDisplay;
unsigned long lastRate;
int sampleCount;

void setup(void)
{
  int errcode;
  SerialMonitorInterface.begin(SERIAL_PORT_SPEED);
  
  Wire.begin();
    imu = RTIMU::createIMU(&settings);                        // create the imu object
  
    SerialMonitorInterface.print("ArduinoIMU starting using device "); SerialMonitorInterface.println(imu->IMUName());
    if ((errcode = imu->IMUInit()) < 0) {
        SerialMonitorInterface.print("Failed to init IMU: "); SerialMonitorInterface.println(errcode);
    }

    if (imu->getCalibrationValid())
        SerialMonitorInterface.println("Using compass calibration");
    else
        SerialMonitorInterface.println("No valid compass calibration data");

    lastDisplay = lastRate = millis();
    sampleCount = 0;

    // Slerp power controls the fusion and can be between 0 and 1
    // 0 means that only gyros are used, 1 means that only accels/compass are used
    // In-between gives the fusion mix.
    
    fusion.setSlerpPower(0.02);
    
    // use of sensors in the fusion algorithm can be controlled here
    // change any of these to false to disable that sensor
    
    fusion.setGyroEnable(true);
    fusion.setAccelEnable(true);
    fusion.setCompassEnable(true);

    imu->IMURead();
    fusion.newIMUData(imu->getGyro(), imu->getAccel(), imu->getCompass(), imu->getTimestamp());


  BLEsetup();
}

void loop() {

String msga,msgg,msgc,msgf;
  
  aci_loop();//Process any ACI commands or events from the NRF8001- main BLE handler, must run often. Keep main loop short.
  if (ble_rx_buffer_len) {//Check if data is available
    //SerialMonitorInterface.print(ble_rx_buffer_len);
    //SerialMonitorInterface.print(" : ");
    //SerialMonitorInterface.println((char*)ble_rx_buffer);
    ble_rx_buffer_len = 0;//clear afer reading
  
    //Serial.println(ble_rx_buffer_len);
    //Serial.println((char*)ble_rx_buffer);

    imu->IMURead();
    fusion.newIMUData(imu->getGyro(), imu->getAccel(), imu->getCompass(), imu->getTimestamp());
   

    RTVector3 accelData=imu->getAccel();
    RTVector3 gyroData=imu->getGyro();
    RTVector3 compassData=imu->getCompass();
    RTVector3 fusionData=fusion.getFusionPose();
    
    msga = "a " + String(accelData.x()) + " " + String(accelData.y()) + " " +String(accelData.z()) ;
    msgg = "g " + String(gyroData.x()) + " " + String(gyroData.y()) + " " +String(gyroData.z());
    msgc = "c " + String(compassData.x()) + " " + String(compassData.y()) + " " +String(compassData.z());
    msgf = "f " + String(fusionData.x()) + " " + String(fusionData.y()) + " " +String(fusionData.z());

   bsend(msga);
   bsend(msgg);
   bsend(msgc);
   bsend(msgf); 
     
    ble_rx_buffer_len=0;
  }
  
}




void bsend(String msg)
{   int nb = min(msg.length()+ 1,20);
    uint8_t sendBuffer[nb];
    msg.getBytes(sendBuffer, nb);
    int i =0;
    int ls = 20;
    while(i<nb)
    {
      int len = min(ls,nb-i);
      uart_tx((uint8_t*)sendBuffer+i, len);
      i+=ls;
    }
}
