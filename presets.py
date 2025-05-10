import time
import colorsys
import random

led_brightness = 0.2  # Default brightness for all presets

## Presets
class Preset_Monochrome:
    def __init__(self, parent_strip):
        self.h = 0
        self.s = 1
        self.v = 0.1
        self.hue_offset = 0
        self.cycle_speed = 0.01  # Speed of hue cycling
        self.parent_strip = parent_strip

        self.time_updated = time.time()  # Track the last update time

        self.map_dispatcher()
    
    def map_dispatcher(self):
        self.parent_strip.dispatcher.map('/hue_offset', self.recieve_message)
        self.parent_strip.dispatcher.map('/sat', self.recieve_message)
        self.parent_strip.dispatcher.map('/val', self.recieve_message)
        self.parent_strip.dispatcher.map('/cycle_speed', self.recieve_message)

    def recieve_message(self, address: str, val: float, *args):
        if address == '/hue_offset':
            self.hue_offset = val
        if address == '/sat':
            self.s = val
        if address == '/val':
            self.v = val
        if address == '/cycle_speed':
            self.cycle_speed = val

    def set_pixels(self):
        # Update hue based on time and cycle speed
        current_time = time.time()
        self.h = (self.h + self.cycle_speed * (current_time - self.time_updated)) % 1.0
        self.time_updated = current_time

        r, g, b = colorsys.hsv_to_rgb(self.h + self.hue_offset, self.s, self.v*led_brightness)

        pixels = self.parent_strip.pixels
        
        for i in range(len(pixels)):
            pixels[i] = (int(r * 255), int(g * 255), int(b * 255))

        pixels.write()
        pixels.show()

preset_lookup = {
'monochrome': Preset_Monochrome,
} 

class Preset_Rainbow:
    def __init__(self, parent_strip):
        self.parent_strip = parent_strip
        self.map_dispatcher()

        self.wavelength_max = self.parent_strip.pixels.n*5
        self.wavelength = 0.25  # Default wavelength in fraction of the strip length
        self.wavelength = self.wavelength_max * self.wavelength  # Convert to pixel count
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

    def set_pixels(self):
        pixels = self.parent_strip.pixels
        num_pixels = len(pixels)

        for i in range(num_pixels):
            if i not in pixel_map_arr:
                continue
            i_hue = pixel_map_arr.index(i)
            hue = ((i_hue + self.offset) % self.wavelength) / self.wavelength
            r, g, b = colorsys.hsv_to_rgb(hue, 1, led_brightness)

            pixels[i] = (int(r * 255), int(g * 255), int(b * 255))

        pixels.write()
        pixels.show()

        # Update the offset for the next frame
        current_time = time.time()
        if current_time - self.time_updated > self.wave_speed:
            self.time_updated = current_time
            self.offset += 1
        # self.offset = (self.offset + 1) % self.wavelength

preset_lookup['rainbow'] = Preset_Rainbow


# this is a dictionary that maps letters to their corresponding pixel positions
# the letters spell the word "elationstation"
# The keys of the dict are unique: e1 l1, etc. 
letter_lookup_dict = {
    'e1': (0,24),
    'l1': (30,48),
    'a1': (60,81),
    't1': (90,109),
    'i1': (118,142),
    'o1': (148,168),
    'n1': (176,203),
    's1': (205,225),
    't2': (234,255),
    'a2': (256,285),
    't3': (286,313),
    'i2': (315,337),
    'o2': (350,369),
    'n2': (378,410),
}

# make a lookup array for incremental pixel positions

pixel_map_arr = []
total_length = sum([end - start for start, end in letter_lookup_dict.values()])
for letter, (start, end) in letter_lookup_dict.items():
    pixel_map_arr.extend(range(start, end))


def get_mapped_pixel(i, pixel_map_arr):
    if i >= len(pixel_map_arr):
        return i 
    return pixel_map_arr[i]



# Make a preset that sets each letter to a different color
# one parameter should be the hue shift per letter

class Preset_Letters:
    def __init__(self, parent_strip):
        self.parent_strip = parent_strip
        self.map_dispatcher()

        self.hue_shift = 2/14  # Default hue shift per letter
        self.hue_shift_max = 1.0

        self.idx_offset = 0  # Offset for animation
        self.time_updated = time.time()  # Track the last update time

        self.time_wait = 0.2  # Time to wait before updating the offset

    def map_dispatcher(self):
        self.parent_strip.dispatcher.map('/hue_shift', self.receive_message)

    def receive_message(self, address: str, val: float, *args):
        if address == '/hue_shift':
            self.hue_shift = val * self.hue_shift_max

    def set_pixels(self):
        pixels = self.parent_strip.pixels
        num_pixels = len(pixels)

        # Increment idx_offset every second
        current_time = time.time()
        if current_time - self.time_updated >= self.time_wait:
            self.time_updated = current_time
            self.idx_offset -= 1

        for letter, (start, end) in letter_lookup_dict.items():
            letter_idx = list(letter_lookup_dict.keys()).index(letter) + self.idx_offset
            hue = (letter_idx * self.hue_shift) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 1, led_brightness)
            for i in range(start, end):
                pixels[i] = (int(r * 255), int(g * 255), int(b * 255))

        pixels.write()
        pixels.show()

