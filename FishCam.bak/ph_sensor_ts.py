#!/usr/bin/env python3
"""Student-friendly pH sensor module.

This module reads pH from a DFRobot Gravity pH probe connected through
a Grove Base Hat (I2C ADC) on a Raspberry Pi. It contains two layers:
 - PHSensorReader: low-level I2C reader that communicates with the ADC
 - PHSensor: high-level wrapper that exposes convenient read functions

The code converts raw 12-bit ADC readings into voltages and then into pH
using a simple linear calibration (slope and offset). Students can read
the code to learn about I2C, ADC decoding, signal conversion, and basic
defensive programming (error handling, averaging, trimming outliers).

Dependencies (on Raspberry Pi):
pip install smbus2
"""

import time
import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

import statistics
from typing import List, Optional
import json

# Configuration constants
SENSOR_CHANNEL = 0  # Which input pin on Grove Base Hat (A0, A1, A2, etc.)
SAMPLING_INTERVAL = (
    0.02  # How often to read sensor (0.02 seconds = 20 milliseconds)
)
ARRAY_LENGTH = 40  # How many readings to average together for stability

# Calibration and ADC constants (defaults)
# These defaults are used if no configuration file is present.
DEFAULT_PH_SLOPE = -0.0169  # pH per mV (fallback default)
DEFAULT_PH_OFFSET = 7.0  # pH offset at 0 mV (fallback default)
DEFAULT_CENTER_VOLTAGE = (
    0.306  # V, empirical neutral point used in this project
)
ADC_MAX = 4095.0
V_REF = 3.3

LAST_CALIB_PATH: str | None = None
print(f"[PH] Module loaded from: {os.path.abspath(__file__)}")  # always prints

