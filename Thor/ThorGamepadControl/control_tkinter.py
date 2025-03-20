"""
    Name: control_tkinter.py
    Author:
    Created:
    Purpose: Main GUI for controlling Thor using a gamepad
"""
import tkinter as tk
from tkinter import ttk
from serial_port_finder import serial_ports
# import serial
from threading import Thread
import control_pygame

class ControlThorGamepad(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Control Thor Gamepad")
        self.geometry("400x200")

        self.selected_port = tk.StringVar()
        self.connection_state = tk.StringVar(value="Disconnected")
        # self.selected_port.trace("w", self.on_port_selected)
        self.controller_thread = None
        self.controller_running = False
        self.create_widgets()
        self.refresh_ports()
        self.mainloop()

    def create_widgets(self):
        # Label frame for serial communication
        self.labelframe = tk.LabelFrame(self, text="Serial Communication")
        self.labelframe.grid(pady=10, padx=10, sticky="nsew")

        # Frame for dropdown, refresh button, and state
        self.frame = tk.Frame(self.labelframe)
        self.frame.grid(pady=10, padx=10, sticky="nsew")

        # Dropdown list for serial ports
        self.port_dropdown = ttk.Combobox(self.frame, textvariable=self.selected_port)
        self.port_dropdown.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Refresh button to search for serial ports again
        self.refresh_button = tk.Button(self.frame, text="Refresh", command=self.refresh_ports)
        self.refresh_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # State label
        self.state_label = tk.Label(self.frame, text="State:")
        self.state_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        # Connection state label
        self.connection_state_label = tk.Label(self.frame, textvariable=self.connection_state)
        self.connection_state_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Start button to start the gamepad controller
        self.start_button = tk.Button(self.frame, text="Start", command=self.start_controller)
        self.start_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        # Stop button to stop the gamepad controller
        self.stop_button = tk.Button(self.frame, text="Stop", command=self.stop_controller)
        self.stop_button.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    def refresh_ports(self):
        # Get the list of available serial ports
        ports = serial_ports()
        print(ports)
        # Update the dropdown list with the available ports
        self.port_dropdown['values'] = ports
        if ports:
            # Set the first port as the default selection
            self.port_dropdown.current(0)
            # Automatically select the first available port
            self.selected_port.set(ports[0])

    # def on_port_selected(self, *args):
    #     # Get the selected port
    #     selected_port = self.selected_port.get()
    #     # Print the selected port (or perform any other action)
    #     print(f"Selected Port: {selected_port}")
        # Check the connection state
        # self.check_connection(selected_port)

    # def check_connection(self, port):
    #     try:
    #         # Try to open the serial port
    #         s = serial.Serial(port)
    #         s.close()
    #         self.connection_state.set("Connected")
    #     except (OSError, serial.SerialException):
    #         self.connection_state.set("Disconnected")

    def start_controller(self):
        if not self.controller_running:
            self.controller_thread = Thread(target=self.run_controller)
            self.controller_thread.start()
            self.controller_running = True

    def stop_controller(self):
        if self.controller_running:
            self.controller_running = False
            self.controller_thread.join()

    def run_controller(self):
        controller = control_pygame.GamepadController()
        while self.controller_running:
            controller.run()

if __name__ == "__main__":
    app = ControlThorGamepad()
    app.mainloop()
