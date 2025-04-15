/*
@company: Hiwonder
@date:    2024-03-01
@version:  2.0
@description: wireless glove control program
*/

#include <SoftwareSerial.h> //software serial library
#include "LobotServoController.h" //robot control signal library
#include "MPU6050.h" //MPU6050 library
#include "Wire.h" //I2C library

// RX and TX pins of the Bluetooth
#define BTH_RX 11
#define BTH_TX 12

// create the minimum and maximum store values of the potentiometers
float min_list[5] = {0, 0, 0, 0, 0};
float max_list[5] = {255, 255, 255, 255, 255};
// data variables read by each finger
float sampling[5] = {0, 0, 0, 0, 0}; 
// finger-related servo variables
float data[5] = {1500, 1500, 1500, 1500, 1500};
uint16_t ServePwm[5] = {1500, 1500, 1500, 1500, 1500};
uint16_t ServoPwmSet[5] = {1500, 1500, 1500, 1500, 1500};
// potentiometer calibration flag
bool turn_on = true;

// initialize Bluetooth communication serial port
SoftwareSerial Bth(BTH_RX, BTH_TX);
// the control object of the robot
LobotServoController lsc(Bth);

// float parameter mapping function
float float_map(float in, float left_in, float right_in, float left_out, float right_out)
{
  return (in - left_in) * (right_out - left_out) / (right_in - left_in) + left_out;
}

// MPU6050 related variables
MPU6050 accelgyro;
int16_t ax, ay, az;
int16_t gx, gy, gz;
float ax0, ay0, az0;
float gx0, gy0, gz0;
float ax1, ay1, az1;
float gx1, gy1, gz1;

// accelerometer calibration variable
int ax_offset, ay_offset, az_offset, gx_offset, gy_offset, gz_offset;


void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  // initialize function button)
  pinMode(7, INPUT_PULLUP);
  // configure each finger's potentiometer
  pinMode(A0, INPUT);
  pinMode(A1, INPUT);
  pinMode(A2, INPUT);
  pinMode(A3, INPUT);
  pinMode(A6, INPUT);
  // configure LEDs
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);

  // configure Bluetooth
  Bth.begin(9600);
  Bth.print("AT+ROLE=M");  // set Bluetooth to master mode
  delay(100);
  Bth.print("AT+RESET");  // perform a soft reset of the Bluetooth module
  delay(250);

  // configure MPU6050
  Wire.begin();
  Wire.setClock(20000);
  accelgyro.initialize();
  accelgyro.setFullScaleGyroRange(3); // set the range of angular velocity
  accelgyro.setFullScaleAccelRange(1); // set the range of acceleration
  delay(200);
  accelgyro.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);  // obtain current data of each axis for calibration
  ax_offset = ax;  // calibration data for the X-axis acceleration
  ay_offset = ay;  // calibration data for the Y-axis acceleration
  az_offset = az - 8192;  // calibration data for the Z-axis acceleration
  gx_offset = gx; // calibration data for the X-axis angular velocity
  gy_offset = gy; // calibration data for the Y-axis angular velocity
  gz_offset = gz; // calibration data for the Z-axis angular velocity
}

