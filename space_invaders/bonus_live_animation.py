from turtle import Turtle


class BonusLifeAnimation(Turtle):
    """
    Displays a short animation and message when the player earns an extra life.

    Shows:
    - A bonus life icon image above the player's ship.
    - The text "1UP" just below the icon.
    - Plays a bonus sound effect.

    After a short delay, the animation and label are cleared.
    """

    def __init__(self, game, position, image_path, screen):
        """
        Initialize the bonus life animation.
        :param game: Reference to the main game object (for sound).
        :param position: Tuple (x, y) for where to show the animation (above ship).
        :param image_path: Path to the image (.gif) to be displayed.
        :param screen: The main Turtle screen instance.
        """

        super().__init__()

        self.game = game

        self.screen = screen
        self.penup()
        self.hideturtle()

        # Try to register the image shape if not already registered
        try:
            self.screen.addshape(image_path)

        except Exception as e:
            print(e)
            pass    # If already added, this will raise an exception we ignore

        # Set shape to the bonus image and move to target position
        self.shape(image_path)
        self.goto(position)
        self.showturtle()       # Show the bonus life icon

        # Create a label for "1UP" text below the image
        self.label = Turtle()
        self.label.hideturtle()
        self.label.penup()
        self.label.color("lime")
        self.label.goto(position[0], position[1] - 25)
        self.label.write("1UP", align="center", font=("Press Start 2P", 10, "normal"))

        # Play sound for bonus life
        self.game.sound.play_sound("bonus")

        # Schedule animation to clear after 1000ms (1 second)
        self.screen.ontimer(self.clear_animation, 1000)

    def clear_animation(self):
        """
        Clears the bonus icon and the "1UP" label from the screen.
        Called automatically after a delay.
        """

        self.hideturtle()
        self.label.clear()
        self.label.hideturtle()
