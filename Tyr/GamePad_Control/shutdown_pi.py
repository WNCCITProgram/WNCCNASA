"""
shutdown_pi.py
Owen Osmera
Purpose: A module to shut down the Raspberry Pi from the controller using subprocess    
This script uses the subprocess module to call the shutdown command
with the appropriate arguments. The command is executed in a shell
environment, and the result is printed to the console.
"""

from subprocess import call


def shutdown_pi():
    # shutdown the pi
    result = call(["sudo --non-interactive shutdown -h now"], shell=True)
    # Will print 0 if successful, 1 if not
    # 0 = success, 1 = failure
    print(result)


def main():
    shutdown_pi()


if __name__ == "__main__":
    main()
