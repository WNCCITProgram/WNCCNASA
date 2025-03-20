#!/usr/bin/env python3
#
# https://www.dexterindustries.com/GoPiGo/
# https://github.com/DexterInd/GoPiGo3
#
# Copyright (c) 2017 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
#
# This code is an example for reading GoPiGo3 information
#
# Results: Print information about the attached GoPiGo3.

import gopigo3  # import the GoPiGo3 drivers

try:
    # Create an instance of the GoPiGo3 class. GPG will be the GoPiGo3 object.
    GPG = gopigo3.GoPiGo3()

    # Each of the following GPG.get functions return a list of 2 values
    # read and display the serial number
    print(f"Manufacturer    : {GPG.get_manufacturer()}")
    # read and display the serial number
    print(f"Board           : {GPG.get_board()}")
    # read and display the serial number
    print(f"Serial Number   : {GPG.get_id()}")
    # read and display the hardware version
    print(f"Hardware version: {GPG.get_version_hardware()}")
    # read and display the firmware version
    print(f"Firmware version: {GPG.get_version_firmware()}")
    # read and display the current battery voltage
    print(f"Battery voltage : {GPG.get_voltage_battery()}")
    # read and display the current 5v regulator voltage
    print(f"5v voltage      : {GPG.get_voltage_5v()}")

except IOError as error:
    print(error)

except gopigo3.FirmwareVersionError as error:
    print(error)
