"""
shutdown_pi.py
Owen Osmera
Purpose: Shows what subprocess needs to be done to shut off pi from controller
"""

from subprocess import call


def shutdown_pi():
    result = call(["sudo --non-interactive shutdown -h now"], shell=True)
    print(result)


def main():
    shutdown_pi()


if __name__ == "__main__":
    main()
