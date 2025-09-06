#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: speedtest_logger.py
Author: William A Loring
Created: 12/05/21
Modified: 09/03/25
Speedtest logger that runs tests automatically, averages results,
and logs to rotating files
"""
import time
import schedule
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from statistics import mean
from speedtest import Speedtest
from rich.console import Console
from rich.panel import Panel

# Configuration constants
TEST_INTERVAL_MINUTES = 60  # How often to run tests (in minutes)
NUM_RUNS_TO_AVERAGE = 3     # Number of runs to average
LOG_FILE_PATH = "speedtest_log.txt"


class SpeedtestLogger:
    def __init__(self):
        # Initialize rich console
        self.console = Console()
        
        # Setup logging with daily rotation
        self.setup_logging()
        
        # Create speedtest object
        self._speedtest = Speedtest(secure=True)
        
        self.console.print(
            Panel.fit(
                "        Internet Speed Test Logger        ",
                style="bold blue",
                subtitle=f"Testing every {TEST_INTERVAL_MINUTES} minutes | Averaging {NUM_RUNS_TO_AVERAGE} runs",
            )
        )

    def setup_logging(self):
        """Setup logging with daily rotation."""
        # Create a custom logger
        self.logger = logging.getLogger('speedtest_logger')
        self.logger.setLevel(logging.INFO)
        
        # Create handler that rotates daily at midnight
        handler = TimedRotatingFileHandler(
            LOG_FILE_PATH,
            when='midnight',
            interval=1,
            backupCount=70,  # Keep 7 days of logs
            encoding='utf-8'
        )
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(handler)
        
        # Also log to console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def get_servers(self):
        """Get the best server for testing."""
        try:
            server = self._speedtest.get_best_server()
            self._sponsor = server.get("sponsor", "Unknown")
            self._location = server.get("name", "Unknown")
            self._country_code = server.get("cc", "Unknown")
            return True
        except Exception as e:
            self.logger.error(f"Failed to get servers: {e}")
            return False

    def run_single_test(self):
        """Run a single speedtest and return results."""
        try:
            # Get download speed
            download_bps = self._speedtest.download()
            download_mbps = download_bps / 10**6
            
            # Get upload speed  
            upload_bps = self._speedtest.upload()
            upload_mbps = upload_bps / 10**6
            
            # Get ping
            ping_ms = self._speedtest.results.ping
            
            return {
                'download': download_mbps,
                'upload': upload_mbps,
                'ping': ping_ms,
                'timestamp': datetime.now()
            }
        except Exception as e:
            self.logger.error(f"Test failed: {e}")
            return None

    def run_averaged_test(self):
        """Run multiple tests and return averaged results."""
        self.console.print(f"[bold cyan]Starting {NUM_RUNS_TO_AVERAGE} speed tests...[/bold cyan]")
        
        # Get server info
        if not self.get_servers():
            return None
            
        results = []
        
        for i in range(NUM_RUNS_TO_AVERAGE):
            self.console.print(f"[yellow]Running test {i+1}/{NUM_RUNS_TO_AVERAGE}...[/yellow]")
            
            # Create new speedtest object for each run to avoid issues
            self._speedtest = Speedtest(secure=True)
            
            result = self.run_single_test()
            if result:
                results.append(result)
                self.console.print(f"[green]✓ Test {i+1} complete: "
                                 f"↓{result['download']:.1f} ↑{result['upload']:.1f} "
                                 f"ping:{result['ping']:.0f}ms[/green]")
            else:
                self.console.print(f"[red]✗ Test {i+1} failed[/red]")
            
            # Small delay between tests
            if i < NUM_RUNS_TO_AVERAGE - 1:
                time.sleep(2)
        
        if not results:
            self.logger.error("All tests failed")
            return None
            
        # Calculate averages
        avg_download = mean([r['download'] for r in results])
        avg_upload = mean([r['upload'] for r in results])
        avg_ping = mean([r['ping'] for r in results])
        
        averaged_result = {
            'download': avg_download,
            'upload': avg_upload,
            'ping': avg_ping,
            'timestamp': datetime.now(),
            'server': f"{self._sponsor} - {self._location}, {self._country_code}",
            'num_tests': len(results)
        }
        
        return averaged_result

    def log_result(self, result):
        """Log the test result."""
        if result:
            log_message = (
                f"Download: {result['download']:.2f} Mbps | "
                f"Upload: {result['upload']:.2f} Mbps | "
                f"Ping: {result['ping']:.1f} ms | "
                f"Server: {result['server']} | "
                f"Tests averaged: {result['num_tests']}"
            )
            self.logger.info(log_message)
            
            # Display to console
            self.console.print(
                Panel(
                    f"[bold green]📊 Average Results ({result['num_tests']} tests)[/bold green]\n\n"
                    f"[bold cyan]Server:[/bold cyan] {result['server']}\n"
                    f"[bold magenta]📥 Download:[/bold magenta] [bold green]{result['download']:.2f} Mbps[/bold green]\n"
                    f"[bold magenta]📤 Upload:[/bold magenta]   [bold green]{result['upload']:.2f} Mbps[/bold green]\n"
                    f"[bold magenta]⚡ Ping:[/bold magenta]     [bold green]{result['ping']:.1f} ms[/bold green]",
                    title="[bold blue]🌐 Speed Test Complete[/bold blue]",
                    border_style="blue"
                )
            )

    def scheduled_test(self):
        """Run the scheduled speedtest."""
        self.console.print(f"\n[bold yellow]🕐 {datetime.now().strftime('%H:%M:%S')} - Starting scheduled speedtest[/bold yellow]")
        
        result = self.run_averaged_test()
        self.log_result(result)
        
        next_run = datetime.now().replace(second=0, microsecond=0)
        next_run = next_run.replace(minute=(next_run.minute // TEST_INTERVAL_MINUTES + 1) * TEST_INTERVAL_MINUTES % 60)
        if next_run.minute == 0:
            next_run = next_run.replace(hour=next_run.hour + 1)
        
        self.console.print(f"[dim]Next test scheduled for: {next_run.strftime('%H:%M')}[/dim]\n")

    def start_logging(self):
        """Start the automated logging."""
        self.logger.info("Speedtest logger started")
        self.console.print(f"[bold green]Logger started! Testing every {TEST_INTERVAL_MINUTES} minutes[/bold green]")
        
        # Schedule the tests
        schedule.every(TEST_INTERVAL_MINUTES).minutes.do(self.scheduled_test)
        
        # Run first test immediately
        self.scheduled_test()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.console.print("\n[bold red]Logger stopped by user[/bold red]")
            self.logger.info("Speedtest logger stopped by user")


def main():
    logger = SpeedtestLogger()
    logger.start_logging()


if __name__ == "__main__":
    main()
