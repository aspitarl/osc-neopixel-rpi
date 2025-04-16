import board
import neopixel
import colorsys
import time

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

class Preset_Rainbow:
    def __init__(self, parent_strip):
        self.parent_strip = parent_strip
        self.map_dispatcher()

        self.wavelength = 0.25  # Default wavelength in fraction of the strip length
        self.wavelength_max = self.parent_strip.pixels.n*5
        self.offset = 0  # Offset for animation

        self.time_updated = time.time()

        self.wave_speed = 0.01  # Speed of the wave animation
        self.wave_speed_max = 0.1


    def map_dispatcher(self):
        self.parent_strip.dispatcher.map('/wavelength', self.receive_message)
        self.parent_strip.dispatcher.map('/wave_speed', self.receive_message)

    def receive_message(self, address: str, val: float, *args):
        if address == '/wavelength':
            self.wavelength = val*self.wavelength_max
        if address == '/wave_speed':
            self.wave_speed = val*self.wave_speed_max
            print(val)

    def set_pixels(self):
        pixels = self.parent_strip.pixels
        num_pixels = len(pixels)

        for i in range(num_pixels):
            hue = ((i + self.offset) % self.wavelength) / self.wavelength
            r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
            pixels[i] = (int(r * 255), int(g * 255), int(b * 255))

        pixels.show()

        # Update the offset for the next frame
        current_time = time.time()
        if current_time - self.time_updated > self.wave_speed:
            self.time_updated = current_time
            self.offset += 1
        # self.offset = (self.offset + 1) % self.wavelength

preset_lookup['rainbow'] = Preset_Rainbow