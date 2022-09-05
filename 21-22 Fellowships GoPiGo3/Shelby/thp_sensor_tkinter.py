# thp_sensor.py with tkinter GUI addit

from tkinter import *
import tkinter as tk
from time import sleep
# EasyTHPSensor rounds data to 0 decimal for temp and humidty
from di_sensors.easy_temp_hum_press import EasyTHPSensor
from easygopigo3 import EasyGoPiGo3  # Import GoPiGo3 library


class THPSensor:

    def __init__(self):
        # Create an instance of the GoPiGo3 class
        self.gpg = EasyGoPiGo3()

        print("Example program for reading Dexter Industries")
        print("Temperature Humidity Pressure Sensor on an I2C port.")

        # Initialize an EasyTHPSensor object
        self.my_thp = EasyTHPSensor()
        print("Temperature Humidity Pressure Sensor on an I2C port.")
        self.window = Tk()

        self.create_widgets()
        
        # while True:
        self.temperature()
        self.humidity()
        self.pressure()

        # print the values to the console
        #   print("Temperature: {:5.1f}F Humidity: {5.1f}% Pressure: {:5.2f}".format(
        #  temp, hum, press))

        mainloop()
    def temperature(self):
        # read the temperature
        # temp=my_thp.safe_celsius()
        self.temp = self.my_thp.safe_fahrenheit()
        #self.temperature = self.my_thp.safe_fahrenheit()

        # Pause 5sec beteen readings
        print(f"Temperature {self.temp}")


    def humidity(self):

        # read the relative humidity
        self.hum = self.my_thp.safe_pressure()
        # Pause 5sec beteen readings
        print(f"Humidity {self.hum}")

    def pressure(self):
        # Read the pressure in pascals
        self.press = self.my_thp.safe_pressure()
        # convert pascals to inHg, compensate for 4000' altitude
        self.press = (self.press/3386.33857)+4.08
        print(f"Pressure {self.press}")
        # Pause 5sec beteen readings

    def create_widgets(self):
        """
        create and grid widgets
        """

        # Create a main label frame to hold widgets
        self.main_frame = LabelFrame(
            self.window,
            bg='#c6ff9e',
            text="Local temperature",
            relief=GROOVE)

        self.lbl_temp = Label(
            self.main_frame,
            text="Temperature",
            bg="light green",
            width=20)

        self.lbl_hum = Label(
            self.main_frame,
            text="Humidity",
            bg="light green",
            width=20)

        self.lbl_press = Label(
            self.main_frame,
            text="Pressure",
            bg="light green",
            width=20)

        # label to display temp
        self.disp_lbl_temp = Label(
            self.main_frame,
            text=f"{self.temp}",
            bg="light green",
            width=20)
        # label to display press
        self.disp_lbl_press = Label(
            self.main_frame,
            text=f"{self.press}",
            bg="light green",
            width=20)
        # label to display hum
        self.disp_lbl_hum = Label(
            self.main_frame,
            text=f"{self.hum}",
            bg="light green",
            width=20)
        # Use grid layout manager to place widgets in the frame
        self.main_frame.grid(row=0, column=0, padx=10, pady=10)
        self.lbl_temp.grid(row=0, column=0, padx=10, pady=10)
        self.disp_lbl_temp.grid(row=0, column=1, padx=10, pady=10)
        self.lbl_hum.grid(row=1, column=0, padx=10, pady=10)
        self.disp_lbl_hum.grid(row=1, column=1, padx=10, pady=10)
        self.lbl_press.grid(row=2, column=0, padx=10, pady=10)
        self.disp_lbl_press.grid(row=2, column=1, padx=10, pady=10)

        # Set padding between frame and window
        self.main_frame.grid_configure(padx=2, pady=2)
        # set padding for all widgets in the frame
        for widget in self.main_frame.winfo_children():
            widget.grid_configure(padx=2, pady=2)


thpsensor = THPSensor()
