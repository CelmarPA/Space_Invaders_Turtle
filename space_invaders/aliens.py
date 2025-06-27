from turtle import Turtle, Screen
from game_specs import WALLS, ALIENS, MAX_ENEMY_LASERS
from enemy_laser import EnemyLaser
from random import choice, randint, random
from explosion import Explosion


class Aliens:
    """
    Manages a group of alien enemies:
    - Handles creation and layout of alien grid
    - Controls alien movement (sideways and descending)
    - Controls alien shooting behavior and enemy lasers
    - Handles alien hit detection and removal
    """

    def __init__(self):
        """
        Initializes the alien manager:
        - Creates an empty list for aliens and their lasers
        - Loads alien images (must exist in the images folder)
        - Sets movement parameters (direction, step size, speed)
        - Initializes shooting chance and timers
        """

        self.aliens = []    # List holding active alien Turtle objects

        # Get the screen reference from a Turtle instance
        self.screen = Screen()

        # Load alien images for different alien types and boss
        self.screen.addshape("images/aliens/alien.gif")
        self.screen.addshape("images/aliens/ufo.gif")
        self.screen.addshape("images/aliens/predator.gif")
        self.screen.addshape("images/aliens/main_ship.gif")

        # Movement control variables
        self.direction = 1  # 1 mean moving right, -1 left
        self.step_x = 10  # Horizontal pixels moved per step
        self.step_y = 10  # Pixels to move down when changing direction
        self.movement_speed = 0.08  # Time between movement updates (seconds)

        self.enemy_lasers = []  # List of EnemyLaser instances currently active

        self.shooting_chance = 0.8  # Probability that an alien shoots on each shooting cycle

        # Timer IDs help manage repeated calls and cancelling timers
        self.timer_id = 0
        self.is_running = False

        self.movement_timer_id = 0
        self.shooting_timer_id = 0

    def generate_aliens(self, position, image):
        """
        CCreates one alien Turtle at the specified position with the specified image.

        Parameters:
        - position: tuple (x, y) coordinates where alien will appear
        - image: string path to the alien's GIF image

        The alien is added to the aliens list.
        """

        alien = Turtle()
        alien.hideturtle()
        alien.shape(image)
        alien.penup()
        alien.goto(position)
        alien.showturtle()

        self.aliens.append(alien)

    def generate_grid(self):
        """
        Creates a grid of aliens arranged in rows and columns.
        The type of alien image depends on the row:
        - Top rows: 'predator'
        - Middle rows: 'ufo'
        - Bottom rows: 'alien'

        Positions are calculated based on the spacing and wall limits.
        """

        # Calculate starting X coordinate so grid is centered horizontally
        start_x = -((ALIENS["cols"] - 1) * ALIENS["spacing_x"]) // 2
        # Start Y coordinate just below the top wall
        start_y = WALLS["top"] - 100     # Position just below top wall

        for row in reversed(range(ALIENS["rows"])):
            # Choose alien image depending on row number
            if row in [4, 3]:
                img = "images/aliens/alien.gif"
            elif row in [2, 1]:
                img = "images/aliens/ufo.gif"
            else:
                img = "images/aliens/predator.gif"

            for col in range(ALIENS["cols"]):
                x = start_x + col * ALIENS["spacing_x"]
                y = start_y - row * ALIENS["spacing_y"]
                self.generate_aliens((x, y), img)

    def move_aliens(self):
        """
        Moves all aliens horizontally based on current direction and step size.

        If any alien hits the horizontal boundary (near the walls),
        all aliens move down vertically and reverse horizontal direction.

        Does nothing if the alien group is not running or empty.
        """

        if not self.is_running or not self.aliens:
            return  # Avoid any movement

        should_descend = False

        # Move all aliens horizontally
        for alien in self.aliens:
            new_x = alien.xcor() + (self.step_x * self.direction)
            alien.setx(new_x)

            # Check if it hits the edges
            if new_x > WALLS["right"] - 40 or new_x < WALLS["left"] + 40:
                should_descend = True

        # If any alien touched the border, move all down and reverse direction
        if should_descend:
            self.direction *= -1
            for alien in self.aliens:
                alien.sety(alien.ycor() - self.step_y)

    def start_movement_loop(self):
        """
        Starts the movement loop using Turtle's ontimer.
        Calls move_aliens repeatedly at intervals defined by movement_speed.
        Uses movement_timer_id to ensure only the current loop runs.
        """

        if not self.is_running:
            return

        current_id = self.movement_timer_id  # Capture current timer ID

        def callback():
            # Continue only if timer ID matches and game still running
            if self.is_running and self.movement_timer_id == current_id:
                self.start_movement_loop()

        # Perform movement if timer ID unchanged
        if self.movement_timer_id == current_id:
            self.move_aliens()

        # Schedule next call after movement_speed seconds (converted to ms)
        interval = int(self.movement_speed * 1000)
        self.screen.ontimer(callback, interval)

    def alien_shoot(self):
        """
        Controls alien shooting logic:
        - Fires an enemy laser from a random alien if under max laser count.
        - Uses shooting_chance to probabilistically decide if shooting happens this cycle.
        - Calls itself repeatedly with randomized intervals to create shooting rhythm.
        """

        if not self.is_running:
            return

        current_id = self.shooting_timer_id  # Capture current timer ID

        if len(self.enemy_lasers) < MAX_ENEMY_LASERS and self.aliens:
            if random() < self.shooting_chance:
                shooter = choice(self.aliens)
                laser = EnemyLaser(shooter.position())
                self.enemy_lasers.append(laser)

        # Only continue shooting if timer ID matches and game is running
        def callback():
            if self.is_running and self.shooting_timer_id == current_id:
                self.alien_shoot()

        # Random interval between 200 and 600 ms for next shooting attempt
        interval = randint(200, 600)
        self.screen.ontimer(callback, interval)

    def update_enemy_lasers(self):
        """
        Updates all active enemy lasers:
        - Moves each laser downwards.
        - Removes lasers that are no longer active.

        Should be called repeatedly in the main game loop.
        """

        for laser in self.enemy_lasers:
            laser.move()

        # Keep only lasers still active (on screen, not collided)
        self.enemy_lasers = [l for l in self.enemy_lasers if l.active]

    def handle_alien_hit(self, alien):
        """
        Handles what happens when an alien is hit by a laser.

        - Hides the alien from the screen.
        - Marks it as inactive.
        - Removes it from the list of active aliens.

        :param alien: (Turtle) The alien turtle object
        """

        if alien in self.aliens:
            position = alien.position()     # Save position before hiding
            alien.hideturtle()
            self.aliens.remove(alien)

            # Start explosion effect
            Explosion(position, self.screen)

    def clear_lasers(self):
        """
        Clears all enemy lasers from the screen and marks them inactive.
        """

        for laser in self.enemy_lasers:
            laser.hideturtle()
            laser.active = False

        self.enemy_lasers.clear()

    def clear_aliens(self):
        """
        Hides all aliens and clears the alien list.
        """

        for alien in self.aliens:
            alien.hideturtle()

        self.aliens.clear()

    def clear_all(self):
        """
        Clears all aliens and enemy lasers from the screen and internal lists.
        """

        for alien in self.aliens:
            alien.hideturtle()
        self.aliens.clear()

        for laser in self.enemy_lasers:
            laser.hideturtle()
        self.enemy_lasers.clear()

    def start(self):
        """
        Starts alien movement and shooting loops:
        - Increments movement_timer_id to avoid old loops.
        - Sets running flag to True.
        """

        self.movement_timer_id += 1
        self.is_running = True

        self.start_movement_loop()
        self.alien_shoot()

    def reset(self):
        """
        Resets the alien group:
        - Stops existing timers.
        - Clears current aliens and lasers.
        - Generates a fresh alien grid.
        - Starts movement and shooting loops again.
        """

        self.cancel_timers()
        self.clear_all()
        self.generate_grid()
        self.start()

    def cancel_timers(self):
        """
        Stops movement and shooting loops by invalidating timer IDs
        and setting the running flag to False.
        """
        self.is_running = False
        self.movement_timer_id += 1
        self.shooting_timer_id += 1
