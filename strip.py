import board
import neopixel
import colorsys


class MyStrip():
    def __init__(self, board_pin=board.D18, num_pixels=30):
        self.h = 0
        self.s = 1
        self.v = 1
        self.pixels = neopixel.NeoPixel(board_pin, num_pixels)

    def set_hsv(self, address: str, val: float, *args):
        if address == '/hue':
            self.h = val
        if address == '/sat':
            self.s = val
        if address == '/val':
            self.v = val

    def set_pixels(self):
        r,g,b =  colorsys.hsv_to_rgb(self.h, self.s, self.v)
        
        for i in range(len(self.pixels)):
            self.pixels[i] = (r*255,g*255,b*255)
        self.pixels.show()