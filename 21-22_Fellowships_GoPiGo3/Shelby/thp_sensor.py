# thp_sensor.py

from time import sleep
from di_sensors.easy_temp_hum_press import EasyThpSensor

print("Temperature Humidity Pressure Sensor on an I2C port.")

my_thp = EasyThpSensor()

while True:
    # read the temperature
    # temp=my_thp.safe_celsius()
    temp = my_thp.safe_fahrenheit()

    # read the relative humidity
    hum = my_thp.safe_pressure()

    #Read the pressure in pascals
    press=my_thp.safe_pressure()

    # convert pascals to inHg, compensate for 4000' altitude
    press = (press/3386.33857)+4.08

    # print the values to the console
    print("Temperature: {:5.1f}F Humidity: {5.1f}% Pressure: {:5.2f}".format(
        temp, hum, press))
    #Pause 5sec beteen readings
    sleep(5)
