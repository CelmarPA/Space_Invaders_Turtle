import pygame
import os
from game_specs import EFFECTS_VOLUME, MUSIC_VOLUME


class SoundManager:
    """
    Manages sound effects and background music using pygame.mixer.
    Handles loading, playing, volume control, and basic music controls (pause, resume, stop).
    """

    def __init__(self):
        """
        Initialize the SoundManager.

        - Initializes the pygame mixer.
        - Loads sound effects into a dictionary.
        - Sets the background music path.
        - Applies default volume settings for sound effects.
        """

        pygame.mixer.init()

        # Base directory for sound files
        self.base_path = "sounds"

        # Load all sound effect files into a dictionary for easy access
        self.sounds = {
            "laser": self.load_sound("laser.wav"),
            "explosion": self.load_sound("explosion.wav"),
            "hit": self.load_sound("hit.wav"),
            "bonus": self.load_sound("bonus.wav"),
            "boss": self.load_sound("boss.wav"),
            "start": self.load_sound("start.wav"),
            "next_level": self.load_sound("next_level.wav"),
            "game_over": self.load_sound("game_over.wav")
        }

        # Background music file path
        self.music_path = os.path.join(self.base_path, "thunderbird-game-over-9232.mp3")

        # Set initial volume for sound effects based on config
        self.set_volume(EFFECTS_VOLUME)

    def load_sound(self, filename):
        """
        Load a single sound effect from a file.

        :param filename: The filename of the sound effect inside the base_path directory.
        :return: pygame.mixer.Sound object
        """

        path = os.path.join(self.base_path, filename)

        return pygame.mixer.Sound(path)

    def play_sound(self, name):
        """
        Play a sound effect by name if it is not already playing.
         Prevents overlapping the same sound repeatedly by checking active channels.

        :param name: Key of the sound effect to play.
        """

        sound = self.sounds[name]

        # Only play if sound is not already playing (no active channels)
        if sound.get_num_channels() == 0:
            sound.play()

    def play_music(self, loop = True):
        """
        Load and play background music.
        :param loop: If True, music loops indefinitely. Otherwise, plays once.
        """

        if os.path.exists(self.music_path):
            pygame.mixer.music.load(self.music_path)
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
            pygame.mixer.music.play(-1 if loop else 0)

    @staticmethod
    def stop_music():
        """
        Stop the background music playback.
        """

        pygame.mixer.music.stop()

    @staticmethod
    def pause_music():
        """
        Pause the background music playback.
        """

        pygame.mixer.music.pause()

    @staticmethod
    def resume_music():
        """
        Resume paused background music playback.
        """

        pygame.mixer.music.unpause()

    def set_volume(self, volume):
        """
        Set the volume for all sound effects.
        :param volume: Float between 0.0 (mute) and 1.0 (max volume).
        """

        for sound in self.sounds.values():
            sound.set_volume(volume)

    def mute(self):
        """
        Mute all sound effects by setting volume to 0.
        """

        self.set_volume(0)

    def unmute(self):
        """
        Restore sound effects volume to a default mid-level (0.5).
        """

        self.set_volume(EFFECTS_VOLUME)
