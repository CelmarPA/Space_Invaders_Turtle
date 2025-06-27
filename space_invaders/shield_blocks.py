from turtle import Turtle
from random import choice, randint
from game_specs import SCREEN_DIMENSIONS, WALLS, NUM_SHIELDS, BLOCK_SIZE


class ShieldBlock(Turtle):
    """
    Represents an individual block of a shield.

    Each block has a "life" (hp) that decreases with damage.
    As it takes damage, it changes color and disappears when its health is zero.
    """

    def __init__(self, position, size, screen):
        """
        Initialize a ShieldBlock instance.

        Sets up the turtle shape, size, color, position, and health.

        :param position: Tuple (x, y) specifying the block's initial position on the screen.
        :param size: Tuple (width, height) for the size of the block in pixels.
        :param screen: Reference to the turtle Screen instance, used for scheduling animation timers.
        """

        super().__init__()

        self.screen = screen        # Store screen reference for event scheduling

        self.penup()                # Disable drawing lines when moving
        self.shape("square")        # Use square shape to represent block
        self.color("green")         # Initial color indicating full health

        # Set the shape size by scaling the default 20x20 pixel square shape
        self.shapesize(stretch_wid=size[1] / 20, stretch_len=size[0] / 20)

        self.goto(position)         # Move block to initial position on screen

        self.active = True          # Indicates if the block is alive/visible
        self.hp = 3         # Starting health points of the block

    def take_damage(self):
        """
        Decrease the block's hp by 1 and update its state accordingly.

        Changes color based on remaining hp:
            3 hp: green (full health)
            2 hp: yellow (damaged)
            1 hp: red (critically damaged)
            0 or less: block disappears and becomes inactive
        Also triggers a brief damage visual effect.
        """

        self.hp -= 1

        self.show_damage_effect()

        if self.hp == 2:
            self.color("yellow")

        elif self.hp == 1:
            self.color("red")

        elif self.hp <= 0:
            self.active = False
            self.hideturtle()

    def show_damage_effect(self):
        """
        Display a brief white particle effect at the block's position to visualize damage.

        Creates a small white circle turtle, shows it briefly, then removes it using a timer.
        """

        particle = Turtle()
        particle.penup()
        particle.hideturtle()
        particle.shape("circle")
        particle.color("white")
        particle.shapesize(0.2)             # Small particle size
        particle.goto(self.position())      # Position particle on the block
        particle.showturtle()

        def remove():
            particle.hideturtle()
            particle.clear()

        self.screen.ontimer(remove, 200)


class ShieldGenerator:
    """
    Manages multiple ShieldBlock instances, arranging them into shields on screen.

    Responsible for creating shields in patterns, checking collisions with lasers and aliens,
    and resetting/clearing shields.
    """

    def __init__(self, screen, num_shields = NUM_SHIELDS):
        """
        Initialize the ShieldGenerator.
        :param screen: Turtle Screen reference to draw and manage blocks.
        :param num_shields: Number of shields to generate horizontally.
        """

        self.screen = screen
        self.blocks = []                # List to keep track of all ShieldBlock instances
        self.num_shields = num_shields

        self.block_size = BLOCK_SIZE    # Size of each individual block (square) in pixels

        self.generate_shields()         # Create shields on initialization

    def generate_shields(self):
        """
        Generate multiple shields spaced evenly across the screen width.

        For each shield:
          - Calculate horizontal center position
          - Generate a random pattern of blocks
          - Create and position ShieldBlock instances accordingly
        """

        spacing = SCREEN_DIMENSIONS["width"] // (self.num_shields + 1)
        y = WALLS["bottom"] + SCREEN_DIMENSIONS["height"] * 0.25        # Vertical position for shields

        for i in range(self.num_shields):
            x_center = -SCREEN_DIMENSIONS["width"] // 2 + (i + 1) * spacing
            pattern = self.random_pattern()
            self.create_pattern_blocks(pattern, x_center, y)

    @staticmethod
    def random_pattern():
        """
        Generate a random 2D pattern matrix representing block presence in a shield.
        Width and height of the pattern are randomly chosen to add variety to shields.

        :return: A list of lists of 0s and 1s, where 1 indicates a block should be created.
        """

        pattern = []
        width = randint(3, 6)
        height = randint(2, 4)

        for _ in range(height):
            row = [choice([0, 1]) for _ in range(width)]
            pattern.append(row)

        return pattern

    def create_pattern_blocks(self, pattern, x_center, y_bottom):
        """
        Create ShieldBlock instances according to the pattern matrix, positioning them centered around x_center.

        :param pattern: 2D list of 0s and 1s representing block layout.
        :param x_center: The x-coordinate center for the shield.
        :param y_bottom: The y-coordinate of the bottom row of the shield.
        :return:
        """

        for row_index, row in enumerate(pattern):
            for col_index, cell in enumerate(row):
                if cell:
                    # Calculate block position based on column, row, block size and center offset
                    x = x_center + (col_index - len(row) // 2) * self.block_size
                    y = y_bottom + (len(pattern) - row_index) * self.block_size

                    block = ShieldBlock((x, y), (self.block_size, self.block_size), self.screen)
                    self.blocks.append(block)

    def check_collision(self, lasers):
        """
        Check for collisions between laser objects and shield blocks.

        When a collision is detected:
          - The block takes damage
          - The laser is deactivated and hidden

        :param lasers: Iterable of laser objects, each must have 'distance()' and 'active' attribute.
        """

        for laser in lasers:
            for block in self.blocks:
                if block.active  and laser.distance(block) < 15:
                    block.take_damage()
                    laser.active = False
                    laser.hideturtle()

    def check_collision_with_aliens(self, aliens):
        """
         Check for collisions between aliens and shield blocks.
         When a collision is detected, the block takes damage.

        :param aliens: Iterable of alien objects, each must have 'distance()' method.
        """

        for alien in aliens:
            for block in self.blocks:
                if block.active and block.distance(alien) < self.block_size:
                    block.take_damage()

    def clear_shields(self):
        """
        Remove all shield blocks from the screen and clear the blocks list.
        """

        for block in self.blocks:
            block.hideturtle()

        self.blocks.clear()

    def reset(self):
        """
        Clear existing shields and regenerate new shields with fresh blocks.
        """

        self.clear_shields()
        self.generate_shields()
