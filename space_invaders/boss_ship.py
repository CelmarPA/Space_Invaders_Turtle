from turtle import Turtle
from random import choice
from explosion import Explosion


class BossShip(Turtle):
    """
    A special enemy ship that occasionally appears and moves across the top of the screen.

    - Enters from either the left or right side randomly.
    - Moves in a straight line and disappears once off-screen.
    - Plays a special sound when appearing.
    - Triggers an explosion and a callback when hit.
    """

    def __init__(self, game, screen, on_destroy_callback = None):
        """
        Initializes the boss ship.

        :param game: reference to the main game (used to play sound)
        :param screen: the Turtle screen object
        :param on_destroy_callback: optional function to call when the boss is destroyed
        """
        super().__init__()

        self.game = game
        self.screen = screen
        self.on_destroy_callback = on_destroy_callback

        # Load and set the boss ship image
        self.screen.addshape("images/aliens/main_ship.gif")
        self.shape("images/aliens/main_ship.gif")

        self.penup()
        self.speed(0)       # Fastest turtle speed
        self.hideturtle()
        self.goto(10000, 10000)      # Position far offscreen initially

        self.active = False         # Whether the boss is currently on-screen
        self.moving_right = True    # Movement direction flag

    def appear(self):
        """
        Makes the boss ship appear on-screen.
        - Randomly chooses whether to enter from the left or right side.
        - Moves horizontally across the top of the screen.
        - Plays a sound effect when it appears.
        """

        if self.active:
            return      # Already on screen

        self.active = True
        self.moving_right = choice([True, False])

        # Y-position near the top of the screen
        y = self.screen.window_height() // 2 - 40

        # X-position just outside the left or right screen edge
        x = -self.screen.window_width() // 2 - 100 if self.moving_right else self.screen.window_width() // 2 + 100
        self.goto(x, y)
        self.showturtle()

        self.game.sound.play_sound("boss")      # Play boss appearance sound
        self.move()     # Start movement loop

    def move(self):
        """
        Moves the boss ship horizontally in the chosen direction.
        - If it moves off-screen, it disappears.
        - Otherwise, continues moving using ontimer.
        """

        if not self.active:
            return

        step = 5 if self.moving_right else - 5
        self.setx(self.xcor() + step)

        # Check if boss ship has exited the screen
        if (self.moving_right and self.xcor() > self.screen.window_width() // 2 + 100) or \
                (not self.moving_right and self.xcor() < - self.screen.window_width() // 2 - 100):
            self.disappear()

        else:
            # Continue movement every 20 milliseconds
            self.screen.ontimer(self.move, 20)

    def disappear(self):
        """
        Hides the boss ship and marks it as inactive.
        Called when it leaves the screen or is destroyed.
        """

        self.hideturtle()
        self.active = False

    def handle_hit(self):
        """
        Called when the boss ship is hit by a laser:
        - Plays an explosion effect at the current position.
        - Hides the boss and marks it inactive.
        - Executes the destruction callback (e.g., add bonus points).
        """

        Explosion(self.position(), self.screen)
        self.disappear()

        if self.on_destroy_callback:
            self.on_destroy_callback()

    def reset(self):
        """
       Forces complete deactivation and relocation of the boss ship.
        Ensures it's fully off-screen and inactive (used when restarting game).
       """
        self.active = False
        self.hideturtle()
        self.goto(10000, 10000)  # Ensure it's off the visible area and out of collision range
