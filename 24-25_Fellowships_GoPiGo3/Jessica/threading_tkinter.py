import tkinter as tk
# Import the Thread class from the threading module
# to handle concurrent operations
from threading import Thread, Event
# Import the time module to use sleep() and time() functions
import time


class ThreadingApp:
    def __init__(self):
        # Create the main window of the application
        self.root = tk.Tk()
        # Set the title of the window
        self.root.title("Threading with Tkinter")
        # Call the method to set up the GUI elements
        self.setup_gui()
        self.stop_event = Event()  # Event to signal the thread to stop
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

# ----------------------------- SETUP GUI ---------------------------------- #
    def setup_gui(self):
        # Create label widget to display text
        self.lbl_display = tk.Label(self.root, text="Threading with Tkinter")
        # Place label in the window with 20 pixels padding on top and bottom
        self.lbl_display.pack(pady=20)

        # Create a button that will start the thread when clicked
        start_button = tk.Button(
            self.root,                    # Parent widget is the main window
            text="Start Thread",          # Text shown on the button
            command=self.start_thread     # Function to call when button is clicked
        )
        # Place button in the window with 20 pixels padding on top and bottom
        start_button.pack(pady=20)

        stop_button = tk.Button(
            self.root,
            text="Stop Thread",
            command=self.stop_thread
        )
        stop_button.pack(pady=20)

# ----------------------------- BACKGROUND TASK ---------------------------- #
    def background_task(self):
        """This method runs in a separate thread
           and performs a background task"""
        while not self.stop_event.is_set():  # Check if the stop event is set
            # Update the label text with the current timestamp
            now = time.localtime()
            now = f"{now.tm_min:02d}:{now.tm_sec:02d}"
            self.lbl_display.config(
                text=f"Running background task {now}"
            )

            # Pause for 1 second before the next update
            time.sleep(1)

# ----------------------------- START THREAD ------------------------------- #
    def start_thread(self):
        # Clear the stop event before starting the thread
        self.stop_event.clear()
        # Create a new thread object
        thread = Thread(
            target=self.background_task,  # Function to run in the thread
            daemon=True                   # Thread stops when program ends
        )
        # Start the thread's execution
        thread.start()

# ----------------------------- STOP THREAD -------------------------------- #
    def stop_thread(self):
        # Set the stop event to signal the thread to stop
        self.stop_event.set() 

# ----------------------------- ON CLOSING --------------------------------- #
    def on_closing(self):
        self.stop_thread()  # Stop the thread when closing the window
        self.root.destroy()  # Destroy the window


def main():
    # Create an instance of our application
    app = ThreadingApp()


# Only run the app if this file is run directly (not imported)
if __name__ == "__main__":
    main()
