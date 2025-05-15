import board
import neopixel
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Control NeoPixel brightness.")
parser.add_argument("--off", action="store_true", help="Turn off all pixels by setting brightness to zero.")
args = parser.parse_args()

pixels = neopixel.NeoPixel(board.D18, 410, auto_write=False)

# Set brightness based on the --off flag
brightness = 0.0 if args.off else 0.5

for i in range(len(pixels)):
    pixels[i] = (255 * brightness, 0, 0)  # Red color

pixels.write()
pixels.show()
