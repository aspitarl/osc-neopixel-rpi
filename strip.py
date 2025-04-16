import board
import neopixel
import colorsys

class StripOSCBridge:
    def __init__(self, 
                 dispatcher,
                 preset='monochrome', 
                 board_pin=board.D18, 
                 num_pixels=30
                 ):
        self.pixels = neopixel.NeoPixel(board_pin, num_pixels)

        self.dispatcher = dispatcher
        self.dispatcher.map("/preset", self.set_preset)

        self.set_preset(preset)

    def set_preset(self, preset):
        if preset in preset_lookup:
            self.preset = preset_lookup[preset](self)
        else:
            print(f"Preset {preset} not found. Using default preset.")


## Presets
class Preset_Monochrome:
    def __init__(self, parent_strip):
        self.h = 0
        self.s = 1
        self.v = 1
        
        self.parent_strip = parent_strip


        self.map_dispatcher()
    
    def map_dispatcher(self):
        self.parent_strip.dispatcher.map('/hue', self.recieve_message)
        self.parent_strip.dispatcher.map('/sat', self.recieve_message)
        self.parent_strip.dispatcher.map('/val', self.recieve_message)

    def recieve_message(self, address: str, val: float, *args):
        if address == '/hue':
            self.h = val
        if address == '/sat':
            self.s = val
        if address == '/val':
            self.v = val

    def set_pixels(self):
        r,g,b =  colorsys.hsv_to_rgb(self.h, self.s, self.v)

        pixels = self.parent_strip.pixels
        
        for i in range(len(pixels)):
            pixels[i] = (r*255,g*255,b*255)
        pixels.show()

preset_lookup = {
'monochrome': Preset_Monochrome,
} 