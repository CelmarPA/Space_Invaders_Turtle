from turtle import Turtle
from game_specs import WALLS, LASER_VELOCITY

class Laser(Turtle):
    """
    Laser class represents a projectile fired by the player's spaceship.

    Inherits from the Turtle class to take advantage of graphical rendering
    and movement functions. The laser moves upward and is deactivated when
    it goes off-screen.
    """

    def __init__(self, position):
        """
        Initializes the Laser object at the given position.

        :param position: Tuple (x, y) where the laser starts (usually the player's ship location).
        """

        super().__init__()

        # Set up basic laser appearance and behavior
        self.hideturtle()
        self.shape("square")        # Default shape for the laser
        self.color("green")         # Green to differentiate from enemy lasers
        self.penup()                # Prevent drawing lines
        self.speed(0)               # Fastest possible rendering
        self.goto(position)         # Set laser's starting position
        self.shapesize(stretch_wid=0.3, stretch_len=0.8)        # Make laser thin and narrow
        self.setheading(90)         # Point laser upward (90 degrees)
        self.showturtle()

        self.active = True         # Flag indicating whether the laser is still in play

    def move(self):
        """
        Moves the laser upward on the screen.

        - Increases the laser's y-coordinate by a fixed amount.
        - If the laser exceeds the top wall limit, it becomes inactive and is hidden.
        """

        if self.active:
            # Move the laser upward by LASER_VELOCITY
            new_y = self.ycor() + LASER_VELOCITY
            self.sety(new_y)

            # Check if the laser has gone off-screen (above top boundary)
            if self.ycor() > WALLS["top"]:
                self.active = False
                self.hideturtle()      # Hide the laser from the screen
