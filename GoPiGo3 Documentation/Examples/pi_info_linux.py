#!/usr/bin/env python3
# Uses subprocess to use Linux shell commands to get pi system info
"""
    Name: pi_info_linux.py
    Author: 
    Created: 
    Purpose: 
"""

import sys
import subprocess

cmd = "cat /proc/device-tree/model"
model = subprocess.check_output(cmd, shell=True).decode("utf-8")
print("-----------------------------------------")
print(model)
print("-----------------------------------------")

print("Python: " + sys.version)
cmd = "hostname -I"
IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
print("IP: " + IP, end='')

cmd = "vcgencmd measure_temp"
temp_c = subprocess.check_output(cmd, shell=True).decode("utf-8")
print(temp_c, end='')

# temp_f = (float(temp_c) * (9 / 5)) + 32
# print(f"{temp_f}'F")

cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
print(CPU)

cmd = "free -m | awk 'NR==2{printf \"Memory usage: %s/%s MB %.2f%%\", $3,$2,$3*100/$2 }'"
MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
print(MemUsage)

cmd = "df -h | awk '$NF==\"/\"{printf \"Disk usage: %d/%d GB %s\", $3,$2,$5}'"
DiskUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
print(DiskUsage)
print("-----------------------------------------")

