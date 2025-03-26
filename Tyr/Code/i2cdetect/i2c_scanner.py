# i2c_scanner.py
from smbus import SMBus

# Initialize the I2C bus
bus = SMBus(1)

print("Scanning for I2C devices...")

for address in range(128):
    try:
        bus.read_byte(address)
        print(f"Device found at address 0x{address:02X}")
    except OSError:
        pass

print("Scan complete.")