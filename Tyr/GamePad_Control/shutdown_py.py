"""
shutdown_py.py
Owen Osmera
Purpose: Shows what subprocess needs to be done to shut off pi from controller
"""

import subprocess

result = subprocess.run(["sudo /usr/sbin/poweroff"], shell=True, capture_output=True, text=True)

print(result)
