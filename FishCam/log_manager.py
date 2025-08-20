#!/usr/bin/env python3
"""
Log management utility for the Aquaponics Sensor Monitoring System
"""

import os
import sys
import glob
from datetime import datetime, timedelta


def get_log_directory():
    """Get the logs directory path"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")


def list_log_files():
    """List all log files with details"""
    log_dir = get_log_directory()

    print(f"Log files in {log_dir}:")
    print("-" * 80)

    # Get all .log files
    log_pattern = os.path.join(log_dir, "*.log*")
    log_files = glob.glob(log_pattern)

    if not log_files:
        print("No log files found")
        return

    # Sort by modification time (newest first)
    log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

    print(f"{'Filename':<35} {'Size':<12} {'Modified':<20} {'Type'}")
    print("-" * 80)

    for log_file in log_files:
        filename = os.path.basename(log_file)
        size = os.path.getsize(log_file)
        modified = datetime.fromtimestamp(os.path.getmtime(log_file))

        # Determine type based on filename patterns
        if filename == "sensors_ts.log":
            file_type = "Current"
        elif filename.startswith("sensors_ts.") and filename.endswith(".log"):
            file_type = "Rotated"
        elif filename == "email_notification.log":
            file_type = "Email Current"
        elif filename.startswith("email_notification.") and filename.endswith(".log"):
            file_type = "Email Rotated"
        elif filename == "web_stream.log":
            file_type = "Stream Current"
        elif filename.startswith("web_stream.") and filename.endswith(".log"):
            file_type = "Stream Rotated"
        else:
            file_type = "Other"

        size_str = f"{size:,} bytes"
        modified_str = modified.strftime("%Y-%m-%d %H:%M:%S")

        print(f"{filename:<35} {size_str:<12} {modified_str:<20} {file_type}")


def show_log_tail(filename="sensors_ts.log", lines=20):
    """Show the last N lines of a log file"""
    log_dir = get_log_directory()
    log_path = os.path.join(log_dir, filename)

    if not os.path.exists(log_path):
        print(f"Log file not found: {filename}")
        return

    print(f"Last {lines} lines of {filename}:")
    print("-" * 80)

    try:
        with open(log_path, "r", encoding="utf-8") as f:
            all_lines = f.readlines()
            tail_lines = (
                all_lines[-lines:] if len(all_lines) > lines else all_lines
            )

            for line in tail_lines:
                print(line.rstrip())

    except Exception as e:
        print(f"Error reading log file: {e}")


def show_log_stats():
    """Show statistics about log rotation"""
    log_dir = get_log_directory()

    print("Log Rotation Statistics:")
    print("-" * 40)
    print(f"Log directory: {log_dir}")

    # Check different log types
    log_types = [
        ("sensors_ts", "Sensor Monitoring"),
        ("email_notification", "Email System"),
        ("web_stream", "Stream Viewer"),
    ]

    total_files = 0
    total_size = 0

    for log_prefix, log_description in log_types:
        logs = glob.glob(os.path.join(log_dir, f"{log_prefix}*.log"))
        
        if logs:
            type_size = sum(os.path.getsize(f) for f in logs)
            total_files += len(logs)
            total_size += type_size
            
            print(f"\n{log_description}:")
            print(f"  Files: {len(logs)}")
            print(f"  Size: {type_size:,} bytes ({type_size/1024:.1f} KB)")

            # Current log
            current_log = os.path.join(log_dir, f"{log_prefix}.log")
            if os.path.exists(current_log):
                current_size = os.path.getsize(current_log)
                current_modified = datetime.fromtimestamp(
                    os.path.getmtime(current_log)
                )
                print(f"  Current log size: {current_size:,} bytes")
                print(f"  Last modified: {current_modified}")

            # Rotated logs
            rotated_logs = [f for f in logs if f != current_log]
            if rotated_logs:
                print(f"  Rotated files: {len(rotated_logs)}")
                oldest_log = min(rotated_logs, key=lambda x: os.path.getmtime(x))
                oldest_date = datetime.fromtimestamp(os.path.getmtime(oldest_log))
                print(f"  Oldest: {os.path.basename(oldest_log)} ({oldest_date.strftime('%Y-%m-%d')})")

    print(f"\nOverall Statistics:")
    print(f"Total log files: {total_files}")
    print(f"Total size: {total_size:,} bytes ({total_size/1024:.1f} KB)")

    # Next rotation time
    now = datetime.now()
    next_midnight = (now + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    time_to_rotation = next_midnight - now

    print(f"\nNext rotation: {next_midnight.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Time until rotation: {time_to_rotation}")


def search_logs(search_term, filename=None, log_type="all"):
    """Search for a term in log files"""
    log_dir = get_log_directory()

    if filename:
        log_files = [os.path.join(log_dir, filename)]
    elif log_type == "sensors":
        log_files = glob.glob(os.path.join(log_dir, "sensors_ts*.log"))
    elif log_type == "email":
        log_files = glob.glob(os.path.join(log_dir, "email_notification*.log"))
    elif log_type == "stream":
        log_files = glob.glob(os.path.join(log_dir, "web_stream*.log"))
    else:  # all
        log_files = glob.glob(os.path.join(log_dir, "*.log"))

    print(f"Searching for '{search_term}' in log files:")
    print("-" * 80)

    total_matches = 0

    for log_file in sorted(log_files):
        if not os.path.exists(log_file):
            continue

        filename = os.path.basename(log_file)
        matches = 0

        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    if search_term.lower() in line.lower():
                        matches += 1
                        print(f"{filename}:{line_num}: {line.strip()}")

        except Exception as e:
            print(f"Error reading {filename}: {e}")
            continue

        if matches > 0:
            total_matches += matches
            print(f"  -> {matches} matches in {filename}")

    print(f"\nTotal matches: {total_matches}")


def clean_old_logs(days_to_keep=7):
    """Clean log files older than specified days"""
    log_dir = get_log_directory()
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    
    print(f"Cleaning logs older than {days_to_keep} days (before {cutoff_date.strftime('%Y-%m-%d')}):")
    print("-" * 60)
    
    # Match rotated log files with date pattern before .log extension
    log_files = glob.glob(os.path.join(log_dir, "*.????-??-??.log"))
    deleted_count = 0
    freed_space = 0
    
    for log_file in log_files:
        file_date = datetime.fromtimestamp(os.path.getmtime(log_file))
        if file_date < cutoff_date:
            try:
                file_size = os.path.getsize(log_file)
                os.remove(log_file)
                filename = os.path.basename(log_file)
                print(f"Deleted: {filename} ({file_size:,} bytes)")
                deleted_count += 1
                freed_space += file_size
            except Exception as e:
                print(f"Error deleting {os.path.basename(log_file)}: {e}")
    
    if deleted_count == 0:
        print("No old log files found to delete.")
    else:
        print(f"\nCleaned {deleted_count} files, freed {freed_space:,} bytes ({freed_space/1024:.1f} KB)")


def show_menu():
    """Display the main menu"""
    print("\n" + "=" * 70)
    print("        AQUAPONICS SENSOR LOG MANAGEMENT MENU")
    print("=" * 70)
    print("1. List all log files")
    print("2. Show log file tail (last lines)")
    print("3. Show log rotation statistics")
    print("4. Search in log files")
    print("5. Clean old log files")
    print("6. Exit")
    print("-" * 70)


def get_user_choice():
    """Get user menu choice"""
    while True:
        try:
            choice = input("Enter your choice (1-6): ").strip()
            if choice in ["1", "2", "3", "4", "5", "6"]:
                return int(choice)
            else:
                print("Invalid choice. Please enter 1, 2, 3, 4, 5, or 6.")
        except (ValueError, KeyboardInterrupt):
            print("\nExiting...")
            sys.exit(0)


def handle_tail_menu():
    """Handle the tail command with user input"""
    log_dir = get_log_directory()
    log_files = glob.glob(os.path.join(log_dir, "*.log*"))

    if not log_files:
        print("No log files found!")
        return

    print("\nAvailable log files:")
    for i, log_file in enumerate(log_files, 1):
        filename = os.path.basename(log_file)
        print(f"{i}. {filename}")

    print(f"{len(log_files) + 1}. sensors_ts.log (default)")

    # Get file choice
    while True:
        try:
            file_choice = input(
                f"\nSelect file (1-{len(log_files) + 1}) or press Enter for default: "
            ).strip()

            if file_choice == "":
                filename = "sensors_ts.log"
                break

            file_choice = int(file_choice)
            if 1 <= file_choice <= len(log_files):
                filename = os.path.basename(log_files[file_choice - 1])
                break
            elif file_choice == len(log_files) + 1:
                filename = "sensors_ts.log"
                break
            else:
                print(f"Invalid choice. Please enter 1-{len(log_files) + 1}")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Get number of lines
    while True:
        try:
            lines_input = input(
                "Number of lines to show (default: 20): "
            ).strip()
            if lines_input == "":
                lines = 20
                break
            lines = int(lines_input)
            if lines > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    show_log_tail(filename, lines)


def handle_search_menu():
    """Handle the search command with user input"""
    log_dir = get_log_directory()
    log_files = glob.glob(os.path.join(log_dir, "*.log*"))

    if not log_files:
        print("No log files found!")
        return

    # Get search term
    search_term = input("\nEnter search term: ").strip()
    if not search_term:
        print("Search term cannot be empty.")
        return

    # Get search scope
    print("\nSearch options:")
    print("1. Search all log files")
    print("2. Search sensor logs only")
    print("3. Search email logs only")
    print("4. Search stream logs only")
    print("5. Search specific file")

    while True:
        try:
            search_choice = input("Choose option (1-5): ").strip()
            if search_choice in ["1", "2", "3", "4", "5"]:
                break
            else:
                print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")
        except ValueError:
            print("Invalid input. Please enter 1, 2, 3, 4, or 5.")

    if search_choice == "1":
        search_logs(search_term, None, "all")
    elif search_choice == "2":
        search_logs(search_term, None, "sensors")
    elif search_choice == "3":
        search_logs(search_term, None, "email")
    elif search_choice == "4":
        search_logs(search_term, None, "stream")
    else:  # search_choice == "5"
        print("\nAvailable log files:")
        for i, log_file in enumerate(log_files, 1):
            filename = os.path.basename(log_file)
            print(f"{i}. {filename}")

        while True:
            try:
                file_choice = int(
                    input(f"Select file (1-{len(log_files)}): ").strip()
                )
                if 1 <= file_choice <= len(log_files):
                    filename = os.path.basename(log_files[file_choice - 1])
                    search_logs(search_term, filename)
                    break
                else:
                    print(f"Invalid choice. Please enter 1-{len(log_files)}")
            except ValueError:
                print("Invalid input. Please enter a number.")


def handle_clean_menu():
    """Handle the clean logs command with user input"""
    print("\nLog cleaning options:")
    print("Current retention policy: 7 days (configured in log rotation)")
    print("This will delete rotated log files older than specified days.")
    print("Current log files will NOT be deleted.")
    
    while True:
        try:
            days_input = input(
                "\nDays to keep (default: 7, or 'cancel' to abort): "
            ).strip().lower()
            
            if days_input == "cancel":
                print("Operation cancelled.")
                return
            elif days_input == "":
                days = 7
                break
            else:
                days = int(days_input)
                if days > 0:
                    break
                else:
                    print("Please enter a positive number of days.")
        except ValueError:
            print("Invalid input. Please enter a number or 'cancel'.")
    
    # Confirm the operation
    confirm = input(f"\nDelete rotated logs older than {days} days? (y/N): ").strip().lower()
    if confirm in ["y", "yes"]:
        clean_old_logs(days)
    else:
        print("Operation cancelled.")


def main():
    """Main function with interactive menu"""
    while True:
        show_menu()
        choice = get_user_choice()

        if choice == 1:
            print("\n" + "=" * 70)
            list_log_files()
        elif choice == 2:
            print("\n" + "=" * 70)
            handle_tail_menu()
        elif choice == 3:
            print("\n" + "=" * 70)
            show_log_stats()
        elif choice == 4:
            print("\n" + "=" * 70)
            handle_search_menu()
        elif choice == 5:
            print("\n" + "=" * 70)
            handle_clean_menu()
        elif choice == 6:
            print("\nGoodbye!")
            break

        # Wait for user to press Enter before showing menu again
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    print("Aquaponics Sensor Monitoring System - Log Management Utility")
    print("=" * 70)
    print("Interactive Menu-Driven Log Manager")

    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting log manager...")
        sys.exit(0)