// read potentiometer data of each finger
void finger() {
  static uint32_t timer_sampling;
  static uint32_t timer_init;
  static uint8_t init_step = 0;
  if (timer_sampling <= millis())
  {
    for (int i = 14; i <= 18; i++)
    {
      if (i < 18)
        sampling[i - 14] += analogRead(i); // read data of each finger
      else
        sampling[i - 14] += analogRead(A6);  // Read data of little finger. I2C uses A4 and A5 ports, therefore, it cannot read continuously starting from A0
      sampling[i - 14] = sampling[i - 14] / 2.0; // obtain the average value between the previous and current measurement values
      data[i - 14 ] = float_map( sampling[i - 14],min_list[i - 14], max_list[i - 14], 2500, 500); // Map the measured value to 500-2500, with 500 for making a fist and 2500 for opening the robotic hand
      data[i - 14] = data[i - 14] > 2500 ? 2500 : data[i - 14];  // limit the maximum value to 2500
      data[i - 14] = data[i - 14] < 500 ? 500 : data[ i - 14];   // limit the minimum value to 500
    }
    timer_sampling = millis() + 10;
  }

  if (turn_on && timer_init < millis())
  {
    switch (init_step)
    {
      case 0:
        digitalWrite(2, LOW);
        digitalWrite(3, LOW);
        digitalWrite(4, LOW);
        digitalWrite(5, LOW);
        digitalWrite(6, LOW);
        timer_init = millis() + 20;
        init_step++;
        break;
      case 1:
        digitalWrite(2, HIGH);
        digitalWrite(3, HIGH);
        digitalWrite(4, HIGH);
        digitalWrite(5, HIGH);
        digitalWrite(6, HIGH);
        timer_init = millis() + 200;
        init_step++;
        break;
      case 2:
        digitalWrite(2, LOW);
        digitalWrite(3, LOW);
        digitalWrite(4, LOW);
        digitalWrite(5, LOW);
        digitalWrite(6, LOW);
        timer_init = millis() + 50;
        init_step++;
        break;
      case 3:
        digitalWrite(2, HIGH);
        digitalWrite(3, HIGH);
        digitalWrite(4, HIGH);
        digitalWrite(5, HIGH);
        digitalWrite(6, HIGH);
        timer_init = millis() + 500;
        init_step++;
        Serial.print("max_list:");
        for (int i = 14; i <= 18; i++)
        {
          max_list[i - 14] = sampling[i - 14];
          Serial.print(max_list[i - 14]);
          Serial.print("-");
        }
        Serial.println();
        break;
      case 4:
        init_step++;
        break;
      case 5:
        if ((max_list[1] - sampling[1]) > 50)
        {
          init_step++;
          digitalWrite(2, LOW);
          digitalWrite(3, LOW);
          digitalWrite(4, LOW);
          digitalWrite(5, LOW);
          digitalWrite(6, LOW);
          timer_init = millis() + 2000;
        }
        break;
      case 6:
        digitalWrite(2, HIGH);
        digitalWrite(3, HIGH);
        digitalWrite(4, HIGH);
        digitalWrite(5, HIGH);
        digitalWrite(6, HIGH);
        timer_init = millis() + 200;
        init_step++;
        break;
      case 7:
        digitalWrite(2, LOW);
        digitalWrite(3, LOW);
        digitalWrite(4, LOW);
        digitalWrite(5, LOW);
        digitalWrite(6, LOW);
        timer_init = millis() + 50;
        init_step++;
        break;
      case 8:
        digitalWrite(2, HIGH);
        digitalWrite(3, HIGH);
        digitalWrite(4, HIGH);
        digitalWrite(5, HIGH);
        digitalWrite(6, HIGH);
        timer_init = millis() + 500;
        init_step++;
        Serial.print("min_list:");
        for (int i = 14; i <= 18; i++)
        {
          min_list[i - 14] = sampling[i - 14];
          Serial.print(min_list[i - 14]);
          Serial.print("-");
        }
        Serial.println();
        lsc.runActionGroup(0, 1);
        turn_on = false;
        break;

      default:
        break;
    }
  }
}


float radianX;
float radianY;
float radianZ;
float radianX_last; // the final obtained X-axis inclination angle
float radianY_last; // the final obtained Y-axis inclination angle


