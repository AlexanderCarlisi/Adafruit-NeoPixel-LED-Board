from enum import Enum
import time
import keyboard
import argparse


# Check debug
parser = argparse.ArgumentParser()
parser.add_argument("debug", help="whether to run without or with the LED Board. Run as debug if you're not on a rasperrypi.")
args = parser.parse_args()
if (args.debug == "y"):
    from debug_display import *
else:
    from display import *


# Input Listeners
class Direction(Enum):
    UP = Pose(-1, 0)
    DOWN = Pose(1, 0)
    LEFT = Pose(0, -1)
    RIGHT = Pose(0, 1)

input_direction = Direction.RIGHT # Global inputDirection for Pacman
# Technically shouldn't be setup like this, it really should be in the
# game loop, but I know this works, and don't feel like changing it.
keyboard.add_hotkey('w', lambda: assign_direction(Direction.UP))
keyboard.add_hotkey('s', lambda: assign_direction(Direction.DOWN))
keyboard.add_hotkey('a', lambda: assign_direction(Direction.LEFT))
keyboard.add_hotkey('d', lambda: assign_direction(Direction.RIGHT))
def assign_direction(direction):
    global input_direction
    input_direction = direction


# Pacman, and Ghosts. Handles basic logic and rendering.
# Additional logic seperate for Pacman and Ghosts can be found in their respective subclasses.
class Entity:
    def __init__(self, color, startingPose, speedSeconds):
        self.color = color
        self.currentPosition = startingPose.clone()
        self.previousPosition = startingPose.clone()
        self.speedSeconds = speedSeconds
        self.spawnPoint = startingPose.clone()
        self.lastMoveTime = 0
        self.alphaAccumulator = 0
        self.respawnEndTime = 0

    def move(self, direction, WALLS):
        if not self.isDead and \
         is_valid_move(WALLS, Pose(self.currentPosition.row + direction.row, self.currentPosition.col + direction.col)) \
         and time.time() - self.lastMoveTime >= self.speedSeconds:
            self.lastMoveTime = time.time()
            self.previousPosition = self.currentPosition.clone()
            self.currentPosition.add(direction.clone())

    def render(self, DISPLAY):
        alpha = (time.time() - self.lastMoveTime) / self.speedSeconds

        if self.currentPosition.equals(self.previousPosition):
            DISPLAY.set_pixel_color(self.currentPosition, self.color)
        else:
            DISPLAY.interpolate(alpha, self.previousPosition, self.currentPosition, self.color)

    @property
    def isDead(self):
        return self.respawnEndTime > time.time()


# Pacman subclass of Entity, handles additional logic like eating.
class Pacman(Entity):
    def __init__(self, color, startingPose, speedSeconds):
        super().__init__(color, startingPose, speedSeconds)
        self.score = 0
        self.powerEndTime = 0
        self.lives = 3
    
    @property
    def isPowered(self):
        return time.time() <= self.powerEndTime
    
    # Checks if new position is already populated, this should be called after super.move()
    # Handles logic for hitting ghosts, and eating.
    def checkCollision(self, game):
        ghosts = (game.blinky, game.inky, game.pinky, game.clyde)
        for pellet in game.POWER_PELLETS:
            if self.currentPosition.equals(pellet):
                self.powerEndTime = time.time() + game.POWER_DURATION_SECONDS
                self.score += game.POWER_PELLET_SCORE
                game.POWER_PELLETS.remove(pellet)

        for dot in game.DOTS:
            if self.currentPosition.equals(dot):
                self.score += game.DOT_SCORE
                game.DOTS.remove(dot)

        for ghost in ghosts:
            if self.currentPosition.equals(ghost.currentPosition):
                if self.isPowered:
                    ghost.respawnEndTime = time.time() + game.GHOST_RESPAWN_TIME
                    ghost.currentPosition = ghost.spawnPoint.clone()
                    self.score += game.GHOST_SCORE

                else:
                    self.respawnEndTime = time.time() + game.PACMAN_RESPAWN_TIME
                    self.currentPosition = self.spawnPoint.clone()
                    self.lives -= 1
        

