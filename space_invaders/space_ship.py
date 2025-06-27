from turtle import Turtle
from game_specs import SCREEN_DIMENSIONS, WALLS, LIVES
from laser import Laser
from explosion import Explosion
from time import time

class SpaceShip(Turtle):
    """
    SpaceShip class represents the player's spaceship in the game.
    Inherits from Turtle and handles movement, shooting, and user input.
    """

    def __init__(self, game, position, screen):
        """
        Initializes the spaceship at the given position.
        :param position: (tuple) Starting (x, y) coordinates of the spaceship.
        """
        super().__init__()

        self.game  = game

        screen_w = SCREEN_DIMENSIONS["width"]
        screen_h = SCREEN_DIMENSIONS["height"]
        self.bottom_margin = SCREEN_DIMENSIONS["height"] * 0.15

        # Register custom ship image
        self.screen = screen
        self.screen.addshape("images/ships/player1.gif")
        self.screen.addshape("images/ships/player2.gif")

        self.shape("images/ships/player1.gif")
        self.penup()
        self.speed(0)
        self.goto(position)

        # Size is proportional to screen dimensions
        self.ship_width = screen_w * 0.12        # 12% of screen width
        self.ship_height = screen_h * 0.015      # 1.5% of screen height
        stretch_len = self.ship_width / 20       # Base turtle size is 20x20
        stretch_wid = self.ship_height / 20

        self.shapesize(stretch_wid = stretch_wid, stretch_len = stretch_len)

        # Flags to control movement
        self.moving_right = False
        self.moving_left = False

        self.lasers = []                    # List of active laser shots
        self.shooting = False               # Continuous shooting flag
        self.shoot_loop_active = False      # To prevent multiple parallel shoot loops

        self.lives = LIVES
        self.score = 0

        self.points_since_last_life = 0

        self.update_loop_active = False

        self.last_shot_time = 0
        self.shot_cooldown = 1.5

    # ----- Movement Control -----

    def start_moving_right(self):
        """
        Start moving the ship to the right.
        """

        self.moving_right = True

    def start_moving_left(self):
        """
        Start moving the ship to the left.
        """

        self.moving_left = True

    def stop_moving_right(self):
        """
        Stop moving the ship to the right.
        """

        self.moving_right = False

    def stop_moving_left(self):
        """
        Stop moving the ship to the left.
        """

        self.moving_left = False

    def go_right(self):
        """
        Moves the ship to the right by a fixed step,
        making sure it does not go beyond the right wall.
        """

        new_x = self.xcor() + 20
        if new_x <= WALLS["right"] - (self.ship_width / 2):
            self.goto(new_x, self.ycor())

    def go_left(self):
        """
        Moves the ship to the left by a fixed step,
        making sure it does not go beyond the left wall.
        """

        new_x = self.xcor() - 20
        if new_x >= WALLS["left"] + (self.ship_width / 2):
            self.goto(new_x, self.ycor())

    # ----- Shooting Control -----

    def start_shooting(self):
        """
        Starts continuous shooting loop if not already active.
        """

        if not self.shooting:
            self.shooting = True
            self.shoot_loop_active = True
            self.shoot_loop()

    def stop_shooting(self):
        """
        Stops the shooting loop.
        """

        self.shooting = False
        self.shoot_loop_active = False

    def fire(self):
        """
        Creates a bullet at the current position of the ship.

        :return: Returns the newly created Bullet.
        """

        current_time = time()

        if not any(l.active for l in self.lasers) or (current_time - self.last_shot_time >= self.shot_cooldown):
            self.last_shot_time = current_time
            x, y = self.position()
            laser_y = y + (self.ship_height / 2) + 20
            laser = Laser((x, laser_y))
            self.lasers.append(laser)
            self.game.sound.play_sound("laser")

    def shoot_loop(self):
        """
        Controls repeated laser firing while shooting is active.
        Fires a shot and schedules the next fire after a delay.
        """

        if self.shooting:
            self.fire()
            self.screen.ontimer(self.shoot_loop, 100)

        else:
            self.shoot_loop_active = False

    # ----- Update Methods -----

    def update_ship(self):
        """
        Updates the ship's position based on its current movement direction.
        Checks if the ship is flagged as moving right or left,
        and moves it accordingly. Then schedules the next update call.

        This method is repeatedly called every 20 milliseconds
        to smoothly animate the ship movement.
        """

        if self.update_loop_active:
            return

        self.update_loop_active = True

        def loop():
            # If the ship is set to move right, move it right
            if self.moving_right:
                self.go_right()

            # If the ship is set to move left, move it left
            if self.moving_left:
                self.go_left()

            self.screen.ontimer(loop, 20)

        loop()

        # Schedule the next ship update call after 20 milliseconds
        self.screen.ontimer(self.update_ship, 20)

    def update_lasers(self):
        """
        Updates all active lasers, moving them forward.
        Removes inactive lasers from the list.
        """

        for laser in self.lasers:
            laser.move()

        self.lasers = [l for l in self.lasers if l.active]

    def move_ship(self):
        """
        Binds keyboard inputs to control ship movement and shooting.

        - Binds arrow keys and 'a'/'d' keys to start and stop moving the ship left or right.
        _ Binds space key to start and stop shooting.
        """

        self.screen.listen()

        # Right movement
        self.screen.onkeypress(self.start_moving_right, "Right")
        self.screen.onkeyrelease(self.stop_moving_right, "Right")
        self.screen.onkeypress(self.start_moving_right, "d")
        self.screen.onkeyrelease(self.stop_moving_right, "d")

        # Left movement
        self.screen.onkeypress(self.start_moving_left, "Left")
        self.screen.onkeyrelease(self.stop_moving_left, "Left")
        self.screen.onkeypress(self.start_moving_left, "a")
        self.screen.onkeyrelease(self.stop_moving_left, "a")

        # Shooting
        self.screen.onkeypress(self.start_shooting, "space")
        self.screen.onkeyrelease(self.stop_shooting, "space")

    def handle_hit(self):
        """
        Handles the event when the player's ship is hit by an enemy laser.
        - Decreases life.
        - Updates visual life counter.
        - Checks for game over.
        """

        position = self.position()

        # Start explosion effect
        Explosion(position, self.screen)

        # Decrease life count
        self.lives -= 1
        # self.scoreboard.update_lives(self.lives)

        # Play sound
        self.game.sound.play_sound("hit")

        # Reset ship position (e.g., to center)
        self.reset_ship_position()

    def clear_lasers(self):
        for laser in self.lasers:
            laser.hideturtle()
            laser.active = False

        self.lasers.clear()

    def reset_ship_position(self):
        self.goto(0, WALLS["bottom"] + self.bottom_margin)

        for laser in self.lasers:
            laser.hideturtle()
            laser.active = False

        self.lasers.clear()

    def stop_moving(self):
        self.moving_left = False
        self.moving_right = False
        self.shooting = False
