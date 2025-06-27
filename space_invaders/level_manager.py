from turtle import Turtle


class LevelManager:
    """
    Handles the game level system and difficulty scaling.

    - Manages level progression.
    - Displays level transition messages.
    - Adjusts alien speed and shooting chance based on difficulty.
    - Controls shield and alien reset between levels.
    """

    def __init__(self, game):
        """
        Initializes the level manager.

        :param game: Reference to the main game object (ScreenGame).
        """

        self.level = 1                  # Current level
        self.game = game                # Link to the main game
        self.label = Turtle()           # Turtle to display messages on screen
        self.label.hideturtle()
        self.label.penup()
        self.label.color("white")

        self.difficulty = None          # Difficulty level selected by the player

        self.speed_factor = 0           # Multiplier for alien movement speed
        self.shot_increment = 0         # Amount to increase alien shooting chance per level

    def next_level(self):
        """
        Advances the game to the next level.

        - Pauses the game temporarily.
        - Shows level transition message.
        - Increases difficulty based on selected mode.
        - Resets shields and aliens.
        - Resumes game after a short delay.
        """

        self.level += 1
        self.game.paused = True
        self.show_level_message()

        def resume_game():
            self.label.clear()
            self.increase_difficulty()
            self.game.reset_player_ship()
            self.restart_enemies()
            self.restart_shields()
            self.game.paused = False
            self.game.game_loop()   # Resume main loop

        # Wait 2 seconds before resuming
        self.game.screen.ontimer(resume_game, 2000)

    def show_level_message(self):
        """
        Displays a message in the center of the screen indicating the current level.
        """

        self.label.clear()
        self.label.goto(0, 0)
        self.label.write(f"LEVEL {self.level}", align="center", font=("Press Start 2P", 24, "bold"))
        self.game.screen.update()

    def increase_difficulty(self):
        """
        Gradually increases the game difficulty as levels progress,
        based on the selected difficulty setting.
        """

        if self.difficulty == "easy":
            self.speed_factor = 0.95
            self.shot_increment = 0.001

        elif self.difficulty == "medium":
            self.speed_factor = 0.9
            self.shot_increment = 0.002

        elif self.difficulty == "hard":
            self.speed_factor = 0.85
            self.shot_increment = 0.003

        self.game.aliens.movement_speed *= self.speed_factor
        self.game.aliens.shooting_chance += self.shot_increment

        # Clamp to avoid extreme values
        self.game.aliens.movement_speed = max(self.game.aliens.movement_speed, 0.05)
        self.game.aliens.shooting_chance = min(self.game.aliens.shooting_chance, 0.2)

    def set_difficulty(self, difficulty):
        """
        Applies the initial difficulty settings when the game starts.

        :param difficulty: "easy", "medium", or "hard"
        """

        self.difficulty = difficulty

        if self.difficulty == "easy":
            self.game.aliens.movement_speed = 0.3
            self.game.aliens.shooting_chance = 0.05

        elif self.difficulty == "medium":
            self.game.aliens.movement_speed = 0.2
            self.game.aliens.shooting_chance = 0.08

        elif self.difficulty == "hard":
            self.game.aliens.movement_speed = 0.12
            self.game.aliens.shooting_chance = 0.12

        self.game.sound.play_sound("start")

        # After setting, you can clear the screen and start the game
        self.game.scoreboard.clear_start_screen()
        self.game.sound.play_music()
        self.game.paused = False
        self.game.resume_turn()
        print(f"Difficulty set to {difficulty}. Starting game...")


    def restart_enemies(self):
        """
        Recreates the alien grid and clears existing lasers.
        Used when progressing to the next level.
        """

        self.game.aliens.generate_grid()
        self.game.aliens.clear_lasers()

    def restart_shields(self):
        """
        Resets the shields by clearing and regenerating them.
        Called when advancing to a new level.
        """

        self.game.shields.clear_shields()
        self.game.shields.generate_shields()