# Ghost subclass of entity
class Ghost(Entity):
    def __init__(self, color, startingPose, speedSeconds):
        super().__init__(color, startingPose, speedSeconds)
        self.originalColor = Color(color.r, color.g, color.b)
        self.BLINK_SECONDS = 1 # Interval to change color when pacman is powered
        self.blink = False # Flips to being white and blue
        self.blinkEndTime = 0 # When to change colors

    def changeColor(self, pacman, blue, white):
        if pacman.isPowered:
            # Change color
            if time.time() > self.blinkEndTime:
                self.blinkEndTime = time.time() + self.BLINK_SECONDS
                if self.blink:
                    self.color = white
                else:
                    self.color = blue
                self.blink = not self.blink
        else:
            self.color = self.originalColor


# Game Setup
class Game:
    DISPLAY = Display()

    # Main Loop
    FIXED_UPDATE_RATE = 1.0 / 24.0 # 24 updates per second for logic; rendering is variable

    # Colors
    PACMAN_COLOR = Color(255, 255, 0)
    BLINKY_COLOR = Color(255, 0, 0)
    INKY_COLOR = Color(0, 255, 255)
    PINKY_COLOR = Color(255, 0, 255)
    CLYDE_COLOR = Color(255, 128, 0)
    WALL_COLOR = Color(0, 0, 255)
    DOT_COLOR = Color(253, 255, 138)
    POWER_PELLET_COLOR = Color(255, 255, 255)
    GHOST_SCARED_BLUE = Color(0, 170, 255)
    GHOST_SCARED_WHITE = Color(186, 232, 255)

    # Move speeds: 1 LED per time given in seconds
    PACMAN_MOVE_SPEED = 0.25
    BLINKY_MOVE_SPEED = 0.34
    INKY_MOVE_SPEED = 0.34
    PINKY_MOVE_SPEED = 0.34
    CLYDE_MOVE_SPEED = 0.34

    # Scores
    DOT_SCORE = 10
    POWER_PELLET_SCORE = 50
    GHOST_SCORE = 100
    CHERRY_SCORE = 250

    POWER_DURATION_SECONDS = 8
    GHOST_RESPAWN_TIME = 5
    PACMAN_RESPAWN_TIME = 3

    def __init__(self):
        self.previous_time = time.time()
        self.accumulator = 0
        self.GHOST_SPAWN_POSITIONS = list()
        self.WALLS = list()
        self.DOTS = list()
        self.POWER_PELLETS = list()

        self.get_position_data(open("pacmanMap.txt", "r").read().splitlines())
        self.pacman = Pacman(self.PACMAN_COLOR, self.PACMAN_SPAWN, self.PACMAN_MOVE_SPEED)
        self.blinky = Ghost(self.BLINKY_COLOR, self.GHOST_SPAWN_POSITIONS[0], self.BLINKY_MOVE_SPEED)
        self.inky = Ghost(self.INKY_COLOR, self.GHOST_SPAWN_POSITIONS[1], self.INKY_MOVE_SPEED)
        self.pinky = Ghost(self.PINKY_COLOR, self.GHOST_SPAWN_POSITIONS[2], self.PINKY_MOVE_SPEED)
        self.clyde = Ghost(self.CLYDE_COLOR, self.GHOST_SPAWN_POSITIONS[3], self.CLYDE_MOVE_SPEED)
        

    def start(self):
        # Initialize unchanging leds
        for pose in self.WALLS:
            self.DISPLAY.set_pixel_color(pose, self.WALL_COLOR)

        # Main Loop
        while not self.isFinished:
            self.tick()

        print("Game Over")
        self.DISPLAY.close() # release resources
            
    def update(self):
        global input_direction
        # Update Ghost Positions
        self.blinky.move(blinky_algorithm(self.blinky, self.pacman, self.WALLS), self.WALLS)
        self.inky.move(inky_algorithm(self.inky, self.pacman, self.blinky, input_direction, self.WALLS), self.WALLS)
        self.pinky.move(pinky_algorithm(self.pinky, self.pacman, input_direction, self.WALLS), self.WALLS)
        self.clyde.move(clyde_algorithm(self.clyde, self.pacman, self.WALLS), self.WALLS)

        # Check for Collison, this fixes an issue where sometimes Pacman phases through ghosts.
        # This happens because they have different move times
        self.pacman.checkCollision(self)

        # Update Pacman position
        self.pacman.move(input_direction.value, self.WALLS)
        self.pacman.checkCollision(self)

        # Update Ghost Colors
        self.blinky.changeColor(self.pacman, self.GHOST_SCARED_BLUE, self.GHOST_SCARED_WHITE)
        self.inky.changeColor(self.pacman, self.GHOST_SCARED_BLUE, self.GHOST_SCARED_WHITE)
        self.pinky.changeColor(self.pacman, self.GHOST_SCARED_BLUE, self.GHOST_SCARED_WHITE)
        self.clyde.changeColor(self.pacman, self.GHOST_SCARED_BLUE, self.GHOST_SCARED_WHITE)

    def render(self):
        self.DISPLAY.clear()
        for pose in self.DOTS:
            self.DISPLAY.set_pixel_color(pose, self.DOT_COLOR)
        for pose in self.POWER_PELLETS:
            self.DISPLAY.set_pixel_color(pose, self.POWER_PELLET_COLOR)
        
        if not self.pacman.isPowered: # If not powered, then get overridden by ghosts
            self.pacman.render(self.DISPLAY)
        self.blinky.render(self.DISPLAY)
        self.inky.render(self.DISPLAY)
        self.pinky.render(self.DISPLAY)
        self.clyde.render(self.DISPLAY)
        if self.pacman.isPowered: # If powered, override ghosts
            self.pacman.render(self.DISPLAY)
        self.DISPLAY.show()

    def tick(self):
        currentTime = time.time()
        frameTime = currentTime - self.previous_time
        self.previous_time = currentTime
        self.accumulator += frameTime

        # Fixed Update (Game Logic)
        while self.accumulator >= self.FIXED_UPDATE_RATE:
            self.update()
            self.accumulator -= self.FIXED_UPDATE_RATE

        # Variable Update
        self.render()

    @property
    def isFinished(self):
        return self.pacman.lives <= 0 or len(self.DOTS) <= 0

    def get_position_data(self, map):
        for row in range(LED_ROW):
            for col in range(LED_COLUMN):
                if map[row][col] == 'P':
                    self.PACMAN_SPAWN = Pose(row, col)
                elif map[row][col] == 'W':
                    self.GHOST_SPAWN_POSITIONS.append(Pose(row, col))
                elif map[row][col] == 'X':
                    self.WALLS.append(Pose(row, col))
                elif map[row][col] == 'D':
                    self.DOTS.append(Pose(row, col))
                elif map[row][col] == 'C':
                    self.CHERRY_SPAWN_POSITION = Pose(row, col)
                elif map[row][col] == 'O':
                    self.POWER_PELLETS.append(Pose(row, col))



