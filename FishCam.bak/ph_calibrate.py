#!/usr/bin/env python3
"""
ph_calibrate.py

Small calibration helper for the DFRobot gravity pH probe + Grove ADC.

Usage examples (millivolts already centered around probe neutral point):
  python ph_calibrate.py --mv1 -10.5 --ph1 7.0 --mv2 -100.0 --ph2 4.0

Or provide raw ADC counts and let the script convert them (requires V_REF/ADC_MAX):
  python ph_calibrate.py --raw1 2048 --raw2 1800 --ph1 7.0 --ph2 4.0 --center_voltage 0.306

The script prints slope and offset for the linear equation used in this project:
    ph = slope * (measured_mv) + offset

Notes for students:
 - measured_mv is the sensor voltage relative to the neutral center point, in millivolts.
 - If you have raw ADC readings (0..4095) from the Grove Base Hat, use --raw1/--raw2
   and provide the center_voltage (defaults to 0.306 V), V_REF (default 3.3 V) and ADC_MAX (default 4095).
"""

import sys
import json

# Defaults used when converting raw ADC counts to millivolts
DEFAULT_CENTER_VOLTAGE = 0.306
V_REF = 3.3
ADC_MAX = 4095.0


def compute_slope_offset(mv1: float, ph1: float, mv2: float, ph2: float):
    """Compute linear slope and offset from two points (mv, ph).

    Returns (slope, offset) where ph = slope * mv + offset
    """
    if mv2 == mv1:
        raise ValueError("The two voltages (mv1 and mv2) must be different.")

    slope = (ph2 - ph1) / (mv2 - mv1)
    offset = ph1 - slope * mv1
    return slope, offset


def raw_to_mv(raw: float, center_voltage: float, v_ref: float = 3.3, adc_max: float = 4095.0):
    """Convert raw ADC count to millivolts relative to the center voltage.

    raw: ADC reading (0..adc_max)
    center_voltage: neutral probe voltage in volts (e.g. 0.306)
    returns: measured_mv (float)
    """
    voltage_v = (raw / adc_max) * v_ref
    measured_mv = (voltage_v - center_voltage) * 1000.0
    return measured_mv


"""
Interactive menu-based calibration helper.

This replaces the previous argparse-based CLI with a simple text menu so
students can run the script and follow prompts to compute slope/offset and
optionally save a `ph_calibration.json` file.
"""


def main():
    # Simple text-menu loop
    while True:
        print("\nCalibration helper menu:")
        print("  1) Enter two measured millivolt values (centered around neutral)")
        print("  2) Enter two raw ADC counts (0..ADC_MAX) and convert to mV")
        print("  3) Quit")
        choice = input("Choose an option (1-3): ").strip()

        if choice == '3' or choice.lower() in ('q', 'quit', 'exit'):
            print("Exiting")
            return

        try:
            if choice == '1':
                mv1 = float(input("Enter first measured mV (e.g. -10.5): ").strip())
                ph1 = float(input("Enter pH for first measurement (e.g. 7.0): ").strip())
                mv2 = float(input("Enter second measured mV (e.g. -100.0): ").strip())
                ph2 = float(input("Enter pH for second measurement (e.g. 4.0): ").strip())

                slope, offset = compute_slope_offset(mv1, ph1, mv2, ph2)

                center_voltage = float(input(f"Center voltage used (V) [default 0.306]: ").strip() or DEFAULT_CENTER_VOLTAGE)
                vref = float(input(f"ADC V_REF [default {V_REF}]: ").strip() or V_REF)
                adc_max = float(input(f"ADC max (ADC_MAX) [default {ADC_MAX}]: ").strip() or ADC_MAX)

            elif choice == '2':
                raw1 = float(input("Enter first raw ADC count (0..ADC_MAX, e.g. 2048): ").strip())
                raw2 = float(input("Enter second raw ADC count (0..ADC_MAX, e.g. 1800): ").strip())
                ph1 = float(input("Enter pH for first measurement (e.g. 7.0): ").strip())
                ph2 = float(input("Enter pH for second measurement (e.g. 4.0): ").strip())

                center_voltage = float(input(f"Center voltage used (V) [default 0.306]: ").strip() or DEFAULT_CENTER_VOLTAGE)
                vref = float(input(f"ADC V_REF [default {V_REF}]: ").strip() or V_REF)
                adc_max = float(input(f"ADC max (ADC_MAX) [default {ADC_MAX}]: ").strip() or ADC_MAX)

                mv1 = raw_to_mv(raw1, center_voltage, vref, adc_max)
                mv2 = raw_to_mv(raw2, center_voltage, vref, adc_max)

                slope, offset = compute_slope_offset(mv1, ph1, mv2, ph2)

            else:
                print("Invalid choice; please enter 1, 2 or 3")
                continue

        except ValueError as e:
            print(f"Input error: {e}; please try again")
            continue

        # Display result
        print("\nCalibration result:")
        print(f"  point A: mv={mv1:.3f} mV -> pH={ph1}")
        print(f"  point B: mv={mv2:.3f} mV -> pH={ph2}")
        print()
        print(f"  slope  = {slope:.6f}  (pH per mV)")
        print(f"  offset = {offset:.6f}")
        print()
        print("Linear equation to use in code: pH = slope * measured_mv + offset")

        # Offer to save
        save_ans = input("Save calibration to ph_calibration.json? [y/N]: ").strip().lower()
        if save_ans in ('y', 'yes'):
            out_path = input("Output path (default: ph_calibration.json): ").strip() or 'ph_calibration.json'
            calib = {
                "PH_SLOPE": float(slope),
                "PH_OFFSET": float(offset),
                "CENTER_VOLTAGE": float(center_voltage),
                "V_REF": float(vref),
                "ADC_MAX": float(adc_max),
            }
            try:
                with open(out_path, 'w', encoding='utf-8') as f:
                    json.dump(calib, f, indent=2)
                print(f"Saved calibration to {out_path}")
            except OSError as e:
                print(f"Failed to write calibration file {out_path}: {e}")


if __name__ == '__main__':
    main()
