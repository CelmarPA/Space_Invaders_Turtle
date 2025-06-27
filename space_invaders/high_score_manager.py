import json
import os

HIGH_SCORE_DIR = "high_score"
HIGH_SCORE_FILE = os.path.join(HIGH_SCORE_DIR, "high_score.json")


class HighScore:
    """
    A class responsible for loading and saving the high score of the game.

    - Saves the high score to a JSON file.
    - Loads it safely with default fallback.
    - Automatically creates the directory if it does not exist.
    """

    def __init__(self):
        """
        Initializes the high score system.

        - Sets up the directory and file path.
        - Ensures the directory exists before reading/writing.
        """

        self.dir = HIGH_SCORE_DIR
        self.path = HIGH_SCORE_FILE

        self.ensure_directory_exists()


    def ensure_directory_exists(self):
        """
        Ensures that the directory for saving the high score exists.
        Creates it if it doesn't.
        """
        os.makedirs(self.dir, exist_ok = True)

    def load_high_score(self):
        """
        Loads the high score from a JSON file.

        Returns:
        - The stored high score (int), or 0 if the file doesn't exist or is invalid.
        """

        if os.path.exists(self.path):
            with open(self.path, "r") as file:
                try:
                    data = json.load(file)
                    return data.get("high_score", 0)     # Return saved score, or 0 if not found

                except json.JSONDecodeError:
                    return 0         # If file is corrupt or empty, default to 0

        return 0        # If file doesn't exist

    def save_high_score(self, score):
        """
        Saves the given high score to the JSON file.
        This will overwrite any existing data in the file.

        :param score: Integer score to be saved.
        """

        with open(self.path, 'w') as file:
            try:
                json.dump({"high_score": score}, file)

            except json.JSONDecodeError:
                return      # In practice, writing shouldn't trigger this unless system is unstable
