/************************************************
      幻尔科技
      产品名称：开源体感手套
      程序功能：蓝牙波特率自动修复
      更新日期：2022-07-01
************************************************/
#include <SoftwareSerial.h>
#include "LobotServoController.h"

#include "I2Cdev.h"
#include "MPU6050.h"
#include "Wire.h"

#define BTH_RX 11
#define BTH_TX 12

SoftwareSerial mySerial(BTH_RX, BTH_TX);

void setup() {
  long int buf[11]={115200,74880,57600,38400,19200,9600,4800,2400,1200,300};  //创建蓝牙波特率数组
  Serial.begin(9600);                                                        //设置串口波特率
  Serial.println("open");                                                    //测试开始
  //蓝牙配置
  for(int i;i<=10;i++)                                                        //buf数组中有10个波特率所以循环10次
  {
      char character;
      mySerial.begin(buf[i]);                                                 //设置波特率
      mySerial.write("AT");                                                   //向蓝牙模块发送测试指令
      delay(500);                                                             //等待0.5s
      while(mySerial.available())
         character = mySerial.read();
      if(character == 'K')
        { 
          mySerial.write("AT+BAUD=9600,N"); 
          delay(100);
          while(mySerial.available())
            Serial.write(mySerial.read());                                   //输出设置结果
          return;
        }  
      Serial.println(buf[i]);                                                //输出当前的蓝牙波特率
    }
}

void loop()
{
  }
