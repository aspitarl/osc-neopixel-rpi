import board
import neopixel
import colorsys
import time

from pythonosc import dispatcher
from presets import preset_lookup

class StripOSCBridge:
    def __init__(self, 
                 dispatcher: dispatcher.Dispatcher,
                 preset='monochrome', 
                 board_pin=board.D18, 
                 num_pixels=410
                 ):
        self.pixels = neopixel.NeoPixel(board_pin, num_pixels, auto_write=False)

        self.dispatcher = dispatcher

        self.set_preset(preset)

    #TODO: cannot change dispatcher mapping while dispatcher is running, figure out how to change the mapping 
    def set_preset(self, preset):
        if preset in preset_lookup:
            self.preset = preset_lookup[preset](self)

        else:
            print(f"Preset {preset} not found. Using default preset.")

