from display import *
from random import randint
from enum import Enum
import time
import keyboard
import display_text

class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

APPLE_COLOR = Color(255, 0, 0)
APPLE_START_POSITION = Pose(4, 25)

SNAKE_COLOR = Color(0, 255, 0)
SNAKE_START_POSITION = Pose(4, 5)

BACKGROUND_COLOR = Color(0, 0, 0)

DISPLAY = Display()

apple_position = APPLE_START_POSITION
snake_head_position = SNAKE_START_POSITION
snake_body_positions = [Pose(SNAKE_START_POSITION.row, SNAKE_START_POSITION.col - 1)] # Initialize with one body part

input_direction = Direction.RIGHT
previous_input_direction = Direction.RIGHT

update_interval_seconds = 0.34
last_update_time = time.time()

score = 0


# Input Listeners
keyboard.add_hotkey('w', lambda: assign_direction(Direction.UP))
keyboard.add_hotkey('s', lambda: assign_direction(Direction.DOWN))
keyboard.add_hotkey('a', lambda: assign_direction(Direction.LEFT))
keyboard.add_hotkey('d', lambda: assign_direction(Direction.RIGHT))

def assign_direction(direction):
    global input_direction, previous_direction
    # Prevent reverse movement (180-degree turn)
    if (direction == Direction.UP and previous_direction != Direction.DOWN) or \
       (direction == Direction.DOWN and previous_direction != Direction.UP) or \
       (direction == Direction.LEFT and previous_direction != Direction.RIGHT) or \
       (direction == Direction.RIGHT and previous_direction != Direction.LEFT):
        input_direction = direction


def startup_text_display():
    while not keyboard.is_pressed("enter"):
        display_text.draw_text_fade(DISPLAY, "PRESS", Pose(0, 0), Color(0, 255, 150), 1, 2)
        display_text.draw_text_fade(DISPLAY, "ENTER", Pose(5, 0), Color(0, 255, 50), 1, 2)
        DISPLAY.show()
    DISPLAY.clear()


def end_text_display():
    gameOverStartTime = time.time()
    gameOverFadeTime = 2
    gameOverStopTime = 2
    DISPLAY.clear()
    while time.time() - gameOverStartTime < gameOverStopTime:
        display_text.draw_text_fade(DISPLAY, "GAME", Pose(0, 0), Color(255, 0, 0), 1, gameOverFadeTime)
        display_text.draw_text_fade(DISPLAY, "OVER", Pose(5, 0), Color(255, 0, 0), 1, gameOverFadeTime)
        DISPLAY.show()

    DISPLAY.clear()
    display_text.draw_string(DISPLAY, "SCORE", Pose(0, 0), Color(0, 255, 100), 1, 1)
    display_text.draw_string(DISPLAY, str(score), Pose(5, 0), Color(200, 255, 255), 1, 1)
    DISPLAY.show()
    input()


# Main Loop
startup_text_display()
while True:
    # Display apple at initial position
    DISPLAY.set_pixel_color(apple_position, APPLE_COLOR)

    # Fixed Update Loop
    # If you want to be optimal, Physics(really logic in this case) should be handled here
    # and rendering should be done in the variable update loop
    if (time.time() - last_update_time) >= update_interval_seconds:
        last_update_time = time.time()

        # Add old head position to body
        previous_head_position = snake_head_position.clone()
        snake_body_positions.insert(0, previous_head_position.clone())

        # Update Head to new position
        if input_direction == Direction.UP:
            snake_head_position = Pose(snake_head_position.row - 1, snake_head_position.col)
        elif input_direction == Direction.DOWN:
            snake_head_position = Pose(snake_head_position.row + 1, snake_head_position.col)
        elif input_direction == Direction.LEFT:
            snake_head_position = Pose(snake_head_position.row, snake_head_position.col - 1)
        elif input_direction == Direction.RIGHT:
            snake_head_position = Pose(snake_head_position.row, snake_head_position.col + 1)

        # Remove last body position
        old_body_pos = snake_body_positions.pop() # old head has been added, this should never be empty here

        # Check Apple Collision
        if snake_head_position.equals(apple_position):
            score += 1
            snake_body_positions.append(old_body_pos.clone()) # Increase length with old body position
            DISPLAY.set_pixel_color(apple_position, BACKGROUND_COLOR) # Remove old apple

            # Generate new apple at a valid random position
            validPosition = False
            while not validPosition: # This sucks, so I might store all possible positions and remove them from the list (I will actually fix this soon)
                apple_position = Pose(randint(0, LED_ROW - 1), randint(0, LED_COLUMN - 1))
                if apple_position not in snake_body_positions and apple_position != snake_head_position:
                    validPosition = True
            DISPLAY.set_pixel_color(apple_position, APPLE_COLOR) # Add new apple

        # Check for Game Over
        if snake_head_position.row < 0 or snake_head_position.row >= LED_ROW or \
        snake_head_position.col < 0 or snake_head_position.col >= LED_COLUMN or \
        snake_head_position in snake_body_positions:
            end_text_display()
            print("Game Over, Score: " + str(score))
            break

        # Update Display
        DISPLAY.set_pixel_color(old_body_pos, BACKGROUND_COLOR)
        for body_pos in snake_body_positions:
            DISPLAY.set_pixel_color(body_pos, SNAKE_COLOR)
        DISPLAY.set_pixel_color(snake_head_position, SNAKE_COLOR)

        previous_direction = input_direction
    DISPLAY.show()

DISPLAY.close()