#
# Ghost Algorithms
#

# Check if the move is valid (not into a wall)
def is_valid_move(WALLS, pose):
    for wall in WALLS:
        if pose.equals(wall):
            return False
    return True

def get_manhattan_distance(pose1, pose2):
    return {
        Direction.UP: abs(pose1.row - 1 - pose2.row) + abs(pose1.col - pose2.col),
        Direction.DOWN: abs(pose1.row + 1 - pose2.row) + abs(pose1.col - pose2.col),
        Direction.LEFT: abs(pose1.row - pose2.row) + abs(pose1.col - 1 - pose2.col),
        Direction.RIGHT: abs(pose1.row - pose2.row) + abs(pose1.col + 1 - pose2.col)
    }


# Calculate the target position based on Pacman's current position
# Returns Pose to move Blinky by
def blinky_algorithm(ghost, pacman, WALLS):
    # Calculate distances in each direction (Manhattan distance)
    distances = get_manhattan_distance(ghost.currentPosition, pacman.currentPosition)

    # Filter out directions that are blocked by walls
    valid_moves = {
        direction: dist for direction, dist in distances.items() if is_valid_move(WALLS, ghost.currentPosition.clone().add(direction.value))
    }

    # Get the direction with the minimum distance
    if valid_moves:
        best_direction = min(valid_moves, key=valid_moves.get)
        return best_direction.value
    
    print("BLINKY Error: No valid moves")
    return Pose(0, 0)


