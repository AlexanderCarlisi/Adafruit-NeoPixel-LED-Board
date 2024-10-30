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

DISPLAY = Display()




# def is_valid_move(row, col, direction):
#     # Check if the move is valid (not into a wall)
#     if direction == Direction.UP:
#         return (row - 1, col) not in WALLS
#     elif direction == Direction.DOWN:
#         return (row + 1, col) not in WALLS
#     elif direction == Direction.LEFT:
#         return (row, col - 1) not in WALLS
#     elif direction == Direction.RIGHT:
#         return (row, col + 1) not in WALLS
#     return False


# def get_manhattan_distance(row1, col1, row2, col2):
#     return {
#         Direction.UP: abs(row1 - 1 - row2) + abs(col1 - col2),
#         Direction.DOWN: abs(row1 + 1 - row2) + abs(col1 - col2),
#         Direction.LEFT: abs(row1 - row2) + abs(col1 - 1 - col2),
#         Direction.RIGHT: abs(row1 - row2) + abs(col1 + 1 - col2)
#     }



# # Calculate the target position based on Pacman's current position
# def blinky_algorithm(ghost, pacman):
#     ghost_row, ghost_col = ghost.position
#     pacman_row, pacman_col = pacman.position

#     # Calculate distances in each direction (Manhattan distance)
#     distances = get_manhattan_distance(ghost_row, ghost_col, pacman_row, pacman_col)

#     # Filter out directions that are blocked by walls
#     valid_moves = {
#         direction: dist for direction, dist in distances.items() if is_valid_move(ghost_row, ghost_col, direction)
#     }

#     # Get the direction with the minimum distance
#     if valid_moves:
#         best_direction = min(valid_moves, key=valid_moves.get)

#         # Update ghost position based on the chosen direction
#         if best_direction == Direction.UP:
#             ghost_row -= 1
#         elif best_direction == Direction.DOWN:
#             ghost_row += 1
#         elif best_direction == Direction.LEFT:
#             ghost_col -= 1
#         elif best_direction == Direction.RIGHT:
#             ghost_col += 1
#         ghost.update_position(ghost_row, ghost_col)


# # Calculate the target position two tiles ahead of Pacman and then double the vector from Blinky to the target
# def inky_algorithm(inky, pacman, blinky, input_direction):
#     # Step 1: Find the position two tiles ahead of Pac-Man in his current direction
#     pac_row, pac_col = pacman.position
#     target_row, target_col = pac_row, pac_col

#     if input_direction == Direction.UP:
#         target_row -= 2
#     elif input_direction == Direction.DOWN:
#         target_row += 2
#     elif input_direction == Direction.LEFT:
#         target_col -= 2
#     elif input_direction == Direction.RIGHT:
#         target_col += 2

#     # Step 2: Calculate the vector from Blinky to the target
#     blinky_row, blinky_col = blinky.position
#     vector_row = target_row - blinky_row
#     vector_col = target_col - blinky_col

#     # Step 3: Double the vector to get Inky's target position
#     inky_target_row = blinky_row + 2 * vector_row
#     inky_target_col = blinky_col + 2 * vector_col

#     # Step 4: Move Inky towards this target position using Manhattan distance
#     inky_row, inky_col = inky.position
#     distances = get_manhattan_distance(inky_row, inky_col, inky_target_row, inky_target_col)

#     # Filter out directions that are blocked by walls
#     valid_moves = {
#         direction: dist for direction, dist in distances.items() if is_valid_move(inky_row, inky_col, direction)
#     }

#     # Get the direction with the minimum distance
#     if valid_moves:
#         best_direction = min(valid_moves, key=valid_moves.get)

#         # Update Inky's position based on the chosen direction
#         if best_direction == Direction.UP:
#             inky_row -= 1
#         elif best_direction == Direction.DOWN:
#             inky_row += 1
#         elif best_direction == Direction.LEFT:
#             inky_col -= 1
#         elif best_direction == Direction.RIGHT:
#             inky_col += 1

#         inky.update_position(inky_row, inky_col)



# # Calculate the target position four tiles ahead of Pacman
# def pinky_algorithm(pinky, pacman, input_direction):
#     # Step 1: Find the position four tiles ahead of Pac-Man in his current direction
#     pac_row, pac_col = pacman.position
#     target_row, target_col = pac_row, pac_col

#     if input_direction == Direction.UP:
#         target_row -= 4
#     elif input_direction == Direction.DOWN:
#         target_row += 4
#     elif input_direction == Direction.LEFT:
#         target_col -= 4
#     elif input_direction == Direction.RIGHT:
#         target_col += 4

#     # Step 2: Move Pinky towards this target position using Manhattan distance
#     pinky_row, pinky_col = pinky.position
#     distances = get_manhattan_distance(pinky_row, pinky_col, target_row, target_col)

#     # Filter out directions that are blocked by walls
#     valid_moves = {
#         direction: dist for direction, dist in distances.items() if is_valid_move(pinky_row, pinky_col, direction)
#     }

