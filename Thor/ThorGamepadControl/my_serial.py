"""
    Name: my_serial.py
    Author:
    Created:
    Purpose: Communicate with the Arduino via serial port
    This library uses the pyserial library to communicate with the Arduino
    https://pyserial.readthedocs.io/en/latest/pyserial.html
"""

# Import the Serial class from the pyserial library
# pip install pyserial
from serial import Serial
# Import the Thread class from the threading library
from threading import Thread

s0 = Serial()  # Create an instance of the Serial class
s0.port = "COM3"  # Set the serial port to COM3
s0.baudrate = 115200  # Set the baud rate to 115200
s0.timeout = 1  # Set the read timeout to 1 second
s0.close()  # Close the serial port if it is open
s0.open()  # Open the serial port


# ------------------------------ SERIAL READ ------------------------------- #
def serial_read():
    # Infinite loop to keep the serial interface open
    while True:
        if not s0.is_open:  # Check if the serial port is closed
            break  # Exit the loop if the serial port is closed
        try:
            # Check if there is data waiting to be read from the serial port
            s0.in_waiting
        except Exception as e:  # Handle exceptions
            # Print a message indicating the serial connection is lost
            print("SERIAL-DISCONNECTED")
            # Print a message indicating the serial connection is lost
            print(f"Lost Serial connection! {e}")

        try:
            # Read a line of data from the serial port
            s0.readline()
        except Exception as e:  # Handle exceptions
            # Print a message indicating an error occurred
            print(f"Something failed: {e}")


# ------------------------------ SERIAL WRITE ------------------------------ #
def serial_write(cmd):
    # Append a newline character to the command
    cmd = cmd + "\n"
    # Write the command to the serial port encoded as UTF-8
    s0.write(cmd.encode("UTF-8"))


# Create a new thread to run the serial_read function
read_thread = Thread(target=serial_read)
# Set the thread as a daemon thread, it will be closed when not used
read_thread.daemon = True

# Check if the script is being run directly
if __name__ == "__main__":
    # Print a message indicating to run control.py instead
    print("Run control.py instead")
