from turtle import Turtle


class Explosion(Turtle):
    """
    A simple animated explosion effect using a sequence of .gif images.

    - Plays a short animation at the given position.
    - Each frame is shown in sequence with a short delay.
    - Automatically hides itself after the animation ends.
    """

    def __init__(self, position, screen):
        """
        Initializes the explosion animation.

        :param position: Tuple (x, y) where the explosion should appear.
        :param screen: Reference to the Turtle screen object.
        """

        super().__init__()

        self.screen = screen

        # Sequence of explosion image frames (must exist in the images' folder)
        self.frames = [
            "images/explosions/explosion1.gif",
            "images/explosions/explosion2.gif",
            "images/explosions/explosion3.gif",
            "images/explosions/explosion4.gif"
        ]

        # Register all frames with the Turtle screen
        for frame in self.frames:
            self.screen.addshape(frame)

        self.index = 0      # Index of the current frame
        self.hideturtle()
        self.penup()
        self.goto(position)

        # Set the initial frame and show the explosion
        self.shape(self.frames[self.index])
        self.showturtle()

        # Start the animation
        self.play_animation()

    def play_animation(self):
        """
        Plays the explosion animation by cycling through frames.
        Uses a timer to schedule the next frame every 100ms.
        """

        self.index += 1

        # Continue to next frame if available
        if self.index < len(self.frames):
            self.shape(self.frames[self.index])
            self.screen.ontimer(self.play_animation, 100)   # 100ms between frames

        else:
            self.hideturtle()       # End of animation, hide explosion

    def clear(self):
        """
        Forces the explosion to disappear immediately.
        Useful if the screen is being reset or cleared.
        """

        self.hideturtle()
        self.screen.update()
