from display import Display
from rpi_ws281x import Color
from enum import Enum
import time
import keyboard


BACKGROUND_COLOR = Color(0, 0, 0)
WALL_COLOR = Color(0, 0, 255)
DOT_COLOR = Color(255, 207, 84)
POWER_PELLET_COLOR = Color(255, 240, 171)
CHERRY_COLOR = Color(252, 5, 71)

GHOST_SCORE = 100
CHERRY_SCORE = 100
DOT_SCORE = 10
POWER_PELLET_SCORE = 50

RESPAWN_TIME = 3
POWER_TIME = 6

DISPLAY = Display()



class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


class Entity:
    def __init__(self, position, color, score):
        self.position = position
        self.color = color
        self.score = score
        self.spawnPosition = position
        self.respawnTime = 0
        self.previousColor = BACKGROUND_COLOR

    def update_position(self, row, col):
        self.clear_position()
        self.previousColor = DISPLAY.get_pixel_color(row, col)
        self.position = (row, col)
        DISPLAY.set_pixel_color(row, col, self.color)

    def clear_position(self):
        DISPLAY.set_pixel_color(self.position[0], self.position[1], self.previousColor)


POWER_PELLETS = []
DOTS = []
CHERRY_SPAWN_POSITION = (0, 0)
GHOST_WAITING_POSITIONS = []
GHOST_RELEASE_POSITION = (0, 0)
WALLS = []


# Game Information
pac_power_time = time.time()
update_interval_seconds = 0.25
last_update_time = time.time()
score = 0
input_direction = Direction.RIGHT
cherry_spawn_time = time.time()
cherryIsSpawned = False


# Input Listeners
keyboard.add_hotkey('w', lambda: assign_direction(Direction.UP))
keyboard.add_hotkey('s', lambda: assign_direction(Direction.DOWN))
keyboard.add_hotkey('a', lambda: assign_direction(Direction.LEFT))
keyboard.add_hotkey('d', lambda: assign_direction(Direction.RIGHT))

def assign_direction(direction):
    global input_direction
    input_direction = direction


def get_position_data(map):
    global PACMAN, GHOSTS, POWER_PELLETS, DOTS, CHERRY, WALLS

    for row in range(Display.LED_ROW):
        for col in range(Display.LED_COLUMN):
            if map[row][col] == 'P':
                PACMAN = Entity((row, col), Color(255, 255, 0), 0)
            elif map[row][col] == 'W':
                GHOST_WAITING_POSITIONS.append((row, col))
            elif map[row][col] == 'R':
                GHOST_RELEASE_POSITION = (row, col)
            elif map[row][col] == 'X':
                WALLS.append((row, col))
            elif map[row][col] == 'D':
                DOTS.append((row, col))
            elif map[row][col] == 'C':
                CHERRY_SPAWN_POSITION = (row, col)
            elif map[row][col] == 'O':
                POWER_PELLETS.append((row, col))


PACMAN = Entity((0, 0), Color(255, 255, 0), 0) # set by get_position_data
get_position_data(open("pacmanMap.txt", "r").read().splitlines())
GHOSTS = [
    Entity(GHOST_WAITING_POSITIONS[0], Color(255, 0, 0), GHOST_SCORE),      # Blinky
    Entity(GHOST_WAITING_POSITIONS[1], Color(255, 0, 225), GHOST_SCORE),    # Pinky
    Entity(GHOST_WAITING_POSITIONS[2], Color(0, 208, 255), GHOST_SCORE),    # Inky
    Entity(GHOST_WAITING_POSITIONS[3], Color(240, 171, 12), GHOST_SCORE),   # Clyde
]


# Main Loop
while True:
    if time.time() - last_update_time >= update_interval_seconds:
        last_update_time = time.time()

        # Update Pacman
        row, col = PACMAN.position
        if input_direction == Direction.UP:
            row -= 1
        elif input_direction == Direction.DOWN:
            row += 1
        elif input_direction == Direction.LEFT:
            col -= 1
        elif input_direction == Direction.RIGHT:
            col += 1

        if (row, col) in WALLS:
            row, col = PACMAN.position

        PACMAN.update_position(row, col)

        # Update Ghosts
        for ghost in GHOSTS:
            row, col = ghost.position
            # Do Algorithem for each Ghost

        # Check for collision
        for ghost in GHOSTS:
            if ghost.position == PACMAN.position:
                if pac_power_time != 0 and time.time() < pac_power_time:
                    score += ghost.score
                    ghost.update_position(ghost.spawnPosition[0], ghost.spawnPosition[1])
                    ghost.respawnTime = time.time() + RESPAWN_TIME

                else:
                    print("Game Over| Score:", score)
                    exit()

        # Check Ghost Respawn
        for ghost in GHOSTS:
            if ghost.respawnTime != 0 and time.time() >= ghost.respawnTime:
                ghost.update_position(GHOST_RELEASE_POSITION[0], GHOST_RELEASE_POSITION[1])
                ghost.respawnTime = 0

        # Check for Power Pellet
        if PACMAN.position in POWER_PELLETS:
            pac_power_time = time.time() + POWER_TIME
            score += POWER_PELLET_SCORE
            POWER_PELLETS.remove(PACMAN.position)

        # Check for Dot
        if PACMAN.position in DOTS:
            score += DOT_SCORE
            DOTS.remove(PACMAN.position)

        # Check for Cherry
        if cherryIsSpawned and PACMAN.position == CHERRY_SPAWN_POSITION:
            score += CHERRY_SCORE
            cherryIsSpawned = False
            # DISPLAY.set_pixel_color(CHERRY_SPAWN_POSITION[0], CHERRY_SPAWN_POSITION[1], BACKGROUND_COLOR)
        
        # Spawn Cherry
        if not cherryIsSpawned and time.time() >= cherry_spawn_time:
            cherry_spawn_time = time.time() + 10
            cherryIsSpawned = True
            DISPLAY.set_pixel_color(CHERRY_SPAWN_POSITION[0], CHERRY_SPAWN_POSITION[1], CHERRY_COLOR)

        # Update Display
        DISPLAY.show()