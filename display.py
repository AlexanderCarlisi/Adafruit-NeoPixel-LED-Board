#
# Display class for the Adafruit PixelStrip
#
# Due to the nature of how the library works, don't worry about
# only updating pixels that are being changed, since it
# will refresh all the pixels no matter what, there is no optimization
# you can do on the display front.
#

from rpi_ws281x import PixelStrip  # type: ignore
from rpi_ws281x import Color as rpi_color # type: ignore

LED_ROW = 10            # Rows of LEDs
LED_COLUMN = 34         # Columns of LEDs
LED_PIN = 18            # GPIO PWM
LED_FREQ_HZ = 800000    # 800khz
LED_DMA = 10            # DMA channel for generating a signal
LED_CHANNEL = 0         # Set to '1' for GPIOs 13, 19, 41, 45, or 53
BRIGHTNESS = 255        # 0 - 255, constant because you shouldn't change during runtime
    
LED_MIN_VALUE = 0       # Minimum value for RGB and Brightness
LED_MAX_VALUE = 255     # Maximum value for RGB and Brightness


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

    def mult(self, multiplier):
        self.row *= multiplier
        self.col *= multiplier


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
        

    # Don't call get_pixel_color, you will most likely get a different result than what you passed in
    # you're better off just storing the previous color yourself.
    # def get_pixel_color(self, row, column):
    #     if 0 <= row < LED_ROW and 0 <= column < LED_COLUMN:
    #         return self.pixelStrip.getPixelColorRGB(self.board[row][column])
        

    # Interpolates the LED Color between 2 points,
    # this is for showing movement across LEDs.
    # alpha = accumulator / fixed_update
    # pixelPos1 = previousPosition
    # pixelPos2 = newPosition
    # color = RGB Color to interpolate
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