def load_calibration(config_path: str | None = None):
    """Load calibration values from JSON file and calculate slope/offset."""
    global PH_SLOPE, PH_OFFSET, CENTER_VOLTAGE, V_REF, ADC_MAX, LAST_CALIB_PATH
    _log = logging.getLogger(__name__)

    # Defaults (pH per mV)
    PH_SLOPE = DEFAULT_PH_SLOPE
    PH_OFFSET = DEFAULT_PH_OFFSET
    CENTER_VOLTAGE = DEFAULT_CENTER_VOLTAGE

    if config_path is None:
        env_path = os.environ.get("PH_CALIB_PATH")
        if env_path and os.path.exists(env_path):
            config_path = env_path
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(script_dir, "ph_calibration.json")

    try:
        LAST_CALIB_PATH = config_path
        print(f"[PH] Using calibration file: {os.path.abspath(config_path)}")  # always prints
        _log.info(f"Loading calibration from: {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Ignore any PH_SLOPE/PH_OFFSET present in JSON (we recompute)
        if "PH_SLOPE" in data or "PH_OFFSET" in data:
            _log.warning("Ignoring PH_SLOPE/PH_OFFSET in JSON; recomputing from voltages.")

        # Allow overriding refs
        V_REF = float(data.get("V_REF", V_REF))
        ADC_MAX = float(data.get("ADC_MAX", ADC_MAX))

        ph_4_voltage = data.get("PH_4_VOLTAGE")
        ph_7_voltage = data.get("PH_7_VOLTAGE")
        ph_10_voltage = data.get("PH_10_VOLTAGE")

        if ph_4_voltage is not None and ph_7_voltage is not None and ph_10_voltage is not None:
            v4 = float(ph_4_voltage)
            v7 = float(ph_7_voltage)
            v10 = float(ph_10_voltage)

            CENTER_VOLTAGE = v7  # ΔV at pH7 = 0 mV

            # Compute slope directly in pH per mV
            eps = 1e-12
            s1_mV = (7.0 - 4.0) / ((v7 - v4 + eps) * 1000.0)   # pH/mV
            s2_mV = (10.0 - 7.0) / ((v10 - v7 + eps) * 1000.0) # pH/mV
            PH_SLOPE = (s1_mV + s2_mV) / 2.0                   # pH/mV

            # Centered at pH7 -> offset is exactly 7.0
            PH_OFFSET = 7.0

            # Strong guard: if per-Volt slipped in, correct it
            if abs(PH_SLOPE) > 0.5:
                _log.warning(f"PH_SLOPE={PH_SLOPE:.6f} pH/mV unrealistic; scaling /1000 as if pH/V")
                PH_SLOPE = PH_SLOPE / 1000.0
            if abs(PH_SLOPE) > 0.5:
                _log.warning("PH_SLOPE still unrealistic; reverting to default.")
                PH_SLOPE = DEFAULT_PH_SLOPE
                PH_OFFSET = DEFAULT_PH_OFFSET
                CENTER_VOLTAGE = DEFAULT_CENTER_VOLTAGE

            # Sanity predictions
            ph_at_v4 = PH_SLOPE * ((v4 - v7) * 1000.0) + PH_OFFSET
            ph_at_v7 = PH_SLOPE * 0.0 + PH_OFFSET
            ph_at_v10 = PH_SLOPE * ((v10 - v7) * 1000.0) + PH_OFFSET

            _log.info(
                f"Calibration: slope={PH_SLOPE:.6f} pH/mV, offset={PH_OFFSET:.3f}, center={CENTER_VOLTAGE:.4f} V"
            )
            print(f"[PH] Calibrated slope={PH_SLOPE:.6f} pH/mV, offset={PH_OFFSET:.3f}, center={CENTER_VOLTAGE:.4f} V")
            _log.info(
                f"Predicted pH @ v4={v4:.4f}V -> {ph_at_v4:.3f}, v7={v7:.4f}V -> {ph_at_v7:.3f}, v10={v10:.4f}V -> {ph_at_v10:.3f}"
            )
        else:
            _log.info("Calibration points missing; using defaults.")
            print("[PH] Calibration points missing; using defaults.")
    except FileNotFoundError:
        _log.warning(f"Calibration file not found at {config_path}; using defaults.")
        print(f"[PH] Calibration file not found at {config_path}; using defaults.")
    except Exception as e:
        _log.warning(f"Failed to load calibration file {config_path}: {e}; using defaults")
        print(f"[PH] Failed to load calibration file {config_path}: {e}; using defaults")


def _resolve_calib_path(config_path: str | None = None) -> str:
    """Resolve the calibration file path using env var or module folder."""
    if config_path and os.path.exists(config_path):
        return config_path
    env_path = os.environ.get("PH_CALIB_PATH")
    if env_path and os.path.exists(env_path):
        return env_path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, "ph_calibration.json")