// update data of inclination sensor
void update_mpu6050()
{
  static uint32_t timer_u;
  if (timer_u < millis())
  {
    // put your main code here, to run repeatedly:
    timer_u = millis() + 20;
    accelgyro.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

    ax0 = ((float)(ax)) * 0.3 + ax0 * 0.7;  // filter the read value
    ay0 = ((float)(ay)) * 0.3 + ay0 * 0.7;
    az0 = ((float)(az)) * 0.3 + az0 * 0.7;
    ax1 = (ax0 - ax_offset) /  8192.0;  // calibrate and convert to the multiples of the gravity acceleration
    ay1 = (ay0 - ay_offset) /  8192.0;
    az1 = (az0 - az_offset) /  8192.0;

    gx0 = ((float)(gx)) * 0.3 + gx0 * 0.7;  // filter the read value of angular velocity
    gy0 = ((float)(gy)) * 0.3 + gy0 * 0.7;
    gz0 = ((float)(gz)) * 0.3 + gz0 * 0.7;
    gx1 = (gx0 - gx_offset);  // calibrate angular velocity
    gy1 = (gy0 - gy_offset);
    gz1 = (gz0 - gz_offset);


    // complementary calculation for x-axis inclination angle
    radianX = atan2(ay1, az1);
    radianX = radianX * 180.0 / 3.1415926;
    float radian_temp = (float)(gx1) / 16.4 * 0.02;
    radianX_last = 0.8 * (radianX_last + radian_temp) + (-radianX) * 0.2;

    // complementary calculation for y-axis inclination angle
    radianY = atan2(ax1, az1);
    radianY = radianY * 180.0 / 3.1415926;
    radian_temp = (float)(gy1) / 16.4 * 0.01;
    radianY_last = 0.8 * (radianY_last + radian_temp) + (-radianY) * 0.2;
  }
}

// print data
void print_data()
{
  /*
  static uint32_t timer_p;
  if ( timer_p < millis())
  {
    Serial.print("ax:"); Serial.print(ax1);
    Serial.print(", ay:"); Serial.print(ay1);
    Serial.print(", az:"); Serial.print(az1);
    Serial.print(", gx:"); Serial.print(gx1);
    Serial.print(", gy:"); Serial.print(gy1);
    Serial.print(", gz:"); Serial.print(gz1);
    Serial.print(", GX:"); Serial.print(radianX_last);
    Serial.print(", GY:"); Serial.println(radianY_last);
    timer_p = millis() + 300;
  }
*/
  static uint32_t timer_printlog;
  if (timer_printlog <= millis())  
  {
    for (int i = 14; i <= 18; i++)
    {
      Serial.print(data[i - 14]);
      Serial.print("  ");
      // Serial.print(float_map(min_list[i-14], max_list[i-14], 500,2500,sampling[i-14]));
      Serial.print(" ");
      // Serial.print();
    }
    timer_printlog = millis() + 1000;
    Serial.println();
  }

}

#define STOP       0
#define GO_FORWARD 1
#define GO_BACK    2
#define TURN_LEFT  3
#define TURN_RIGHT 4

//"run()" function controls bionic robots such as hexapod and humanoid robots
void run()
{
  static uint32_t timer;
  static int act;
  static int last_act = 0;
  static uint8_t count = 0;
  if (timer > millis())
    return;
  timer = millis() + 80;
  if (radianY_last < -35 && radianY_last > -90 && data[3] < 1200  && data[2] > 2000) // If the palm's inclination angle to the right is within the range of 35 to 90 degrees, indicating the middle finger is extended and the ring finger is bent
  {
    act = TURN_RIGHT; //右转(turn right)
  }
  if (radianY_last < 90 && radianY_last > 35 && data[3] < 1200 && data[2] > 2000)    // If the palm's inclination angle to the left is within the range of 35 to 90 degrees, indicating the middle finger is extended and the ring finger is bent
  {
    act = TURN_LEFT; //左转(turn left)
  }
  if ((radianY_last < 15 && radianY_last > -15) && data[2] < 600)  // If making a fist with the palm facing down, and the index finger is extended, the robot stops
  {
    act = STOP;
  }
  if ((radianY_last < 15 &&  radianY_last > -15 ) && data[2] > 2100 && data[3] > 2100)  // If the hand is stretched with the palm facing down, the robot stops
  {
    act = GO_FORWARD;
  }
  if ((radianY_last < -130 ||  radianY_last > 130 ) && data[2] < 1200 && data[4] > 2000)  // If the hand gesture of Spider-Man is made with the palm facing upward, the robot moves backward
  {
    act = GO_BACK;
  }
  if ((radianY_last < -130 ||  radianY_last > 130 ) && data[2] > 2000) // If the hand is stretched with the palm facing upward, the robot stops
  {
    act = STOP;
  }
  if (act != last_act)
  {
    last_act = act;
    if (act == STOP)
    {
      if (count != 1) {
        count = 1;
        lsc.stopActionGroup();  // stop current action group
        lsc.runActionGroup(0, 1);  // run specified action group
        return;
      }
    }
    if (act == GO_FORWARD)
    {
      if (count != 2) {
        count = 2;
        lsc.stopActionGroup();
        lsc.runActionGroup(1, 0);
        return;
      }
    }
    if (act == GO_BACK)
    {
      if (count != 3) {
        count = 3;
        lsc.stopActionGroup();
        lsc.runActionGroup(2, 0);
        return;
      }
    }
    if (act == TURN_LEFT)
    {
      if (count != 4) {
        count = 4;
        lsc.stopActionGroup();
        lsc.runActionGroup(3, 0);
        return;
      }
    }
    if (act == TURN_RIGHT)
    {
      if (count != 5) {
        count = 5;
        lsc.stopActionGroup();
        lsc.runActionGroup(4, 0);
        return;
      }
    }
  }
}