#     # Get the direction with the minimum distance
#     if valid_moves:
#         best_direction = min(valid_moves, key=valid_moves.get)

#         # Update Pinky's position based on the chosen direction
#         if best_direction == Direction.UP:
#             pinky_row -= 1
#         elif best_direction == Direction.DOWN:
#             pinky_row += 1
#         elif best_direction == Direction.LEFT:
#             pinky_col -= 1
#         elif best_direction == Direction.RIGHT:
#             pinky_col += 1

#         pinky.update_position(pinky_row, pinky_col)


# # Clyde moves towards Pac if he is more than 8 tiles away, otherwise moves towards the bottom-left corner
# def clyde_algorithm(clyde, pacman):
#     # Step 1: Calculate distance between Clyde and Pac-Man
#     clyde_row, clyde_col = clyde.position
#     pac_row, pac_col = pacman.position
#     distance_to_pacman = abs(clyde_row - pac_row) + abs(clyde_col - pac_col)  # Manhattan distance

#     # Step 2: Determine the target
#     if distance_to_pacman > 8:
#         # If Clyde is farther than 8 tiles, target Pac-Man (Chase mode)
#         target_row, target_col = pac_row, pac_col
#     else:
#         # If Clyde is within 8 tiles, target the bottom-left corner (Scatter mode)
#         target_row, target_col = Display.LED_ROW - 1, 0  # Bottom-left corner

#     # Step 3: Move Clyde towards the target using Manhattan distance
#     distances = get_manhattan_distance(clyde_row, clyde_col, target_row, target_col)

#     # Filter out directions that are blocked by walls
#     valid_moves = {
#         direction: dist for direction, dist in distances.items() if is_valid_move(clyde_row, clyde_col, direction)
#     }

#     # Step 4: Get the direction with the minimum distance to the target
#     if valid_moves:
#         best_direction = min(valid_moves, key=valid_moves.get)

#         # Update Clyde's position based on the chosen direction
#         if best_direction == Direction.UP:
#             clyde_row -= 1
#         elif best_direction == Direction.DOWN:
#             clyde_row += 1
#         elif best_direction == Direction.LEFT:
#             clyde_col -= 1
#         elif best_direction == Direction.RIGHT:
#             clyde_col += 1

#         clyde.update_position(clyde_row, clyde_col)


# Game Information
previous_time = time.time()
FIXED_UPDATE_RATE = 1.0 / 24.0 # 4 updates per second
accumulator = 0


# Input Listeners
class Direction(Enum):
    UP = (0, 1)
    DOWN = (0, -1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

input_direction = Direction.UP
keyboard.add_hotkey('w', lambda: assign_direction(Direction.UP))
keyboard.add_hotkey('s', lambda: assign_direction(Direction.DOWN))
keyboard.add_hotkey('a', lambda: assign_direction(Direction.LEFT))
keyboard.add_hotkey('d', lambda: assign_direction(Direction.RIGHT))

def assign_direction(direction):
    global input_direction
    input_direction = direction


# def get_position_data(map):
#     global PACMAN, GHOSTS, POWER_PELLETS, DOTS, WALLS, GHOST_RELEASE_POSITION, CHERRY_SPAWN_POSITION

#     for row in range(Display.LED_ROW):
#         for col in range(Display.LED_COLUMN):
#             if map[row][col] == 'P':
#                 PACMAN = Entity((row, col), Color(255, 255, 0), 0)
#             elif map[row][col] == 'W':
#                 GHOST_WAITING_POSITIONS.append((row, col))
#             elif map[row][col] == 'R':
#                 GHOST_RELEASE_POSITION = (row, col)
#             elif map[row][col] == 'X':
#                 WALLS.append((row, col))
#             elif map[row][col] == 'D':
#                 DOTS.append((row, col))
#             elif map[row][col] == 'C':
#                 CHERRY_SPAWN_POSITION = (row, col)
#             elif map[row][col] == 'O':
#                 POWER_PELLETS.append((row, col))



#get_position_data(open("pacmanMap.txt", "r").read().splitlines())


class Pose:
    def __init__(self, row, col):
        self.row = row
        self.col = col


class Entity:
    def __init__(self, color, startingPos, moveTime):
        self.color = color
        self.currentPosition = startingPos
        self.previousPosition = startingPos
        self.moveTime = moveTime


pacman = Entity(Color(255, 255, 0), Pose(0, 0))
def testLogic():
    global pacman
    pacman.previousPosition = pacman.currentPosition
    pacman.currentPosition.col += 1


def game_tick():
    global previous_time, accumulator
    currentTime = time.time()
    frameTime = currentTime - previous_time
    previous_time = currentTime
    accumulator += frameTime

    # Fixed Update (Game Logic)
    while accumulator >= FIXED_UPDATE_RATE:
        # Update Logic
        testLogic()
        accumulator -= FIXED_UPDATE_RATE

    # Variable Update
    alpha = accumulator / FIXED_UPDATE_RATE
    print("<<acc \n" + str(alpha))
    # render -> alpha


# Main Loop
while True:
    game_tick()
