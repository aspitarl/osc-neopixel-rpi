import board
import neopixel

pixels = neopixel.NeoPixel(board.D18,120, auto_write=False)

for i in range(len(pixels)):
    pixels[i] = (255,255,0)

pixels.write()
pixels.show()