// "run1" function controls the robotic hand
void run1(int mode)
{
  // assign values to the servo of each finger
  for (int i = 0; i < 5; i++)
  {
    ServoPwmSet[i] = data[i]; 
    ServoPwmSet[i] = float_map(ServoPwmSet[i], 500, 2500, 1100, 1950);
  }
  
  int pos = 0;
  if(mode == 4) // If it is mode 4, control left robotic hand
    pos = 2750 - ServoPwmSet[4];
  else // If it is mode 1, control right robotic hand
    pos = ServoPwmSet[4];
  // If there is a rotation at the Y-axis, add the position of pan-tilt servo
  if (radianY_last < 90 && radianY_last > -90)
  {
    if ( abs(radianY_last) > 1)  {
      uint16_t se = 1500 + radianY_last*10;
      lsc.moveServos(6, 30, 1, 3050 - ServoPwmSet[0], 2, ServoPwmSet[1], 3, ServoPwmSet[2], 4, ServoPwmSet[3], 5, pos , 6 , se);// control each finger

      return;
    }
  }
  // If no choice for Y-axis, only send the servo position of five fingers
  lsc.moveServos(5, 30, 1, 3050 - ServoPwmSet[0], 2, ServoPwmSet[1], 3, ServoPwmSet[2], 4, ServoPwmSet[3], 5, pos);// control each finger
}

// send data to the smart car
void car_control(byte motor1, byte motor2)
{
  byte buf[6];
  buf[0] = buf[1] = 0x55;
  buf[2] = 0x04;
  buf[3] = 0x32;
  buf[4] = (byte)motor1;
  buf[5] = (byte)motor2;
  Bth.write(buf, 6);
}

// "run2" function controls the smart car
void run2()
{
  static uint32_t timer;

  if (timer > millis())
    return;
  timer = millis() + 100;
  if (data[2] < 600 && (radianY_last < -30 && radianY_last > -90))
  {
    car_control(100, -100);
  }
  else if (data[2] < 600  && (radianY_last > 30 && radianY_last < 90))
  {
   car_control(-100, 100); 
  }
  else if (data[2] < 600 && abs(radianY_last) < 30 )
  {
    car_control(100, 100);
  }
  else if (data[2] < 600 && (radianY_last < -130 ||  radianY_last > 130 ))
  {
   car_control(-100, -100); 
  }
  else
    car_control(0, 0); 
}

