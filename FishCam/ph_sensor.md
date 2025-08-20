pH Sensor - Quick Setup
=======================

This project reads pH from a DFRobot Gravity pH probe V2 connected to a Grove
Base Hat (I2C ADC) on a Raspberry Pi.

Using the pH sensor (quick steps)
-------------------------------

1. Enable I2C on the Raspberry Pi

   - Open a terminal on the Pi and run:

     sudo raspi-config

   - Navigate to: Interface Options -> I2C -> Enable

   - Reboot the Pi if prompted.

   You can verify the I2C device exists with:

     ls /dev/i2c-*

   and scan the bus for devices with:

     sudo apt-get install -y i2c-tools

     i2cdetect -y 1

2. Install Python dependency

   - Install smbus2 on the Pi:

     pip3 install smbus2

3. Run the quick test program

   - From the project directory on the Pi run:

     python ph_sensor_ts.py

Calibrating the pH probe (simple two-point calibration)
------------------------------------------------------

You'll need two calibration solutions: pH 4.00 (acid) and pH 7.00 (neutral).

1. Rinse the probe in distilled water and gently blot dry.

2. Place the probe in the pH 7.00 solution and let it stabilize (30-60s).

  - Note the reported pH value from the program (or use the raw voltage).

3. Place the probe in the pH 4.00 solution and let it stabilize.

  - Note the reported pH value.

From the two readings you can compute a linear calibration:

   measured_mv = measured_voltage - center_voltage (in mV)
   ph = slope * measured_mv + offset

Solve for slope and offset using your two calibration points (pH7 and pH4).
A common simple approach is to set offset so measured value at pH7 == 7.0,
then compute slope using the pH4 point.

Notes and troubleshooting
-------------------------

- If you see warnings about I2C or Grove Base Hat during startup, they are
  often benign; verify the device appears in `i2cdetect` and that cables are
  seated correctly.

- Use `i2cdetect -y 1` to confirm you can see the Grove Base Hat on the bus.

- If readings are extremely noisy, increase the averaging sample count and
  ensure probe is clean and at stable temperature.

## Notes and troubleshooting

- If you see warnings about I2C or Grove Base Hat during startup, they are
  often benign; verify the device appears in `i2cdetect` and that cables are
  seated correctly.

- Use `i2cdetect -y 1` to confirm you can see the Grove Base Hat on the bus.

- If readings are extremely noisy, increase the averaging sample count and
  ensure probe is clean and at stable temperature.

## Calibration helper script

This repository includes a small helper script `ph_calibrate.py` that computes
the linear slope and offset from two measured points. It is useful when you
have two known calibration solutions (for example pH 7.00 and pH 4.00).

### Examples (run on the Raspberry Pi)

- If you already converted to millivolts (centered around neutral):

```bash
python ph_calibrate.py --mv -10.5 -100.0 --ph 7.0 4.0
```

- If you measured raw ADC counts (0..4095) from the Grove ADC:

```bash
python ph_calibrate.py --raw 2048 1800 --ph 7.0 4.0 --center_voltage 0.306
```

The script prints `slope` and `offset`. Copy those values into
`ph_sensor_ts.py` as `PH_SLOPE` and `PH_OFFSET` (or keep them in a
configuration file) so the live readings use your calibrated conversion.

### Example output (illustrative)

```text
Calibration result:
  point A: mv=-10.500 mV -> pH=7.0
  point B: mv=-100.000 mV -> pH=4.0

  slope  = 0.031915  (pH per mV)
  offset = 7.335555
```

## Example calibration file

You can save calibration results to `ph_calibration.json` and the module will load it on import.
Create a file named `ph_calibration.json` in the project directory with content similar to this example:

```json
{
  "PH_SLOPE": -0.0169,
  "PH_OFFSET": 7.0,
  "CENTER_VOLTAGE": 0.306,
  "V_REF": 3.3,
  "ADC_MAX": 4095.0
}
```

Then run the sensor script; to print the loaded calibration use:

```bash
python ph_sensor_ts.py --show-calib
```

