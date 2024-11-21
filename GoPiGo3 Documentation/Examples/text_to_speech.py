"""
    Name: text_to_speech.py
    Author:
    Created:
    Purpose: Render text into speech
    This library has many modules with which you can try
    changing the voice, volume, and speed rate of the audio.
    https://pypi.org/project/pyttsx3/
    https://pyttsx3.readthedocs.io/en/latest/
"""
from sys import exit
from time import sleep
# Raspberry Pi
# pip3 install pyttsx3
import pyttsx3


class TextToAudio:
    def __init__(self):
        # Change these constants to experiment with the speech engine
        RATE = 150    # integer default 200 words per minute
        VOLUME = 0.9  # float 0.0-1.0 inclusive default 1.0
        # VOICE = 1     # Set 1 for Zira (female), 0 for David (male)
        # Initialize the pyttxs3 voice engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', RATE)
        self.engine.setProperty('volume', VOLUME)
        # Retrieves all available voices from your system.
        # voices = self.engine.getProperty('voices')
        # self.engine.setProperty('voice', voices[VOICE].id)
        # Run engine to set properties
        self.engine.runAndWait()

# -------------------------- GREET USER ---------------------------------- #
    def greet_user(self):
        self.engine.say("Hello, I am Zira.")
        self.engine.say("What would you like me to say? Press CTRL C to exit")
        print("Talking . . .")
        self.engine.runAndWait()

# -------------------- MAIN PROGRAM LOOP --------------------------------- #
    def main_program(self):
        # Repeating loop, CTRL-C to exit
        while True:
            try:
                self.speak()
            except KeyboardInterrupt:
                self.quit_program()

# ---------------------------- QUIT PROGRAM ------------------------------ #
    def quit_program(self):
        # Quit program
        print("\nHave a good day!")
        self.engine.say("Have a good day!")
        self.engine.runAndWait()
        self.engine.stop()
        sleep(2)
        exit(0)

# --------------------- SPEAK -------------------------------------------- #
    def speak(self):
        # Get text from command line
        spoken_text = input("((<< ")
        # Call the say method to speak the text
        self.engine.say(spoken_text)
        print("Talking . . .")
        self.engine.runAndWait()


# ------------- MAIN PROGRAM --------------------------------------------- #
# Create program object to run program
text_to_audio = TextToAudio()
text_to_audio.greet_user()
text_to_audio.main_program()