//control robotic arm (PWM servo)
void run3(int mode)
{
  static uint32_t timer;
  static uint32_t median;

  if (timer > millis())
    return;
  timer = millis() + 50;

  if(mode == 5)
    median = 500;
  else
    median = 1500;

  if (data[1] < 1200 && data[2] < 1000 && data[3] < 1000)  // make a fist and tilt to control servo 6
  {
      if (radianY_last < 90 && radianY_last > -90)
      {
          lsc.moveServo(6, median + radianY_last*10, 50);
          delay(50);
      }
  } 
  else if ( data[0] > 1400 && data[1] > 1400 && data[2] > 1400 && data[3] > 1400) // stretch all five fingers and tilt to control servo5
  {
      if (radianY_last < 90 && radianY_last > -90)
      {
          lsc.moveServo(5, median + radianY_last*10, 50);
          delay(50);
      }
  }
  else if (data[1] > 1400 && data[2] < 1000 && data[3] < 1000 ) // extend the index finger to control servo 1
  {
      if (radianY_last < 90 && radianY_last > -90)
      {
          lsc.moveServo(1, median + radianY_last*10, 50);
          delay(50);
      }
  }
  else if (data[1] > 1400 && data[2] > 1400 && data[3] < 1000 ) // extend the index and middle fingers to control servo 2
  {
      if (radianY_last < 90 && radianY_last > -90)
      {
          lsc.moveServo(2, median + radianY_last*10, 50);
          delay(50);
      }
  }
  else if (data[1] < 1400 && data[2] > 1200 && data[3] > 1000 ) // extend the middle, ring, and little fingers to control servo 3 
  {
      if (radianY_last < 90 && radianY_last > -90)
      {
          lsc.moveServo(3, median + radianY_last*10, 50);
          delay(50);
      }
  }
  else if (data[0] < 1400 && data[1] > 1400 && data[2] > 1400 && data[3] > 1400) // extend four fingers excepting the thumb to control servo 4 
  {
      if (radianY_last < 90 && radianY_last > -90)
      {
          lsc.moveServo(4, median + radianY_last*10, 50);
          delay(50);
      }
  }
}

int mode = 0;
bool key_state = false;

void loop() {
  finger();  // update data of finger potentiometers 
  update_mpu6050();  // update data of inclination sensor 

  if (turn_on == false) // After the wireless glove is started, the calibration for potentiometers is completed 
  {
    // if K3 button is pressed 
    if(key_state == true && digitalRead(7) == true)
    {
      delay(30);
      if(digitalRead(7) == true)
        key_state = false;
    }
    if (digitalRead(7) == false && key_state == false)
    {
      delay(30);
      // If K3 is pressed, switch the control mode and display corresponding numbers of LEDs 
      if (digitalRead(7) == false)
      {
        key_state = true;
        if (mode == 6)
        {
          mode = 0;
        }
        else
          mode++;
        if (mode == 0)
        {
          digitalWrite(2, HIGH);
          digitalWrite(3, HIGH);
          digitalWrite(4, HIGH);
          digitalWrite(5, HIGH);
          digitalWrite(6, HIGH);
        }
        if (mode == 1)
        {
          digitalWrite(2, LOW);
          digitalWrite(3, HIGH);
          digitalWrite(4, HIGH);
          digitalWrite(5, HIGH);
          digitalWrite(6, HIGH);
        }
        if (mode == 2)
        {
          digitalWrite(2, LOW);
          digitalWrite(3, LOW);
          digitalWrite(4, HIGH);
          digitalWrite(5, HIGH);
          digitalWrite(6, HIGH);
        }
        if (mode == 3)
        {
          digitalWrite(2, LOW);
          digitalWrite(3, LOW);
          digitalWrite(4, LOW);
          digitalWrite(5, HIGH);
          digitalWrite(6, HIGH);
        }

        if (mode == 4)
        {
          digitalWrite(2, LOW);
          digitalWrite(3, LOW);
          digitalWrite(4, LOW);
          digitalWrite(5, LOW);
          digitalWrite(6, HIGH);
        }

        if (mode == 5)
        {
          digitalWrite(2, LOW);
          digitalWrite(3, LOW);
          digitalWrite(4, LOW);
          digitalWrite(5, LOW);
          digitalWrite(6, LOW);
        }
      }
    }

    if (mode == 0)
      run();  // bionic robots such as hexapod and humanoid robots 
    if (mode == 1 || mode == 4)  { // Mode 1 is for the left robotic hand, and mode 2 is for the right robotic hand 
      run1(mode); // robotic hand 
    }
    if (mode == 2)
      run2(); // smart car
    if (mode == 3 || mode == 5)
      run3(mode);  // robotic arm; Mode 3 drives PWM servo and mode 5 drives bus servo 
  }
  //print_data();  // printing sensor data facilitates debugging 
}
