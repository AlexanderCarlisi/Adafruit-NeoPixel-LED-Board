from display import *

TEXT_ROW = 5
TEXT_COL = 5

def draw_char(display, char, topLeftPose, color):
    mapping = open("text/" + char + ".txt", "r").read().splitlines()
    pixelPose = topLeftPose.clone()
    for row in range(TEXT_ROW):
        pixelPose.col = topLeftPose.col
        try:
            for col in range(TEXT_COL):
                if mapping[row][col] == '#':
                    display.set_pixel_color(pixelPose, color)
                pixelPose.col += 1
        except:
            pass # Some letters don't have white space to the end, so COL ends early
        pixelPose.row += 1
                

def draw_string(display, string, topLeftPose, color, letterSpacing=1, alpha=1):
    string = string.upper()
    pixelPose = topLeftPose.clone()
    color = color_multiply(color, alpha)
    for char in string:
        draw_char(display, char, pixelPose, color)
        pixelPose.col += TEXT_COL + letterSpacing