def calibrate_voltage_for_ph(target_ph: float, samples: int = 20, channel: int = SENSOR_CHANNEL, config_path: str | None = None) -> dict:
    """Average 'samples' readings and store the voltage for the given buffer pH.
    Returns basic stats so the caller can display them."""
    cfg_path = _resolve_calib_path(config_path)
    key = None
    if abs(target_ph - 4.0) <= 0.5:
        key = "PH_4_VOLTAGE"
    elif abs(target_ph - 7.0) <= 0.5:
        key = "PH_7_VOLTAGE"
    elif abs(target_ph - 10.0) <= 0.5:
        key = "PH_10_VOLTAGE"
    else:
        raise ValueError("target_ph must be one of 4, 7, or 10")

    reader = PHSensorReader()
    volts: list[float] = []
    phs: list[float] = []
    for _ in range(max(1, int(samples))):
        reading = reader.read_raw(channel)
        volts.append(float(reading["voltage_v"]))
        phs.append(float(reading["ph"]))
        time.sleep(SAMPLING_INTERVAL)

    avg_v = sum(volts) / len(volts)
    avg_ph = sum(phs) / len(phs) if phs else float("nan")
    # Load, update, save JSON
    try:
        if os.path.exists(cfg_path):
            with open(cfg_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {}
    except Exception:
        data = {}
    data[key] = round(avg_v, 6)

    # Keep these fields if already present
    if "V_REF" not in data:
        data["V_REF"] = V_REF
    if "ADC_MAX" not in data:
        data["ADC_MAX"] = ADC_MAX

    with open(cfg_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"[PH] Calibrated {key} = {avg_v:.6f} V using {len(volts)} samples "
          f"(avg pH during sampling: {avg_ph:.3f}) -> {cfg_path}")

    # Reload calibration to recompute slope/offset and show predictions
    load_calibration(cfg_path)

    return {
        "avg_voltage_v": float(avg_v),
        "avg_ph": float(avg_ph),
        "samples": int(len(volts)),
    }

# Load calibration at module import time (will fall back to defaults)
load_calibration()

# Get logger for this module (no handlers configured here)
logger = logging.getLogger(__name__)


class PHSensorReader:
    """Reader that uses smbus2 i2c_rdwr to query the Grove Base Hat ADC."""
    def __init__(
        self,
        addr: int = 0x08,
        busnum: int = 1,
        center_voltage: float | None = None,  # use latest global at call time
    ):
        self.addr = addr
        self.busnum = busnum
        self.center_voltage = float(CENTER_VOLTAGE if center_voltage is None else center_voltage)

    def _read_raw_bytes(self, channel: int = 0) -> List[int]:
        try:
            from smbus2 import i2c_msg, SMBus
        except Exception as e:
            raise RuntimeError(
                "smbus2 is required; install with 'pip install smbus2' and run on the Pi"
            ) from e

        # if not (0 <= channel <= 3):
        #     raise ValueError("channel must be 0..3")

        with SMBus(self.busnum) as bus:
            # Explicit write then read (works for many MM32/Grove hats)
            write = i2c_msg.write(self.addr, [0x30, channel, 0x00, 0x00])
            bus.i2c_rdwr(write)
            read = i2c_msg.read(self.addr, 4)
            bus.i2c_rdwr(read)
            data = list(read)
            print("i2c_rdwr read:", data)

        return data

    def read_raw(self, channel: int = 0) -> dict:
        data = self._read_raw_bytes(channel)

        candidates = []
        if len(data) >= 2:
            v0 = (data[0] | (data[1] << 8)) & 0xFFFF
            candidates.append(("low_first", v0))
        if len(data) >= 4:
            v1 = (data[2] | (data[3] << 8)) & 0xFFFF
            candidates.append(("mid_pair", v1))
            v2 = (data[0] << 8) | data[1]
            candidates.append(("high_first", v2))

        raw = None
        chosen_method = None
        for name, val in candidates:
            if 0 <= val <= ADC_MAX:
                raw = int(val)
                chosen_method = name
                break

        if raw is None:
            raw = ((data[0] | (data[1] << 8)) & 0x0FFF) if len(data) >= 2 else 0
            chosen_method = "fallback_mask12"

        voltage_v = (raw / ADC_MAX) * V_REF
        voltage_mV = (voltage_v - self.center_voltage) * 1000.0

        # Force per‑mV at runtime as a last resort
        slope_used = PH_SLOPE
        if abs(slope_used) > 0.5:
            logger.warning(f"PH_SLOPE seems per-Volt ({slope_used:.6f}); scaling /1000")
            slope_used = slope_used / 1000.0

        ph_unclamped = slope_used * voltage_mV + PH_OFFSET
        ph = min(14.0, max(0.0, ph_unclamped))

        logger.info(
            f"[DEBUG] Raw ADC: {raw}, V: {voltage_v:.4f}, Center: {self.center_voltage:.4f}, mV: {voltage_mV:.2f}, "
            f"slope_used(pH/mV): {slope_used:.6f}, offset: {PH_OFFSET:.3f}"
        )
        logger.info(f"[DEBUG] Calculated pH (clamped): {ph:.3f}")

        return {"raw": raw, "voltage_v": voltage_v, "voltage_mV": voltage_mV, "ph": ph, "raw_bytes": data, "chosen_method": chosen_method}

    def read_ph(self, channel: int = 0) -> float:
        r = self.read_raw(channel)
        return float(r["ph"])

    def read_average(
        self,
        channel: int = 0,
        samples: int = 40,
        delay: float = 0.05,
        trim: bool = True,
    ) -> Optional[float]:
        vals: List[float] = []
        for _ in range(samples):
            try:
                vals.append(self.read_ph(channel))
            except Exception:
                pass
            time.sleep(delay)

        if not vals:
            raise RuntimeError("no valid readings collected")

        if trim and len(vals) >= 5:
            vals_sorted = sorted(vals)
            vals = vals_sorted[1:-1]

        return float(statistics.mean(vals))


class PHSensor:
    """
    pH sensor wrapper class using the SMBus  reader.
    Public API is unchanged: `read_ph_sensor()` and `read_ph_averaged()`.
    """

    def __init__(self, channel: int = SENSOR_CHANNEL):
        """Initialize the pH sensor reader."""
        self.channel = channel
        self.current_ph = 7.0
        self.last_sampling_time = time.time()

        try:
            # Create fallback sensor instance
            self.sensor = PHSensorReader()
            logger.info("pH sensor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize pH sensor: {e}")
            raise

    def read_ph_sensor(self) -> Optional[float]:
        """Return a single pH reading (float) or None on error."""
        try:
            ph = self.sensor.read_ph(channel=self.channel)
            # Clamp to valid range
            if ph is None:
                return None
            if ph < 0:
                ph = 0.0
            elif ph > 14:
                ph = 14.0

            logger.debug(f"pH sensor reading: {ph:.2f}")
            self.current_ph = ph
            return ph
        except Exception as e:
            logger.error(f"Error reading pH sensor: {e}")
            return None

    def read_ph_averaged(
        self, samples: int = ARRAY_LENGTH, delay: float = SAMPLING_INTERVAL
    ) -> Optional[float]:
        """Return averaged pH value using the fallback averaging function."""
        try:
            # Use fallback's robust averaging if available
            ph = self.sensor.read_average(
                channel=self.channel, samples=samples, delay=delay
            )
            if ph is None:
                return None
            if ph < 0:
                ph = 0.0
            elif ph > 14:
                ph = 14.0

            self.current_ph = ph
            return ph
        except Exception as e:
            logger.error(f"Error reading averaged pH: {e}")
            return None

    # Backwards-compatible internal helper left in place in case other code calls it
    def _read_sensor_voltage(self) -> Optional[float]:
        """Return sensor voltage in millivolts (float) or None on error."""
        try:
            raw = self.sensor.read_raw(channel=self.channel)
            vm = raw.get("voltage_mV")
            if vm is None:
                return None
            return float(vm)
        except Exception as e:
            logger.error(f"Error reading sensor voltage: {e}")
            return None


# Convenience function for backwards compatibility
def read_ph():
    """
    Convenience function to read pH sensor data.
    Creates a temporary sensor instance and returns pH reading.

    Returns:
        float: pH value (0-14 scale), or None if error
    """
    try:
        sensor = PHSensor()
        return sensor.read_ph_sensor()
    except Exception as e:
        logger.error(f"Failed to read pH sensor: {e}")
        return None


def read_ph_averaged():
    """
    Convenience function to read averaged pH sensor data.
    Creates a temporary sensor instance and returns averaged pH reading.

    Returns:
        float: Averaged pH value (0-14 scale), or None if error
    """
    try:
        sensor = PHSensor()
        # Take several readings for immediate averaging
        val = sensor.read_ph_averaged()
        return val
    except Exception as e:
        logger.error(f"Failed to read averaged pH sensor: {e}")
        return None


# Diagnostic function to test all ADC channels
def test_all_channels():
    """Test all ADC channels to find where the sensor signal is connected."""
    print("Testing all ADC channels to find the pH sensor signal...")
    print("Looking for a channel that reads approximately 1.81V\n")
    
    try:
        reader = PHSensorReader()
        
        for channel in range(8):  # Test channels 0-7
            try:
                raw_data = reader.read_raw(channel)
                voltage = raw_data['voltage_v']
                raw_adc = raw_data['raw']
                print(f"Channel {channel}: Raw ADC = {raw_adc:4d}, Voltage = {voltage:.3f}V")
                
                # Check if this might be our pH sensor (around 1.8V)
                if 1.5 < voltage < 2.2:
                    print(f"  *** Channel {channel} might be your pH sensor! ***")
                    
            except Exception as e:
                print(f"Channel {channel}: Error - {e}")
                
    except Exception as e:
        print(f"Error initializing ADC reader: {e}")
    
    print("\nIf you found a channel with ~1.81V, update SENSOR_CHANNEL in the code.")

# Test function for standalone execution
def main():
    """Test function to verify pH sensor functionality."""
    print("Testing pH sensor...")
    print("Reading pH values every second...")
    print("Press Ctrl+C to exit\n")

    try:
        # Recreate sensor AFTER load_calibration ran in __main__
        sensor = PHSensor()

        while True:
            ph_value = sensor.read_ph_sensor()

            if ph_value is not None:
                print(f"pH: {ph_value:.2f}")
            else:
                print("Failed to read pH sensor")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nProgram stopped")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Configure file and console logging only when run directly
    log_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )

    # Create logs directory relative to this script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(script_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # File handler with daily rotation, keep 7 days
    log_file_path = os.path.join(logs_dir, "ph_sensor_ts.log")
    file_handler = TimedRotatingFileHandler(
        log_file_path,
        when="midnight",
        interval=1,
        backupCount=7,
    )
    file_handler.setFormatter(log_formatter)
    # Add date to rotated log files
    file_handler.suffix = "%Y-%m-%d"

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)

    # Configure logging with our handlers
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False

    logger.info(f"Running module: {os.path.abspath(__file__)}")
    load_calibration()

    import argparse
    parser = argparse.ArgumentParser(description="pH sensor reader")
    parser.add_argument(
        "--show-calib",
        action="store_true",
        help="Print the currently loaded calibration and exit",
    )
    parser.add_argument(
        "--test-channels",
        action="store_true", 
        help="Test all ADC channels to find the pH sensor signal",
    )
    parser.add_argument("--calibrate", type=float, choices=[4.0, 7.0, 10.0],
                        help="Average readings and store voltage for the given buffer (4, 7, or 10).")
    parser.add_argument("--samples", type=int, default=40,
                        help="Number of readings to average during calibration (default: 40).")
    parser.add_argument("--channel", type=int, default=SENSOR_CHANNEL,
                        help="ADC channel to use (default: SENSOR_CHANNEL).")
    parser.add_argument("--calib-path", type=str, default=None,
                        help="Override path to ph_calibration.json.")
    args = parser.parse_args()

    if args.calibrate is not None:
        result = calibrate_voltage_for_ph(args.calibrate, samples=args.samples, channel=args.channel, config_path=args.calib_path)
        # Exit after calibration
        print("Loaded calibration values:")
        print(f"  MODULE FILE      = {os.path.abspath(__file__)}")
        print(f"  CALIBRATION FILE = {_resolve_calib_path(args.calib_path)}")
        print(f"  PH_SLOPE         = {PH_SLOPE}")
        print(f"  PH_OFFSET        = {PH_OFFSET}")
        print(f"  CENTER_VOLTAGE   = {CENTER_VOLTAGE}")
        print(f"  AVG PH (CAL)     = {result.get('avg_ph', float('nan')):.3f} over {result.get('samples', 0)} samples")
        raise SystemExit(0)

    if args.show_calib:
        print("Loaded calibration values:")
        print(f"  MODULE FILE      = {os.path.abspath(__file__)}")
        print(f"  CALIBRATION FILE = {LAST_CALIB_PATH}")
        print(f"  PH_SLOPE         = {PH_SLOPE}")
        print(f"  PH_OFFSET        = {PH_OFFSET}")
        print(f"  CENTER_VOLTAGE   = {CENTER_VOLTAGE}")
        sys.exit(0)
        
    if args.test_channels:
        test_all_channels()
        sys.exit(0)

    # Temporarily run channel test first, then normal operation
    print("=== RUNNING CHANNEL TEST FIRST ===")
    test_all_channels()
    print("\n=== NOW RUNNING NORMAL PH SENSOR TEST ===\n")
    main()
