"""
    Name: serial_port_finder.py
    Author:
    Created:
    Purpose: Find the serial port for an Arduino    
"""

# sys module to access system-specific parameters and functions
import sys
# glob module to find all the pathnames matching a specified pattern
import glob
# pyserial module to handle serial communication
# pip install pyserial
import serial


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):  # Check if the platform is Windows
        # Generate a list of COM ports
        ports = ['COM%s' % (i + 1) for i in range(256)]
    # Check if the platform is Linux or Cygwin
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # Find all the serial ports on Linux/Cygwin
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):  # Check if the platform is macOS
        ports = glob.glob('/dev/tty.*')  # Find all the serial ports on macOS
    else:
        # Raise an error if the platform is unsupported
        raise EnvironmentError('Unsupported platform')

    # Initialize an empty list to store the available serial ports
    result = []

    # Iterate over the list of ports
    for port in ports:
        try:
            # Try to open the serial port
            s = serial.Serial(port)
            # Close the serial port if it is successfully opened
            s.close()
            # Add the port to the result list if it was successfully opened
            result.append(port)

        # Handle exceptions
        except (OSError, serial.SerialException):
            # Ignore the exception and continue with the next port
            pass

    # Return the list of available serial ports
    return result


def main():
    """ Main function to test the serial_ports function """
    # Call the serial_ports function to get the available ports
    result = serial_ports()
    # Print the available serial ports
    print(f"Serial Ports: {result}")


# Check if the script is run as the main program
# Otherwise, it is being imported as a module
if __name__ == '__main__':
    main()
