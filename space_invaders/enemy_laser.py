from turtle import Turtle
from game_specs import WALLS, LASER_VELOCITY


class EnemyLaser(Turtle):
    """
    A class representing a laser projectile shot by an enemy alien.

    Inherits from the Turtle class and handles:
    - Appearance (color, size, direction)
    - Movement (downward)
    - Deactivation when it leaves the screen
    """

    def __init__(self, position):
        """
        Initializes an enemy laser object.

        :param position: Tuple (x, y) coordinates where the laser should start (alien position).
        """

        super().__init__()

        self.hideturtle()
        self.shape("square")
        self.color("red")       # Red color to differentiate from player laser
        self.penup()
        self.speed(0)           # Maximum drawing speed

        self.goto(position)

        # Set size of laser (thin and narrow)
        self.shapesize(stretch_wid=0.3, stretch_len=0.8)

        # Point laser down (270 degrees in turtle heading)
        self.setheading(270)

        self.showturtle()

        # Track whether the laser is still active and visible
        self.active = True

    def move(self):
        """
        Moves the laser down by a fixed velocity.
        Deactivates and hides the laser if it goes beyond the bottom wall.
        """

        if self.active:
            new_y = self.ycor() - LASER_VELOCITY       # Move down
            self.sety(new_y)

            # If the laser moves below the bottom boundary, deactivate it
            if self.ycor() < WALLS["bottom"]:
                self.active = False
                self.hideturtle()
