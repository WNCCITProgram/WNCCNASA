"""
shutdown_pi.py
Purpose: A module to soft shut down the Raspberry Pi from the PS4 controller
using subprocess to call the shutdown command with sudo.
The command is executed in a shell environment.
The result is printed to the console.
"""

from subprocess import call


def shutdown_rpi():
    """Call the shutdown command with sudo to shut down the Raspberry Pi.
    '--non-interactive' is used to prevent the need for a password prompt
    '-h' is used to halt the system
    'now' is used to shut down immediately
    'shell=True' is used to execute the command in a shell environment
    """
    result = call(["sudo --non-interactive shutdown -h now"], shell=True)

    # Will print 0 if successful, 1 if not
    # 0 = success, 1 = failure
    print(result)


def main():
    shutdown_rpi()


if __name__ == "__main__":
    main()
