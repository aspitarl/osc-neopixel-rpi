import board
import neopixel
import colorsys
import time

from pythonosc import dispatcher

from presets import *

preset_lookup = {
'monochrome': Preset_Monochrome,
'rainbow': Preset_Rainbow,
'letters': Preset_Letters,
'rainbow_rain': Preset_RainbowRain,
'rainbombs': Preset_Rainbombs,
} 

default_preset_fp = 'default_preset.txt'

class StripOSCBridge:
    def __init__(self, 
                 preset=None, 
                 board_pin=board.D18, 
                 num_pixels=410
                 ):
        self.pixels = neopixel.NeoPixel(board_pin, num_pixels, auto_write=False, brightness=0.1)

        # Read preset from file if not provided. See TODO below
        if preset is None:
            try:
                with open(default_preset_fp, 'r') as f:
                    preset = f.read().strip()
            except FileNotFoundError:
                preset = 'rainbow'  # Fallback to default if file doesn't exist

        self.set_preset(preset)

    def setup_dispatcher(self):

        self.dispatcher = dispatcher.Dispatcher()
        self.dispatcher.map('/preset', self.change_preset)

    #TODO: cannot change dispatcher mapping while dispatcher is running, figure out how to change the mapping 
    # Could not figure it out, so workarounud is to create preset name text file, 
    # then the rpi can be rebooted to have dispatcher with presets
    def set_preset(self, preset):

        self.setup_dispatcher()

        if preset in preset_lookup:
            self.preset = preset_lookup[preset](self)
            self.preset.map_dispatcher()

            # Update the default preset file
            with open(default_preset_fp, 'w') as f:
                f.write(preset)
        else:
            print(f"Preset {preset} not found. Using default preset.")

    def change_preset(self, address: str, val: float, *args):

        preset_names = list(preset_lookup.keys())
        index = int(val) % len(preset_names)
        selected_preset = preset_names[index]
        print(f"Switching to preset: {selected_preset}")
        self.set_preset(selected_preset)

