# 
# The point of this file is to allow Debugging without having an LED Board in front of you.
# To use this just replace your import of display.py to debug_display.
# The classes are written so that you don't need to change any of your code, only the import.
# Uses pygame to simulate the LED Board.
#

import pygame

# LED and Pygame settings
LED_ROW = 10                # Rows of LEDs to simulate
LED_COLUMN = 34             # Columns of LEDs to simulate
LED_SPACING_PIXELS = 20     # Pixels between each simulated LED
WINDOW_SIZE = (1280, 720)   # Pygame window size
LED_RADIUS = 8              # Radius of each simulated LED


# Color function for consistency with actual LED board class
class Color():
    def __init__(self, r, g, b):
        self.tuple = (r, g, b)
        self.r = r
        self.g = g
        self.b = b


# Returns multiplied color
def color_multiply(color, multiplier):
    return Color(
        max(0, min(255, int(color[0] * multiplier))),
        max(0, min(255, int(color[1] * multiplier))),
        max(0, min(255, int(color[2] * multiplier)))
    )


# Position Class, should be used instead of tuples
class Pose:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def clone(self):
        return Pose(self.row, self.col)
    
    def equals(self, pose):
        return self.row == pose.row and self.col == pose.col
    
    def add(self, pose):
        self.row += pose.row
        self.col += pose.col

    def mult(self, multiplier):
        self.row *= multiplier
        self.col *= multiplier


class Display:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Simulated LED Board")
        
        # Board map and initial color (black/off)
        self.board = [[(0, 0, 0) for _ in range(LED_COLUMN)] for _ in range(LED_ROW)]
        
        # Generate the display positions for each LED on the screen
        self.generate_board_map()

        pygame.display.set_mode(WINDOW_SIZE, pygame.SRCALPHA, 64)


    def generate_board_map(self):
        self.positions = []
        for row in range(LED_ROW):
            row_positions = []
            for col in range(LED_COLUMN):
                x = col * LED_SPACING_PIXELS + 50
                y = row * LED_SPACING_PIXELS + 50
                row_positions.append((x, y))
            self.positions.append(row_positions)


    def set_pixel_color(self, pose, color):
        if 0 <= pose.row < LED_ROW and 0 <= pose.col < LED_COLUMN:
            self.board[pose.row][pose.col] = color.tuple


    # def get_pixel_color(self, row, column):
    #     if 0 <= row < LED_ROW and 0 <= column < LED_COLUMN:
    #         return self.board[row][column]
    #     return Color(0, 0, 0)
    

    # Interpolates the LED Color between 2 points, this is for showing 
    # movement across LEDs. If you interpolate onto the same Position 
    # it will NOT display colors properly.
    # ---
    # alpha = accumulator / fixed_update
    # pixelPos1 = previousPosition
    # pixelPos2 = newPosition
    # color = RGB Color to interpolate
    def interpolate(self, alpha, pixelPos1, pixelPos2, color):
        pixelColor1 = color_multiply(color.tuple, 1 - alpha)  # Fades out
        pixelColor2 = color_multiply(color.tuple, alpha)      # Fades in
        self.set_pixel_color(pixelPos1, pixelColor1)
        self.set_pixel_color(pixelPos2, pixelColor2)
    

    def show(self):
        # Fill the screen with black before drawing LEDs
        self.screen.fill((0, 0, 0))

        # Draw each LED in its respective color
        for row in range(LED_ROW):
            for col in range(LED_COLUMN):
                color = self.board[row][col]
                position = self.positions[row][col]
                pygame.draw.circle(self.screen, color, position, LED_RADIUS)
        
        pygame.display.flip()
        for event in pygame.event.get(): # Unclog the windows toilet
            if event.type == pygame.QUIT:
                exit(0)


    def clear(self):
        for row in range(LED_ROW):
            for col in range(LED_COLUMN):
                pygame.draw.circle(self.screen, (0, 0, 0), self.positions[row][col], LED_RADIUS)


    def close(self):
        pygame.quit()