import board
import neopixel

pixels = neopixel.NeoPixel(board.D18,30)
pixels[0] = (10, 0 ,0)
pixels[9] = (0, 10 ,0)
pixels.show()