# Calculate the target position two tiles ahead of Pacman and then double the vector from Blinky to the target
def inky_algorithm(inky, pacman, blinky, input_direction, WALLS):
    # Step 1: Find the position two tiles ahead of Pac-Man in his current direction
    pacPose = pacman.currentPosition
    targetPose = pacPose.clone()

    targetPose.add(input_direction.value.clone().mult(2))

    # Step 2: Calculate the vector from Blinky to the target
    vector_row = targetPose.row - blinky.currentPosition.row
    vector_col = targetPose.col - blinky.currentPosition.col

    # Step 3: Double the vector to get Inky's target position
    targetPose = blinky.currentPosition.clone()
    targetPose.add(Pose(2 * vector_row, 2 * vector_col))

    # Step 4: Move Inky towards this target position using Manhattan distance
    distances = get_manhattan_distance(inky.currentPosition, targetPose)

    # Filter out directions that are blocked by walls
    valid_moves = {
        direction: dist for direction, dist in distances.items() if is_valid_move(WALLS, inky.currentPosition.clone().add(direction.value))
    }

    # Get the direction with the minimum distance
    if valid_moves:
        best_direction = min(valid_moves, key=valid_moves.get)
        return best_direction.value
    
    print("INKY Error: No valid moves")
    return Pose(0, 0)


def pinky_algorithm(pinky, pacman, input_direction, WALLS):
    # Step 1: Find the position four tiles ahead of Pac-Man in his current direction
    target_pose = pacman.currentPosition.clone()
    target_pose.add(input_direction.value.clone().mult(4))

    # Step 2: Calculate Manhattan distances to the target position
    distances = get_manhattan_distance(pinky.currentPosition, target_pose)

    # Step 3: Filter out directions that are blocked by walls
    valid_moves = {
        direction: dist for direction, dist in distances.items() if is_valid_move(WALLS, pinky.currentPosition.clone().add(direction.value))
    }

    # Step 4: Choose the best direction based on minimum distance
    if valid_moves:
        best_direction = min(valid_moves, key=valid_moves.get)
        return best_direction.value

    # If no valid moves, return a default (stationary or error) pose
    print("PINKY Error: No valid moves")
    return Pose(0, 0)


def clyde_algorithm(clyde, pacman, WALLS):
    # Step 1: Calculate the distance between Clyde and Pac-Man
    distance_to_pacman = abs(clyde.currentPosition.row - pacman.currentPosition.row) + \
                         abs(clyde.currentPosition.col - pacman.currentPosition.col)  # Manhattan distance

    # Step 2: Determine the target
    if distance_to_pacman > 8:
        # If Clyde is farther than 8 tiles, target Pac-Man (Chase mode)
        target_pose = pacman.currentPosition.clone()
    else:
        # If Clyde is within 8 tiles, target the bottom-left corner (Scatter mode)
        target_pose = Pose(LED_ROW - 1, 0)  # Bottom-left corner

    # Step 3: Calculate Manhattan distances to the target position
    distances = get_manhattan_distance(clyde.currentPosition, target_pose)

    # Step 4: Filter out directions that are blocked by walls
    valid_moves = {
        direction: dist for direction, dist in distances.items() if is_valid_move(WALLS, clyde.currentPosition.clone().add(direction.value))
    }

    # Step 5: Choose the best direction based on minimum distance
    if valid_moves:
        best_direction = min(valid_moves, key=valid_moves.get)
        return best_direction.value

    # If no valid moves, return a default (stationary or error) pose
    print("CLYDE Error: No valid moves")
    return Pose(0, 0)


# Main Loop
game = Game()
game.start()