preset_lookup['letters'] = Preset_Letters


class Preset_RainbowRain(Preset_Rainbow):
    def __init__(self, parent_strip):
        super().__init__(parent_strip)
        self.dot_spacing = 50  # Spacing between dots
        self.dot_color = (0, 0, 0)  # Default color for the dots
        self.dot_speed = 0.05  # Speed of the dots
        self.dot_offset = 0  # Offset for the moving dots
        self.time_updated_dots = time.time()

        self.map_dispatcher()

    def map_dispatcher(self):
        super().map_dispatcher()
        self.parent_strip.dispatcher.map('/dot_spacing', self.receive_message)
        self.parent_strip.dispatcher.map('/dot_speed', self.receive_message)

    def receive_message(self, address: str, val: float, *args):
        super().receive_message(address, val, *args)
        if address == '/dot_spacing':
            self.dot_spacing = int(val)
        if address == '/dot_speed':
            self.dot_speed = val

    def set_pixels(self):
        pixels = self.parent_strip.pixels
        num_pixels = len(pixels)

        # Set the rainbow background
        for i in range(num_pixels):
            if i not in pixel_map_arr:
                continue
            i_hue = pixel_map_arr.index(i)
            hue = ((i_hue + self.offset) % self.wavelength) / self.wavelength
            r, g, b = colorsys.hsv_to_rgb(hue, 1, led_brightness)
            pixels[i] = (int(r * 255), int(g * 255), int(b * 255))

        # Update the offset for the rainbow animation
        current_time = time.time()
        if current_time - self.time_updated > self.wave_speed:
            self.time_updated = current_time
            self.offset += 1

        # Add moving dots in the opposite direction
        if current_time - self.time_updated_dots > self.dot_speed:
            self.time_updated_dots = current_time
            self.dot_offset = (self.dot_offset - 1) % self.dot_spacing

        for i in range(0, num_pixels, self.dot_spacing):
            dot_position = (i + self.dot_offset) % num_pixels
            pixels[dot_position] = self.dot_color

        pixels.write()
        pixels.show()


preset_lookup['rainbow_rain'] = Preset_RainbowRain

class Preset_Rainbombs:
    def __init__(self, parent_strip):
        self.parent_strip = parent_strip
        self.map_dispatcher()

        self.bomb_interval = 0.1  # Time between bombs
        self.bomb_speed = 0.05  # Speed of the expanding pixels
        self.bomb_lifetime = 50  # Number of frames for each bomb
        self.last_bomb_time = time.time()

        self.active_bombs = []  # List of active bombs [(position, frame_count)]

    def map_dispatcher(self):
        self.parent_strip.dispatcher.map('/bomb_interval', self.receive_message)
        self.parent_strip.dispatcher.map('/bomb_speed', self.receive_message)
        self.parent_strip.dispatcher.map('/bomb_lifetime', self.receive_message)

    def receive_message(self, address: str, val: float, *args):
        if address == '/bomb_interval':
            self.bomb_interval = val
        elif address == '/bomb_speed':
            self.bomb_speed = val
        elif address == '/bomb_lifetime':
            self.bomb_lifetime = int(val)

    def set_pixels(self):
        pixels = self.parent_strip.pixels
        num_pixels = len(pixels)

        # Check if it's time to spawn a new bomb
        current_time = time.time()
        if current_time - self.last_bomb_time >= self.bomb_interval:
            self.last_bomb_time = current_time
            bomb_position = random.randint(0, num_pixels - 1)
            self.active_bombs.append((bomb_position, 0))  # Add new bomb with frame count 0

        # Clear the strip
        for i in range(num_pixels):
            pixels[i] = (0, 0, 0)

        # Update and draw active bombs
        new_active_bombs = []
        for bomb_position, frame_count in self.active_bombs:
            if frame_count < self.bomb_lifetime:
                # Calculate the positions of the expanding pixels
                left_pixel = (bomb_position - frame_count) % num_pixels
                right_pixel = (bomb_position + frame_count) % num_pixels

                # Set the colors of the expanding pixels
                r, g, b = colorsys.hsv_to_rgb(frame_count / self.bomb_lifetime, 1, led_brightness)
                pixels[left_pixel] = (int(r * 255), int(g * 255), int(b * 255))
                pixels[right_pixel] = (int(r * 255), int(g * 255), int(b * 255))

                # Increment the frame count and keep the bomb active
                new_active_bombs.append((bomb_position, frame_count + 1))

        # Update the list of active bombs
        self.active_bombs = new_active_bombs

        # Write the updated pixel data
        pixels.write()
        pixels.show()


preset_lookup['rainbombs'] = Preset_Rainbombs


