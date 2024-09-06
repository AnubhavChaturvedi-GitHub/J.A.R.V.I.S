import os
import pygame
import random
from pygame import mixer
from Features.clap_d import *


def play_random_music(folder_path):
    music_files = [file for file in os.listdir(folder_path) if file.endswith(('.mp3', '.wav', '.ogg', '.flac'))]

    if not music_files:
        print("No music files found in the specified folder.")
        return

    selected_music = random.choice(music_files)
    music_path = os.path.join(folder_path, selected_music)

    try:
        # Initialize pygame and mixer
        pygame.init()
        mixer.init()

        # Load and play the selected music file in the background
        mixer.music.load(music_path)
        mixer.music.play()

        # Wait for the music to finish (or you can add some delay or user input here)
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)  # Adjust the tick value as needed

        # Stop and quit pygame mixer
        mixer.music.stop()
        mixer.quit()
    except Exception as e:
        print(f"Error playing music: {e}")

def clap_to_music():
    while True:
        tt = TapTester()
        clap_count = 0

        while True:
            if tt.listen():
                clap_count += 2

                if clap_count == REQUIRED_CLAPS:
                    play_random_music(r"C:\Users\chatu\OneDrive\Desktop\J.A.R.V.I.S\DATA\MUSIC")
                    break