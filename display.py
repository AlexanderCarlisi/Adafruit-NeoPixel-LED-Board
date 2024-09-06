from rpi_ws281x import PixelStrip

class Display:

    LED_ROW = 10            # Rows of LEDs
    LED_COLUMN = 34         # Columns of LEDs
    LED_PIN = 18            # GPIO PWM
    LED_FREQ_HZ = 800000    # 800khz
    LED_DMA = 10            # DMA channel for generating a signal
    LED_CHANNEL = 0         # Set to '1' for GPIOs 13, 19, 41, 45, or 53
    
    LED_MIN_VALUE = 0       # Minimum value for RGB and Brightness
    LED_MAX_VALUE = 255     # Maximum value for RGB and Brightness

    pixelStrip = PixelStrip(LED_ROW * LED_COLUMN, LED_PIN, LED_FREQ_HZ, LED_DMA, False, 20, LED_CHANNEL)
    board = []


    def __init__(self):
        self.pixelStrip.begin() # Initialize rpi_ws281x Library
        self.board = self.generate_board_map() # Initialize LedBoard Pin Mappings


    def generate_board_map(self):
        board_map = []
        for row in range(self.LED_ROW):
            if row % 2 == 0:
                board_map.append(list(range(row * self.LED_COLUMN + self.LED_COLUMN - 1, row * self.LED_COLUMN - 1, -1)))
            else:
                board_map.append(list(range(row * self.LED_COLUMN, (row + 1) * self.LED_COLUMN)))

        return board_map

    def set_pixel_color(self, row, column, color):
        # W does not set brightness, I don't know what it means by white color.
        self.pixelStrip.setPixelColorRGB(self.board[row][column], color.r, color.g, color.b, color.w)

    def show(self):
        self.pixelStrip.show()