from turtle import Turtle
from game_specs import SCREEN_DIMENSIONS,LIVES
from high_score_manager import HighScore


class ScoreBoard(Turtle):
    """
    ScoreBoard manages game interface elements such as:
    - Player scores
    - High score tracking (persistent)
    - Player lives (shown as ship icons)
    - On-screen messages (start screen, game over, pause, transitions)
    """

    def __init__(self, screen_game, lives = LIVES):
        """
        Initializes the scoreboard.

        :param screen_game: Reference to the main game controller
        :param lives: Initial number of lives per player
        """

        super().__init__()
        self.hideturtle()
        self.speed(0)
        self.penup()
        self.color("white")

        self.screen_width = SCREEN_DIMENSIONS["width"]
        self.screen_game = screen_game

        # Load persistent high score
        self.high_score = HighScore()
        self.hi_score = self.high_score.load_high_score()

        # Player scores and lives
        self.player1_score = 0
        self.player2_score = 0
        self.player1_lives = lives
        self.player2_lives = lives

        self.player1_lives_icons = []
        self.player2_lives_icons = []

        # Layout settings
        margin_top = 470
        self.y_pos_titles = margin_top
        self.y_pos_scores = margin_top - 30
        self.x_left = -self.screen_width // 3
        self.x_center = 0
        self.x_right = self.screen_width // 3

        # Draw static and initial elements
        self.draw_static_titles()
        self.update_hi_score()
        self.update_scores()
        self.create_lives_icons()

        # Writers for various messages
        self.start_writer = None
        self.start_subtitle_writer = None
        self.game_over_writer = None
        self.reset_writer = None
        self.pause_writer = None

        self.transition_running = False  # Fade control flag

    def draw_static_titles(self):
        """
        Draws the title headers for player scores and high score.
        """

        self.clear()

        # Titles
        self.goto(self.x_left, self.y_pos_titles)
        self.write("SCORE<1>", align="center", font=("Press Start 2P", 16, "bold"))

        self.goto(self.x_center, self.y_pos_titles)
        self.write("HI-SCORE", align="center", font=("Press Start 2P", 16, "bold"))

        self.goto(self.x_right, self.y_pos_titles)
        self.write("SCORE<2>", align="center", font=("Press Start 2P", 16, "bold"))

    def create_lives_icons(self):
        """
        Updates the visual representation of remaining lives for both players using ship icons.
        """

        for icon in self.player1_lives_icons + self.player2_lives_icons:
            icon.hideturtle()
            icon.clear()

        self.player1_lives_icons.clear()
        self.player2_lives_icons.clear()

        spacing = 40
        margin_x = 20
        margin_y = 40
        y = -SCREEN_DIMENSIONS["height"] // 2 + margin_y

        # Player 1 icon (left side)
        start_x_player1 = -SCREEN_DIMENSIONS["width"] // 2 + margin_x + 30

        for i in range(self.player1_lives - 1):
            icon = Turtle()
            icon.penup()
            icon.hideturtle()
            icon.shape("images/ships/player1.gif")
            icon.shapesize(stretch_wid = 0.5, stretch_len = 0.7)
            icon.goto(start_x_player1 + i * spacing, y)
            icon.showturtle()
            self.player1_lives_icons.append(icon)

        # Player 2 icons (right side)
        start_x_player2 = SCREEN_DIMENSIONS["width"] // 2 - margin_x - (spacing * self.player2_lives) + 40

        for i in range(self.player2_lives - 1):
            icon = Turtle()
            icon.penup()
            icon.hideturtle()
            icon.shape("images/ships/player2.gif")
            icon.shapesize(stretch_wid=0.5, stretch_len=0.7)
            icon.goto(start_x_player2 + i * spacing, y)
            icon.showturtle()
            self.player2_lives_icons.append(icon)

    def update_scores(self):
        """
        Updates and redraws the current player scores and high score.
        """

        self.clear()
        self.draw_static_titles()

        # Format numbers with leading zeros
        p1 = f"{self.player1_score:04d}"
        hi = f"{self.hi_score:04d}"
        p2 = f"{self.player2_score:04d}"


        self.goto(self.x_left, self.y_pos_scores)
        self.write(p1, align="center", font=("Press Start 2P", 20, "bold"))

        self.goto(self.x_center, self.y_pos_scores)
        self.write(hi, align="center", font=("Press Start 2P", 20, "bold"))

        self.goto(self.x_right, self.y_pos_scores)
        self.write(p2, align="center", font=("Press Start 2P", 20, "bold"))

    def update_hi_score(self):
        """
        Checks and updates the high score if current scores surpass it.
        """

        new_hi = max(self.player1_score, self.player2_score, self.hi_score)

        if new_hi > self.hi_score:
            self.hi_score = new_hi
            self.high_score.save_high_score(self.hi_score)

    def update_lives(self, player, lives):
        """
        Updates the lives of a player and redraws life icons.
        :param player: 1 or 2
        :param lives: integer (new life count)
        """

        if player == 1:
            self.player1_lives = max(0, lives)

        else:
            self.player2_lives = max(0, lives)

        self.create_lives_icons()

    def set_player1_score(self, score):
        """
        Sets the score for the specified player and updates display and high score.

        param score: integer value of the player's new score
        """

        self.player1_score = score
        self.update_hi_score()
        self.update_scores()

    def set_player2_score(self, score):
        """
        Sets the score for the specified player and updates display and high score.

        :param score: integer value of the player's new score
        """

        self.player2_score = score
        self.update_hi_score()
        self.update_scores()

    def show_turn_transition(self, text, duration=2000, steps=10):
        """
        Shows a fade-out message for turn transition.

        :param text: message string
        :param duration: total duration in ms
        :param steps: number of fade steps
        """

        if self.transition_running:
            return

        self.transition_running = True

        transition = Turtle()
        transition.hideturtle()
        transition.color("white")
        transition.penup()
        transition.goto(0, 0)
        transition.write(text, align="center", font=("Press Start 2P", 20, "bold"))

        def fade_out(step=0):
            if not self.transition_running:
                transition.clear()
                return

            if step < steps:
                brightness = int(255 * (1 - (step / steps)))
                hex_color = f"#{brightness:02x}{brightness:02x}{brightness:02x}"
                transition.color(hex_color)
                self.screen.update()
                self.screen.ontimer(lambda: fade_out(step + 1), duration // steps)

            else:
                transition.clear()
                self.transition_running = False

        self.screen.update()
        self.screen.ontimer(lambda: fade_out(0), 500)

    def cancel_fade_transition(self):
        """
        Cancel the fade transition.
        """

        self.transition_running = False

    def show_start_screen(self):
        """
        Displays the game title and start prompt.
        """

        if self.start_writer is None:
            self.start_writer = Turtle()
            self.start_writer.hideturtle()
            self.start_writer.color("white")
            self.start_writer.penup()

        self.start_writer.clear()
        self.start_writer.goto(0, 0)
        self.start_writer.write("SPACE INVADERS", align="center", font=("Press Start 2P", 32, "bold"))

        if self.start_subtitle_writer is None:
            self.start_subtitle_writer = Turtle()
            self.start_subtitle_writer.hideturtle()
            self.start_subtitle_writer.penup()
            self.start_subtitle_writer.color("white")

        self.start_subtitle_writer.clear()
        self.start_subtitle_writer.goto(0, -30)
        self.start_subtitle_writer.write("Press ENTER to Start", align="center", font=("Press Start 2P", 18, "normal"))

    def clear_start_screen(self):
        """
        Clean the start screen.
        """

        if self.start_writer:
            self.start_writer.clear()
        if self.start_subtitle_writer:
            self.start_subtitle_writer.clear()

    def show_difficulty_menu(self):
        """
        Displays the difficulty selection screen.
        """

        self.clear_start_screen()
        self.start_writer.goto(0, 100)
        self.start_writer.write("SELECT DIFFICULTY", align="center", font=("Press Start 2P", 24, "bold"))

        self.start_subtitle_writer.goto(0, 0)
        self.start_subtitle_writer.write("1 - EASY\n2 - MEDIUM\n3 - HARD", align="center",
                                         font=("Press Start 2P", 18, "normal"))

    def show_game_over_screen(self):
        """
        Displays the game over screen with options to restart or exit.
        """

        self.game_over_writer = Turtle()
        self.game_over_writer.hideturtle()
        self.game_over_writer.color("white")
        self.game_over_writer.penup()
        self.game_over_writer.goto(0, 0)
        self.game_over_writer.write("GAME OVER", align="center", font=("Press Start 2P", 32, "bold"))

        self.reset_writer = Turtle()
        self.reset_writer.hideturtle()
        self.reset_writer.color("white")
        self.reset_writer.penup()
        self.reset_writer.goto(0, -50)
        self.reset_writer.write("Press ENTER to Play Again\nPress ESC to Exit", align="center",
                                  font=("Press Start 2P", 16, "normal"))

    def clear_game_over_screen(self):
        """
        Clean the game over screen.
        :return:
        """

        if self.game_over_writer:
            self.game_over_writer.clear()

        if self.reset_writer:
            self.reset_writer.clear()

    def clear_difficulty_menu(self):
        """
        Clean the difficulty menu options.
        """

        self.clear_start_screen()

    def show_pause_message(self):
        """
        Show the pause message.
        """

        if not hasattr(self, "pause_writer") or self.pause_writer is None:
            self.pause_writer = Turtle()
            self.pause_writer.hideturtle()
            self.pause_writer.color("white")
            self.pause_writer.penup()

        self.pause_writer.clear()
        self.pause_writer.goto(0, 0)
        self.pause_writer.write("PAUSED", align="center", font=("Press Start 2P", 28, "bold"))

    def clear_pause_message(self):
        if hasattr(self, "pause_writer") and self.pause_writer:
            self.pause_writer.clear()

    def reset(self):
        """
        Resets scores and life icons to initial state.
        """

        self.player1_score = 0
        self.player2_score = 0
        # self.hi_score = 0
        self.update_scores()
        self.create_lives_icons()
