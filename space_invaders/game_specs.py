# Screen dimensions for the game window (max width: 960px, max height: 1024px)
SCREEN_DIMENSIONS = {
    "width": 960,
    "height": 1024
}

# Wall boundaries based on screen dimensions, defining the play area edges
WALLS = {
    "left": SCREEN_DIMENSIONS['width'] / 2 * -1,
    "right": SCREEN_DIMENSIONS['width'] / 2,
    "top": SCREEN_DIMENSIONS['height'] / 2,
    "bottom": SCREEN_DIMENSIONS['height'] / 2 * -1
}

# Color palette for blocks, indexed by row number modulo the number of colors
COLORS = {
    0: "red",
    1: "orange",
    2: "green",
    3: "yellow"
}

# Number of block rows to create in the game
ALIENS = {
    "rows": 5,
    "cols": 11,
    "spacing_x": 60,
    "spacing_y": 50
}

# Maximum number of enemy lasers allowed on screen simultaneously.
# Limits how many shots enemies can fire to balance game difficulty.
MAX_ENEMY_LASERS = 1

# Speed at which lasers travel across the screen.
# Higher value means lasers move faster.
LASER_VELOCITY = 10

# Number of shield blocks present on the player's side for protection.
# Shields absorb enemy laser hits to protect the player.
NUM_SHIELDS = 4

# Size (probably in pixels) of each individual shield block.
# Used for positioning and collision detection.
BLOCK_SIZE = 25

# Initial number of lives a player starts the game with.
# When this reaches zero, player loses or turn switches.
LIVES = 3

# Maximum number of lives a player can accumulate (through bonuses, etc.).
# Prevents the player from having too many lives.
MAX_LIVES = 5

# Number of points a player must accumulate before earning an extra life.
# Helps reward skillful play with additional survivability.
BONUS_LIFE_THRESHOLD = 2000

# Points awarded to the player for destroying a single enemy alien.
# Used to update the player's score.
POINTS_PER_ENEMY = 20

# Bonus points awarded for hitting or defeating the boss enemy.
# Adds incentive to target the boss.
BOSS_BONUS_POINTS = 300

# Volume level for sound effects (e.g., explosions, laser shots).
# Value between 0.0 (mute) and 1.0 (max volume).
EFFECTS_VOLUME = 0.3

# Volume level for background music during gameplay.
# Separate control from effects volume for better audio balance.
MUSIC_VOLUME = 0.5
