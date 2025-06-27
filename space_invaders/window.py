# Libraries
import turtle
from turtle import Screen, hideturtle
from numpy.random import randint
from game_specs import SCREEN_DIMENSIONS, WALLS, LIVES, BONUS_LIFE_THRESHOLD, MAX_LIVES, POINTS_PER_ENEMY, BOSS_BONUS_POINTS
from space_ship import SpaceShip
from aliens import Aliens
from check_hit import CheckHit
from scoreboard import ScoreBoard
from shield_blocks import ShieldGenerator
from explosion import Explosion
from bonus_live_animation import BonusLifeAnimation
from level_manager import LevelManager
from boss_ship import BossShip
from sound_manager import SoundManager


class ScreenGame:
    """
    Main class responsible for setting up and managing the entire game:
    - Initializes the game screen, player ships, alien waves, shields, sounds
    - Manages game loop, collisions, level progression, score, pause, and transitions
    - Controls turn-based logic for two players
    """

    def __init__(self):
        """
        Initializes the main game window, ships, scoreboard, enemies, sounds,
        and sets up input bindings.
        """

        # Set up the main Turtle screen and hide default turtle
        self.screen = Screen()
        hideturtle()
        self.canvas = self.screen.getcanvas()
        self.root = self.canvas.winfo_toplevel()

        # Define bottom margin as 5% of screen height, for ship placement
        self.bottom_margin = SCREEN_DIMENSIONS["height"] * 0.15

        # Game sound
        self.sound = None

        # Players ships
        self.player1_ship = None
        self.player2_ship = None
        self.active_ship = None

        # Players scores
        self.player1_score = None
        self.player2_score = None
        self.active_score = None

        # Boss ship, aliens end shields
        self.boss_ship = None
        self.aliens = None
        self.shields = None

        # Scoreboard and level manager
        self.scoreboard = None
        self.level_manager = None

        # Game is not paused initially and not started
        self.paused = False
        self.started = False

        # Configure the screen settings (size, background, event bindings)
        self.screen_config()

    def screen_config(self):
        """
        Configures the window and all game elements. This includes loading ships,
        aliens, shields, and scoreboard, and setting up key bindings.
        """

        # Set up the screen size using predefined width and height constants
        self.screen.setup(width = SCREEN_DIMENSIONS["width"], height = SCREEN_DIMENSIONS["height"])

        # Set the background color of the game screen to black
        self.screen.bgcolor("black")

        # Set the window title to "Space Invaders"
        self.screen.title("Space Invaders")

        # Turn off automatic screen updates for manual control (for smoother animations)
        self.screen.tracer(0)
        self.root.configure(bg = "black")
        self.canvas.place(x = 0, y = 0, width = SCREEN_DIMENSIONS["width"], height = SCREEN_DIMENSIONS["height"])

        # Center the canvas within the root window (custom method)
        self.center_canvas()

        # Bind the root window resize event to a handler for dynamic canvas resizing
        self.root.bind("<Configure>", self.on_resize)

        # Calculate the starting Y position for the ship based on the bottom wall and margin
        start_y = WALLS["bottom"] + self.bottom_margin

        # Sound Manager
        self.sound = SoundManager()

        # Create player ships
        self.player1_ship = SpaceShip(self, (0, start_y), self.screen)     # Initialize the ship object at the calculated position
        self.player2_ship = SpaceShip(self, (0, start_y), self.screen)
        self.player2_ship.hideturtle()
        self.active_ship = self.player1_ship

        # Scoreboard and initial score assignments
        self.scoreboard = ScoreBoard(self)
        self.active_score = self.player1_score

        # Aliens and shields
        self.aliens = Aliens()
        self.aliens.reset()
        self.shields = ShieldGenerator(self.screen)

        # Level Manager
        self.level_manager = LevelManager(self)

        # Boss ship with callback on destroy
        self.boss_ship = BossShip(self, self.screen, on_destroy_callback = self.boss_destroyed)
        self.schedule_boss_appearance()

        # Enable the screen to listen for keyboard events
        self.screen.listen()

        # Start the ships movement handler
        self.enable_controls_for_active_ship()

        self.paused = True
        self.scoreboard.show_start_screen()
        self.screen.onkey(self.start_game, "Return")

        # Call game loop()
        self.game_loop()

    def enable_controls_for_active_ship(self):
        """
        Enable movement and update loop for the current player's ship
        """

        self.active_ship.move_ship()
        self.active_ship.update_ship()

    def switch_player(self):
        """
        Switch to the next player (from Player 1 to Player 2),
        resetting aliens, shields, and player ship.
        """

        # Cancel and clean the turtle objets
        self.aliens.cancel_timers()
        self.aliens.clear_lasers()
        self.aliens.clear_aliens()
        self.shields.clear_shields()

        # Pause the game and remove Player1_ship
        self.paused = True
        self.active_ship.hideturtle()
        self.active_ship.clear_lasers()
        self.active_ship.stop_moving()

        # Define active_ship as Player2_ship
        if self.active_ship == self.player1_ship:
            self.active_ship = self.player2_ship
            self.active_score = self.scoreboard.player2_score

            # Define the image for the ship then show it
            self.player2_ship.shape("images/ships/player2.gif")
            self.player2_ship.reset_ship_position()
            self.player2_ship.showturtle()
            self.player2_ship.stop_moving()

            # Show the message transition turn for 2 seconds
            self.scoreboard.show_turn_transition("PLAYER 2 TURN")
            self.screen.update()

            self.screen.ontimer(self.start_player2_turn, 2000)

        else:
            self.end_game()  # Ends the game if all lives of the 2 player ended

    def start_player2_turn(self):
        """
        Set up level, aliens and shields for player 2
        """
        self.level_manager.level = 1
        self.aliens.reset()
        self.shields.reset()
        self.resume_turn()

    def center_canvas(self):
        """
        Centers the canvas within the root window.

        - Calculates the horizontal and vertical position to place the canvas
          so that it is centered based on the current size of the root window.
        - Uses integer division (//) to avoid floating-point positions.
        - Applies the calculated position using the `place()` geometry manager.
        """

        # Get the current width and height of the root window
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()

        # Calculate the top-left (x, y) coordinates to center the canvas
        x = (root_width -  SCREEN_DIMENSIONS["width"]) // 2
        y = (root_height - SCREEN_DIMENSIONS["height"]) // 2

        # Move the canvas to the calculated position
        self.canvas.place(x = x, y = y)

    def game_loop(self):
        """
        Main game loop that updates the game state and screen.

        - Runs only if the game is not paused.
        - Updates the screen graphics.
        - Moves the ship and checks for collisions with alien's ships or laser.
        - Checks if all alien's ships are cleared to progress to the next level.
        - Plays a sound effect when advancing levels (if sounds are enabled).
        - Pauses the game and waits to start the next turn when level is cleared.
        - Schedules the next loop iteration after 20 milliseconds.
        """

        # Continue the game loop only if the game is not paused
        if not self.paused and self.canvas.winfo_exists():
            try:
                # Update the screen display (manual control because tracer is off)
                self.screen.update()
                self.active_ship.update_lasers()
                self.aliens.update_enemy_lasers()
                self.check_player_hit()
                self.check_enemy_hit()
                self.shields.check_collision(self.active_ship.lasers)
                self.shields.check_collision(self.aliens.enemy_lasers)
                self.shields.check_collision_with_aliens(self.aliens.aliens)
                self.check_laser_collisions()
                self.check_boss_hit()

                # Change the game level
                if not self.aliens.aliens and not self.paused:
                    self.paused = True
                    self.sound.play_sound("next_level")
                    self.level_manager.next_level()

            except turtle.TurtleGraphicsError:
                return

        self.screen.ontimer(self.game_loop, 20)

    def on_resize(self, event):
        """
        Handles window resize events by scheduling the actual resize handler.

        - This method is called whenever the window is resized.
        - It defers execution of the resize handling by 10 milliseconds
          to avoid rapid repeated calls during continuous resizing.
        - The actual resize logic is executed in the 'handle_resize' method.

        :param event: (event) The resize event object passed by the window manager.
        """
        # Store the event (though currently unused in this snippet)
        _event = event

        # Schedule the handle_resize method to run after 10 milliseconds
        self.root.after(10, self.handle_resize)

    def handle_resize(self):
        """
        Handles adjustments needed after the window resize event.

        - Updates any pending tasks related to the root window.
        - Retrieves the current width and height of the root window.
        - Centers the canvas within the window.
        - Changes the root window background color to white if
          the window exceeds the predefined screen dimensions,
          otherwise sets it to black.
        """

        # Process any pending events and updates for the root window
        self.root.update_idletasks()

        # Get the current width and height of the root window
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()

        # Center the canvas within the resized window
        self.center_canvas()

        # Change background color based on window size relative to screen dimensions
        if root_width > SCREEN_DIMENSIONS["width"] or root_height > SCREEN_DIMENSIONS["height"]:
            self.root.configure(bg = "white")

        else:
            self.root.configure(bg = "black")

    def toggle_pause(self):
        """
        Toggles the game's pause state.

        - Switches the 'paused' flag between True and False.
        - If the game is paused:
            - Updates the scoreboard to show paused state.
            - Updates the screen once to reflect the pause.
        - If the game is unpaused:
            - Updates the scoreboard to show active state.
            - Restarts the main game loop.
        """

        # Flip the paused state (True becomes False, False becomes True)
        self.paused = not self.paused

        if self.paused:
            self.scoreboard.show_pause_message()
            self.sound.pause_music()  # Pause music
            # Notify scoreboard that the game is paused (e.g., show pause message)
            self.screen.update()    # Update screen to reflect pause state

        else:
            # Restart the main game loop to continue gameplay
            self.sound.resume_music()  # Resume music
            self.scoreboard.clear_pause_message()
            self.game_loop()

    def resume_turn(self):
        """
        Resumes the current player's turn by reactivating enemy logic and movement.
        """

        self.aliens.is_running = True
        self.aliens.movement_timer_id += 1
        self.aliens.shooting_timer_id += 1
        self.aliens.start()

        self.enable_controls_for_active_ship()
        self.paused = False
        self.screen.update()

    def schedule_boss_appearance(self):
        """
        Schedule the random appearance of the ship's boss (boss).
        """

        interval = randint(15000, 30000)    # Between 15 and 30 seconds
        self.screen.ontimer(self.trigger_boss_appearance, interval)

    def trigger_boss_appearance(self):
        """
        Shows the boss ship if it is not active.
        """

        if not self.boss_ship.active:
            self.boss_ship.appear()

        # Reschedule next appearance
        self.schedule_boss_appearance()

    def boss_destroyed(self):
        """
        Logic executed when the flagship is destroyed.
        """

        bonus_points = BOSS_BONUS_POINTS
        self.active_ship.score += bonus_points
        self.update_active_player_score()

    def check_player_hit(self):
        """
        Check if the active player's ship is hit by any enemy lasers.

        Collision detection uses a threshold based on the ship's width (quarter of the ship width).
        When a hit occurs:
        - The laser is deactivated and hidden.
        - The ship's hit handling method is called (to reduce life, play effects, etc.).
        - The scoreboard updates the player's remaining lives.
        - If lives reach zero, the active player is switched.
        """

        hits = CheckHit.check_lasers_vs_targets(
            lasers = self.aliens.enemy_lasers,
            targets = [self.active_ship],
            threshold = self.active_ship.ship_width / 4
        )

        for laser, ship in hits:
            laser.active = False                # Deactivate the laser on hit
            laser.hideturtle()                  # Hide the laser graphic
            self.active_ship.handle_hit()       # Reduce life and handle hit effects
            self.scoreboard.update_lives(       # Update the visual lives indicator
                player = 1 if self.active_ship == self.player1_ship else 2,
                lives = self.active_ship.lives
            )

            if self.active_ship.lives <= 0:
                self.switch_player()            # Switch turns if no lives remain


    def check_enemy_hit(self):
        """
        Check if any enemy aliens are hit by the active player's lasers.

        For each hit:
        - Deactivate and hide the laser.
        - Remove the alien from the alive list.
        - Play explosion sound.
        - Update the active player's score.
        """

        hits = CheckHit.check_lasers_vs_targets(
            lasers = self.active_ship.lasers,
            targets = self.aliens.aliens,
        )

        for laser, alien in hits:
            laser.active = False
            laser.hideturtle()
            self.aliens.handle_alien_hit(alien)     # Remove alien from alive list

            self.sound.play_sound("explosion")

            self.update_active_player_score()

    def check_laser_collisions(self):
        """
        Check for collisions between player lasers and enemy lasers.

        When two lasers collide:
        - Both lasers are deactivated and hidden.
        - Explosion sound is played.
        - An explosion animation is created at the midpoint of the collision.
        """

        hits = CheckHit.check_laser_vs_laser(
            player_lasers = self.active_ship.lasers,
            enemy_lasers = self.aliens.enemy_lasers
        )

        for player_laser, enemy_laser in hits:
            x_p, y_p = player_laser.position()
            x_e, y_e = enemy_laser.position()
            mid_x = (x_p + x_e) / 2
            mid_y = (y_p + y_e) / 2

            position = (mid_x, mid_y)

            player_laser.active = False
            enemy_laser.active = False
            player_laser.hideturtle()
            enemy_laser.hideturtle()

            self.sound.play_sound("explosion")

            Explosion(position, self.screen)

    def check_boss_hit(self):
        """
        Check if the boss ship is hit by the active player's lasers.

        If the boss is active and hit:
        - Deactivate and hide the laser.
        - Play explosion sound.
        - Call the boss's hit handler (which may reduce boss life or trigger effects).
        """

        if not self.boss_ship.active:
            return      # No boss active, skip checking

        hits = CheckHit.check_lasers_vs_targets(
            lasers = self.active_ship.lasers,
            targets = [self.boss_ship],
        )

        for laser, _ in hits:
            laser.active = False
            laser.hideturtle()

            self.sound.play_sound("explosion")

            self.boss_ship.handle_hit()

    def update_active_player_score(self):
        """
        Update the active player's score when an enemy is destroyed.

        - Adds a fixed number of points per enemy.
        - Accumulates points since last extra life.
        - Updates the scoreboard display for the correct player.
        - Awards an extra life if points exceed the bonus threshold, capped by MAX_LIVES.
        - Shows a bonus life animation above the ship on life gain.
        """

        points = POINTS_PER_ENEMY

        self.active_ship.score += points
        self.active_ship.points_since_last_life += points

        if self.active_ship == self.player1_ship:
            self.scoreboard.set_player1_score(self.active_ship.score)
            self.scoreboard.update_lives(player = 1, lives = self.active_ship.lives)

        else:
            self.scoreboard.set_player2_score(self.active_ship.score)
            self.scoreboard.update_lives(player = 2, lives = self.active_ship.lives)

        # Check for extra life bonus
        if self.active_ship.points_since_last_life >= BONUS_LIFE_THRESHOLD:
            if self.active_ship.lives < MAX_LIVES:
                self.active_ship.lives += 1
                self.active_ship.points_since_last_life = 0

                x, y = self.active_ship.position()
                bonus_pos = (x, y + 60)  # Show bonus animation above the ship

                # Choose image depending on player
                image = "images/icons/player1_small.gif" if self.active_ship == self.player1_ship else "images/icons/player2_small.gif"
                BonusLifeAnimation(self, bonus_pos, image, self.screen)
                self.screen.update()

                # Update visual lives display again to reflect new life
                if self.active_ship == self.player1_ship:
                    self.scoreboard.update_lives(player = 1, lives = self.active_ship.lives)

                else:
                    self.scoreboard.update_lives(player = 2, lives = self.active_ship.lives)

    def reset_player_ship(self):
        """
        Reset the active player's ship position to default.
        """
        self.active_ship.reset_ship_position()

    def start_game(self):
        """
        tarts the game by clearing the start screen and showing the difficulty menu.

        - Only starts if the game hasn't started yet.
        - Plays start sound.
        - Pauses game and shows difficulty selection.
        - Binds keys '1', '2', '3' to difficulty choices.
        """

        if self.started:
            return

        self.started = True

        # Clear the start screen messages
        self.scoreboard.clear_start_screen()

        self.sound.play_sound("start")

        self.paused = True
        self.scoreboard.show_difficulty_menu()

        # Bind keys to difficulty selection functions
        self.screen.onkey(lambda: self.choose_difficulty("easy"), "1")
        self.screen.onkey(lambda: self.choose_difficulty("medium"), "2")
        self.screen.onkey(lambda: self.choose_difficulty("hard"), "3")
        self.screen.listen()



    def choose_difficulty(self, difficulty):
        """
        Sets the difficulty level and starts the actual game.

        Difficulty must be one of "easy", "medium", or "hard".
        """

        if difficulty in ("easy", "medium", "hard"):
            self.level_manager.set_difficulty(difficulty)
            self.start_actual_game()

    def start_actual_game(self):
        """
        Clears the difficulty menu and unpauses the game.

        - Enables 'p' key to toggle pause.
        - Resumes the current player's turn.
        """

        self.scoreboard.clear_difficulty_menu()
        self.paused = False

        self.screen.onkey(self.toggle_pause, "p")
        self.resume_turn()


    def end_game(self):
        """
        Ends the game:

        - Pauses the game.
        - Stops music and plays 'game over' sound.
        - Cancels any ongoing alien timers (like movement or shooting).
        - Clears active explosions and all game elements.
        - Shows game over screen.
        - Binds 'Return' to restart and 'Escape' to exit.
        """

        self.paused = True
        self.sound.stop_music()
        self.sound.play_sound("game_over")

        self.aliens.cancel_timers()

        Explosion(self.active_ship.position(), self.screen).clear()
        self.clear_all()

        self.scoreboard.show_game_over_screen()

        self.screen.onkey(self.restart_game, "Return")
        self.screen.onkey(self.exit_game, "Escape")

    def restart_game(self):
        """
        Restart the game to initial state:

        - Clears all elements and cancels timers.
        - Resets scores, lives, and points counters.
        - Resets all game objects: players, aliens, shields, scoreboard, etc.
        - Shows start screen and difficulty menu.
        - Rebinds difficulty keys.
        """

        self.clear_all()
        self.aliens.cancel_timers()
        self.scoreboard.cancel_fade_transition()

        if hasattr(self.scoreboard, "game_over_writer"):
            self.scoreboard.clear_game_over_screen()

        # Reset scores and points for both players
        self.player1_ship.score = 0
        self.player2_ship.score = 0
        self.player1_ship.points_since_last_life = 0
        self.player2_ship.points_since_last_life = 0

        # Reset vidas
        self.player1_ship.lives = LIVES
        self.player2_ship.lives = LIVES

        # Reset ships and game entities
        self.player1_ship.reset()
        self.player2_ship.reset()
        self.active_ship = self.player1_ship
        self.scoreboard.reset()

        self.level_manager.level = 1
        self.aliens.reset()
        self.shields.reset()

        # Reset ships position and hide player 2 initially
        self.player1_ship.reset_ship_position()
        self.player2_ship.reset_ship_position()
        self.player2_ship.hideturtle()

        self.started = False
        self.paused = True

        # Show start and difficulty selection screens
        self.scoreboard.show_start_screen()
        self.sound.play_sound("start")
        self.scoreboard.show_difficulty_menu()

        self.screen.onkey(lambda: self.level_manager.set_difficulty("easy"), "1")
        self.screen.onkey(lambda: self.level_manager.set_difficulty("medium"), "2")
        self.screen.onkey(lambda: self.level_manager.set_difficulty("hard"), "3")
        self.screen.listen()


    def exit_game(self):
        """
        Exit the game by closing the turtle graphics window.
        """
        self.screen.bye()

    def clear_all(self):
        """
        Clear all game elements from the screen and reset visuals:

        - Hide both player ships and clear their lasers.
        - Clear aliens and shields.
        - Clear scoreboard and any menus.
        - Make boss ship disappear if active.
        - Update the screen to reflect changes.
        """

        self.player1_ship.hideturtle()
        self.player2_ship.hideturtle()
        self.player1_ship.clear_lasers()
        self.player2_ship.clear_lasers()
        self.aliens.clear_all()
        self.shields.clear_shields()
        self.scoreboard.clear()
        self.scoreboard.clear_start_screen()
        self.scoreboard.clear_difficulty_menu()

        if self.boss_ship.active:
            self.boss_ship.disappear()

        self.screen.update()


if __name__ == "__main__":
    # Create an instance of the custom game screen
    screen = ScreenGame()

    # Start the main event loop to keep the window open and responsive
    screen.screen.mainloop()
