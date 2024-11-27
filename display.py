#
# Display class for the Adafruit PixelStrip
#
# Due to the nature of how the library works, don't worry about
# only updating pixels that are being changed, since it
# will refresh all the pixels no matter what, there is no optimization
# you can do on the display front.
#

# Constants
LED_ROW = 10            # Rows of LEDs
LED_COLUMN = 34         # Columns of LEDs
LED_PIN = 18            # GPIO PWM
LED_FREQ_HZ = 800000    # 800khz
LED_DMA = 10            # DMA channel for generating a signal
LED_CHANNEL = 0         # Set to '1' for GPIOs 13, 19, 41, 45, or 53
BRIGHTNESS = 255        # 0 - 255, constant because you shouldn't change during runtime

# Check if Debug with pygame, or real LED Board
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("debug", help="whether to run without or with the LED Board. Run as debug if you're not on a rasperrypi.")
args = parser.parse_args()

# Debug
if (args.debug == "y"):
    import pygame
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
            max(0, min(255, int(color.tuple[0] * multiplier))),
            max(0, min(255, int(color.tuple[1] * multiplier))),
            max(0, min(255, int(color.tuple[2] * multiplier)))
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
            return self.clone()

        def mult(self, multiplier):
            self.row *= multiplier
            self.col *= multiplier
            return self.clone()

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

        # Interpolates the LED Color between 2 points, this is for showing 
        # movement across LEDs. If you interpolate onto the same Position 
        # it will NOT display colors properly.
        def interpolate(self, alpha, pixelPos1, pixelPos2, color):
            pixelColor1 = color_multiply(color, 1 - alpha)  # Fades out
            pixelColor2 = color_multiply(color, alpha)      # Fades in
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
                    self.board[row][col] = (0, 0, 0)
                    pygame.draw.circle(self.screen, (0, 0, 0), self.positions[row][col], LED_RADIUS)

        def close(self):
            pygame.quit()

# LED Board
else:
    from rpi_ws281x import PixelStrip  # type: ignore
    from rpi_ws281x import Color as rpi_color # type: ignore

    # For use with debug_display, you should always use Color over ws281x's Color.
    def Color(r, g, b):
        return rpi_color(r, g, b)

    # Returns multiplied color
    def color_multiply(color, multiplier):
        return Color(color.r * multiplier, color.g * multiplier, color.b * multiplier)

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
            return self.clone()

        def mult(self, multiplier):
            self.row *= multiplier
            self.col *= multiplier
            return self.clone()

    # Adafruit Neopixel LED Board class
    class Display:
        pixelStrip = None
        board = []

        def __init__(self):
            self.pixelStrip = PixelStrip(LED_ROW * LED_COLUMN, LED_PIN, LED_FREQ_HZ, LED_DMA, False, BRIGHTNESS, LED_CHANNEL)
            self.pixelStrip.begin() # Initialize rpi_ws281x Library
            self.board = self.generate_board_map() # Initialize LedBoard Pin Mappings

        def generate_board_map(self):
            board_map = []
            for row in range(LED_ROW):
                if row % 2 == 0:
                    board_map.append(list(range(row * LED_COLUMN + LED_COLUMN - 1, row * LED_COLUMN - 1, -1)))
                else:
                    board_map.append(list(range(row * LED_COLUMN, (row + 1) * LED_COLUMN)))

            return board_map

        def set_pixel_color(self, pose, color):
            if 0 <= pose.row < LED_ROW and 0 <= pose.col < LED_COLUMN:
                self.pixelStrip.setPixelColor(self.board[pose.row][pose.col], color)
            
        # Interpolates the LED Color between 2 points, this is for showing 
        # movement across LEDs. If you interpolate onto the same Position 
        # it will NOT display colors properly.
        def interpolate(self, alpha, pixelPos1, pixelPos2, color):
            pixelColor1 = color_multiply(color, 1 - alpha)  # Fades out
            pixelColor2 = color_multiply(color, alpha)      # Fades in
            self.set_pixel_color(pixelPos1, pixelColor1)
            self.set_pixel_color(pixelPos2, pixelColor2)

        def show(self):
            self.pixelStrip.show()

        def close(self):
            for row in range(LED_ROW):
                for col in range(LED_COLUMN):
                    self.pixelStrip.setPixelColor(self.board[row][col], Color(0, 0, 0))