#!/usr/bin/env python3
"""
    Name: psutil_system.info.py
    Author: William A Loring
    Created: 09-18-21 Revised:
    Purpose: Test program with functions for monitoring CPU
    and RAM usage in Python with PsUtil.
"""

import os
import sys
from time import sleep
# pip install psutil
import psutil
# Windows: pip install rich
# Linux: pip3 install rich
# Import Console for console printing
from rich.console import Console
# Import Panel for title displays
from rich.panel import Panel

# Initialize rich.console
console = Console()


class SystemInfo:
    def __init__(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.sent = 0
        self.recv = 0
        while True:
            console.print(
                Panel.fit(
                    " System Information ",
                    style="bold blue")
            )
            console.print(
                f"           CPU: {psutil.cpu_count(logical=False)}              ")
            console.print(f"  Logical CPU: {psutil.cpu_count()}    ")

            # Output current CPU usage as a percentage
            console.print(f"     CPU usage: {self.get_cpu_usage_pct()} %    ")

            # Output current CPU frequency in GHz
            console.print(
                f" CPU frequency: {(self.get_cpu_frequency()):,.2f} GHz    ")

            # Output total RAM in GB
            console.print(
                f"     RAM total: {self.get_ram_total():,.2f} GB    ")

            # Output current RAM usage in GB
            console.print(
                f"     RAM usage: {self.get_ram_usage():,.2f} GB    ")

            # Output current RAM usage as a percentage.
            console.print(f"     RAM usage: {self.get_ram_usage_pct()} %    ")

            # Display network io in Kilobits per second
            console.print(f"   Net IO sent: {self.sent:,.1f} Kbps       ")
            console.print(f"   Net IO recv: {self.recv:,.1f} Kbps        ")

            # Get current network io statistics in Kbps
            sent_1, recv_1 = self.get_network_io()
            sleep(1)
            # Get current network io statistics in Kbps
            sent_2, recv_2 = self.get_network_io()
            # Subtract first reading from second reading
            # gives us how many kilobits were sent/recv per second
            self.sent = sent_2 - sent_1
            self.recv = recv_2 - recv_1

            console.clear()

    def get_network_io(self):
        """
            Get current net io counters statistics in bytes
            convert to bits, then kb
        """
        sent = psutil.net_io_counters().bytes_sent
        recv = psutil.net_io_counters().bytes_recv
        # Convert bytes to bits *8, convert bits to kilobits / 1024
        sent = (sent * 8) / 1024
        recv = (recv * 8) / 1024

        return sent, recv

    def get_cpu_usage_pct(self):
        """
            Obtains the system's average CPU load as measured over a period of 500 milliseconds.
            interval=0.5
            :returns: System CPU load as a percentage.
            :rtype: float
        """
        return psutil.cpu_percent(interval=None)

    def get_cpu_frequency(self):
        """
            Obtains the real-time value of the current CPU frequency.
            :returns: Current CPU frequency in BHz.
            :rtype: int
        """
        return int(psutil.cpu_freq().current) / 1024

    def get_ram_usage(self):
        """
            Obtains the absolute number of RAM bytes currently in use by the system.
            :returns: System RAM usage in Gigabytes.
            :rtype: int
        """
        ram_useage = int(psutil.virtual_memory().total -
                         psutil.virtual_memory().available)
        return ram_useage / 1024 / 1024 / 1024

    def get_ram_total(self):
        """
            Obtains the total amount of RAM in bytes available to the system.
            :returns: Total system RAM in bytes.
            :rtype: int
        """
        ram_total = int(psutil.virtual_memory().total)
        return ram_total / 1024 / 1024 / 1024

    def get_ram_usage_pct(self):
        """
            Obtains the system's current RAM usage.
            :returns: System RAM usage as a percentage.
            :rtype: float
        """
        return psutil.virtual_memory().percent


if __name__ == "__main__":
    try:
        system_info = SystemInfo()
    except KeyboardInterrupt:
        sys.exit(0)
