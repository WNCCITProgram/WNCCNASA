#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: speedtest_cli.py
Author: William A Loring
Created: 12/05/21
speedtest-cli is a Python module
that uses speedtest.net to test internet bandwidth
https://github.com/sivel/speedtest-cli
https://pypi.org/project/speedtest-cli/
"""
# speedtest-cli return bandwidth in bits per second
# A megabit is 1 million bits
# Bandwidth is typically measured in megabits per second (mbps)
# pip install speedtest-cli
from speedtest import Speedtest
import threading
import time
import sys

# Windows: pip install rich
# Linux: sudo apt install python3-rich
# Import Console for console printing
from rich.console import Console

# Import Panel for title displays
from rich.panel import Panel


class SpeedtestCLI:
    def __init__(self):
        # Initialize rich.console
        self.console = Console()

        self.console.print(
            Panel.fit(
                "        Internet Bandwidth Test        ",
                style="bold blue",
                subtitle="By William Loring",
            )
        )

        # Create speedtest object
        self._speedtest = Speedtest(secure=True)

        # Animation control
        self._stop_animation = False

    # ---------------------- ANIMATE DOTS ---------------------------------- #
    def animate_dots(self, message):
        """Animate dots while operation is running."""
        # Hide cursor during animation
        print('\033[?25l', end='', flush=True)
        
        while not self._stop_animation:
            for i in range(4):  # 0, 1, 2, 3 dots
                if self._stop_animation:
                    break
                # Create dots string based on current iteration
                dots = " ." * i
                # Use the previous method to clear the line
                line_text = f"{message}{dots}"
                print(f"\r{line_text:<50}", end="", flush=True)
                time.sleep(0.5)
        
        # Show cursor again after animation
        print('\033[?25h', end='', flush=True)

    # ----------------------- GET SERVERS ---------------------------------- #
    def get_servers(self):
        # Return the nearest test server and location in dictionary format
        # A ping test determines the server with the lowest latency
        server = self._speedtest.get_best_server()

        # Get information about nearest server from returned server dictionary
        self._sponsor = f'{server.get("sponsor")}'
        self._location = f'{server.get("name")}'
        self._country_code = f'{server.get("cc")}'

    # ------------------ GET DOWNLOAD BANDWIDTH ---------------------------- #
    def get_download_bandwidth(self):
        """Get download bandwidth from test server."""
        # Start animation in a separate thread
        self._stop_animation = False
        animation_thread = threading.Thread(
            target=self.animate_dots, args=("Get Download Bandwidth",)
        )
        animation_thread.daemon = True
        animation_thread.start()

        # Get bandwidth, returns bits per second
        download_result = self._speedtest.download()

        # Stop animation
        self._stop_animation = True
        animation_thread.join()
        # Clear the line completely and show clean final message with rich formatting
        print(f"\r{' ' * 80}\r", end="", flush=True)  # Clear line
        self.console.print(
            "[bold green]✓ Download Bandwidth Complete[/bold green]"
        )

        # Convert from bits per second to megabits per second
        self._download_result = download_result / 10**6

    # ------------------- GET UPLOAD BANDWIDTH ----------------------------- #
    def get_upload_bandwidth(self):
        """Get upload bandwidth from test server."""
        # Start animation in a separate thread
        self._stop_animation = False
        animation_thread = threading.Thread(
            target=self.animate_dots, args=("Get Upload Bandwidth",)
        )
        animation_thread.daemon = True
        animation_thread.start()

        # Get upload bandwidth, returns bits per second
        upload_result = self._speedtest.upload()

        # Stop animation
        self._stop_animation = True
        animation_thread.join()
        # Clear the line completely and show clean final message with rich formatting
        print(f"\r{' ' * 80}\r", end="", flush=True)  # Clear line
        self.console.print(
            "[bold green]✓ Upload Bandwidth Complete[/bold green]"
        )

        # Convert from bits per second to megabits per second
        self._upload_result = upload_result / 10**6

    # ----------------------- GET PING LATENCY ----------------------------- #
    def get_ping_latency(self):
        """Get ping (latency) from test server."""
        self.console.print("[bold green]✓ Ping Latency Complete[/bold green]")
        # Get ping results/latency, return ms
        self._ping_result = self._speedtest.results.ping

    # -------------------- DISPLAY SPEEDTEST RESULTS ----------------------- #
    def display_results(self):
        """Display results of speedtest."""
        line = (
            "[bold blue]------------------------------------------[/bold blue]"
        )
        self.console.print(line)

        # Display speedtest results
        sponsor = f"[bold yellow]{self._sponsor} - {self._location}, {self._country_code}[/bold yellow]"
        self.console.print(sponsor)

        download = f"📥 Download Bandwidth: [yellow]{self._download_result:.2f} Mbps[/yellow]"
        self.console.print(download)

        upload = f"  📤 Upload Bandwidth: [yellow]{self._upload_result:.2f} Mbps[/yellow]"
        self.console.print(upload)

        latency = (
            f"    ⚡ Latency (ping): [yellow]{self._ping_result} ms[/yellow]"
        )
        self.console.print(latency)

        self.console.print(line)


def main():
    # Create program object
    speedtest = SpeedtestCLI()

    # Program menu loop
    while True:
        # Call program object methods
        speedtest.get_servers()
        speedtest.get_download_bandwidth()
        speedtest.get_upload_bandwidth()
        speedtest.get_ping_latency()
        speedtest.display_results()

        speedtest.console.print()
        speedtest.console.print(
            "    [bold cyan]1:[/bold cyan] Test again\n[bold cyan]Enter:[/bold cyan] Exit"
        )
        choice = input(">> ")
        if choice == "":
            speedtest.console.print("[bold red]Goodbye! 👋[/bold red]")
            break


main()
