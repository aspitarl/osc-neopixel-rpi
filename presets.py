import time
import colorsys
import random

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


## Presets
class PresetBase:
    def __init__(self, parent_strip, dispatch_map):
        self.parent_strip = parent_strip
        self.dispatch_map = dispatch_map

    def map_dispatcher(self):
        for address, attr in self.dispatch_map.items():
            self.parent_strip.dispatcher.map(address, self.receive_message)

    def receive_message(self, address: str, val: float, *args):
        if address in self.dispatch_map:
            setattr(self, self.dispatch_map[address], val)

class Preset_Monochrome(PresetBase):
    def __init__(self, parent_strip):
        dispatch_map = {
            '/param1': 'bright_mult',
            '/param2': 'hue_offset',
            '/param3': 'cycle_speed',
        }
        super().__init__(
            parent_strip,
            dispatch_map=dispatch_map
            )

        self.h = 0
        self.s = 1
        self.v = 0.5
        self.hue_offset = 0
        self.cycle_speed = 0.01  # Speed of hue cycling
        self.time_updated = time.time()  # Track the last update time
        self.bright_mult = 1.0  # Add bright_mult

    def set_pixels(self):
        # Update hue based on time and cycle speed
        current_time = time.time()
        self.h = (self.h + self.cycle_speed * (current_time - self.time_updated)) % 1.0
        self.time_updated = current_time

        r, g, b = colorsys.hsv_to_rgb(self.h + self.hue_offset, self.s, self.v)
        r = int(r * 255 * self.bright_mult)
        g = int(g * 255 * self.bright_mult)
        b = int(b * 255 * self.bright_mult)
        pixels = self.parent_strip.pixels
        
        for i in range(len(pixels)):
            pixels[i] = (r, g, b)

        pixels.show()

class Preset_Rainbow(PresetBase):
    def __init__(self, parent_strip):

        dispatch_map = {
            '/param1': 'bright_mult',
            '/param2': 'wavelength',
            '/param3': 'wave_speed',
            '/param4': 'wait_time',
        }
        super().__init__(
            parent_strip,
            dispatch_map=dispatch_map
            )

        self.wavelength_max = self.parent_strip.pixels.n*5
        self.wavelength = 0.25  # Default wavelength in fraction of the strip length
        self.offset = 0  # Offset for animation

        self.time_updated = time.time()

        self.wait_time = 0.01  # Speed of the wave animation
        self.wait_time_max = 0.1

        self.wave_speed_max = 50 # hue offset increment per frame
        self.wave_speed = 0.5  # Speed of the wave animation
        self.bright_mult = 1.0  # Add bright_mult

    def set_pixels(self):
        pixels = self.parent_strip.pixels
        num_pixels = len(pixels)
        
        wavelength_scaled = self.wavelength_max * self.wavelength  # Convert to pixel count
        wavelength_scaled = max(2, wavelength_scaled)  # Ensure it's at least 1 pixel

        for i in range(num_pixels):
            if i not in pixel_map_arr:
                continue
            i_hue = pixel_map_arr.index(i)
            hue = ((i_hue + self.offset) % wavelength_scaled) / wavelength_scaled
            r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
            r = int(r * 255 * self.bright_mult)
            g = int(g * 255 * self.bright_mult)
            b = int(b * 255 * self.bright_mult)
            pixels[i] = (r, g, b)

        pixels.show()

        wait_time_scaled = self.wait_time_max * self.wait_time  # Convert to pixel count
        wait_time_scaled = max(0.01, wait_time_scaled)  # Ensure it's at least 0.01 seconds
        wave_speed_scaled = self.wave_speed_max * self.wave_speed  # Convert to pixel count 
        wave_speed_scaled = max(0.01, wave_speed_scaled)  # Ensure it's at least 0.01 pixels
        # Update the offset for the next frame
        current_time = time.time()
        if current_time - self.time_updated > wait_time_scaled:
            self.time_updated = current_time
            self.offset += wave_speed_scaled
        # self.offset = (self.offset + 1) % self.wavelength


# Make a preset that sets each letter to a different color
# one parameter should be the hue shift per letter

class Preset_Letters(PresetBase):
    def __init__(self, parent_strip):
        dispatch_map = {
            '/param1': 'bright_mult',
            '/param2': 'hue_shift',
        }
        super().__init__(
            parent_strip,
            dispatch_map=dispatch_map
                         )

        self.hue_shift = 0.5/14  # Default hue shift per letter
        self.hue_shift_max = 1.0

        self.bright_mult = 1.0  # overall brightness

        self.idx_offset = 0  # Offset for animation
        self.time_updated = time.time()  # Track the last update time

        self.time_wait = 0.1  # Time to wait before updating the offset

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
            r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
            r = int(r * 255 * self.bright_mult)
            g = int(g * 255 * self.bright_mult)
            b = int(b * 255 * self.bright_mult)
            for i in range(start, end):
                pixels[i] = (r, g, b)

        pixels.show()


class Preset_RainbowRain(PresetBase):
    def __init__(self, parent_strip):
        dispatch_map = {
            '/param1': 'bright_mult',
            '/param2': 'dot_spacing',
        }
        super().__init__(
            parent_strip,
            dispatch_map=dispatch_map
            )

        self.wavelength_max = self.parent_strip.pixels.n*5
        self.wavelength = 0.25  # Default wavelength in fraction of the strip length
        self.offset = 0  # Offset for animation

        self.time_updated = time.time()

        self.wait_time = 0.01  # Speed of the wave animation
        self.wait_time_max = 0.1

        self.wave_speed_max = 50 # hue offset increment per frame
        self.wave_speed = 0.5  # Speed of the wave animation

        self.dot_spacing = 0.5  # Spacing between dots
        self.dot_spacing_max = 100  # Maximum spacing between dots
        self.dot_color = (0, 0, 0)  # Default color for the dots
        self.dot_speed = 0.05  # Speed of the dots
        self.dot_offset = 0  # Offset for the moving dots
        self.time_updated_dots = time.time()
        self.bright_mult = 1.0  # Add bright_mult

    def set_pixels(self):
        pixels = self.parent_strip.pixels
        num_pixels = len(pixels)

        # Set the rainbow background
        for i in range(num_pixels):
            if i not in pixel_map_arr:
                continue
            i_hue = pixel_map_arr.index(i)
            hue = ((i_hue + self.offset) % self.wavelength) / self.wavelength
            r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
            r = int(r * 255 * self.bright_mult)
            g = int(g * 255 * self.bright_mult)
            b = int(b * 255 * self.bright_mult)
            pixels[i] = (r, g, b)

        # Update the offset for the rainbow animation
        current_time = time.time()
        if current_time - self.time_updated > self.wait_time:
            self.time_updated = current_time
            self.offset += 1

        dot_spacing_scaled = int((self.dot_spacing_max * self.dot_spacing) + 2)  # Convert to pixel count
        # Add moving dots in the opposite direction
        if current_time - self.time_updated_dots > self.dot_speed:
            self.time_updated_dots = current_time
            self.dot_offset = (self.dot_offset - 1) % dot_spacing_scaled

        for i in range(0, num_pixels, dot_spacing_scaled):
            dot_position = (i + self.dot_offset) % num_pixels
            pixels[dot_position] = self.dot_color

        pixels.show()


class Preset_Rainbombs(PresetBase):
    def __init__(self, parent_strip):
        dispatch_map = {
            '/param1': 'bright_mult',
            '/param2': 'bomb_brightness',
            '/param3': 'bomb_size', 
            '/param4': 'background_hue_speed',
        }
        super().__init__(
            parent_strip,
            dispatch_map=dispatch_map
            )

        self.bomb_interval = 1  # Time between bombs
        self.bomb_speed = 0.25  # Speed of the expanding pixels
        self.bomb_lifetime = 5  # Number of frames for each bomb
        self.bomb_size = 0.5  # Exact number of pixels in the bomb
        self.bomb_size_scale = 5
        self.last_bomb_time = time.time()

        self.active_bombs = []  # List of active bombs [(position, frame_count, direction)]
        self.hue = 0  # Current hue for the bombs
        self.hue_speed = 0.0005  # Speed of hue shifting
        self.background_hue = 0.5  # Initial background hue
        self.background_hue_speed = 0.1  # Speed of background hue shifting
        self.background_hue_speed_scale = 0.05
        self.bg_led_brightness = 0.5  # Brightness of the background LEDs

        self.letter_phase_delay = {letter: random.uniform(0.1, 1.0) for letter in letter_lookup_dict}  # Random phase delay for each letter
        self.letter_last_bomb_time = {letter: time.time() for letter in letter_lookup_dict}  # Track last bomb time for each letter

        self.bomb_brightness = 1.0  # Default bomb brightness (scaled to led_brightness)
        self.bright_mult = 1.0  # Add bright_mult

    def set_pixels(self):
        pixels = self.parent_strip.pixels
        num_pixels = len(pixels)

        # Update the hue
        self.hue = (self.hue + self.hue_speed) % 1.0

        # Update the background hue
        self.background_hue = (self.background_hue + self.background_hue_speed*self.background_hue_speed_scale) % 1.0

        # Set the background hue
        bg_r, bg_g, bg_b = colorsys.hsv_to_rgb(self.background_hue, 1, self.bg_led_brightness)
        bg_r = int(bg_r * 255 * self.bright_mult)
        bg_g = int(bg_g * 255 * self.bright_mult)
        bg_b = int(bg_b * 255 * self.bright_mult)
        for i in range(num_pixels):
            pixels[i] = (bg_r, bg_g, bg_b)

        # Check if it's time to spawn a new bomb for each letter
        current_time = time.time()
        for letter, (start, end) in letter_lookup_dict.items():
            if current_time - self.letter_last_bomb_time[letter] >= self.letter_phase_delay[letter]:
                self.letter_last_bomb_time[letter] = current_time
                bomb_position = random.randint(start, end - 1)
                direction = random.choice([-1, 1])  # Random direction: -1 for left, 1 for right
                self.active_bombs.append((bomb_position, 0, direction))  # Add new bomb with direction

        bomb_size_scaled = int(self.bomb_size_scale * self.bomb_size)  # Convert to pixel count
        # Update and draw active bombs
        new_active_bombs = []
        r, g, b = colorsys.hsv_to_rgb(self.hue, 1, self.bomb_brightness)
        r = int(r * 255 * self.bright_mult)
        g = int(g * 255 * self.bright_mult)
        b = int(b * 255 * self.bright_mult)
        for bomb_position, frame_count, direction in self.active_bombs:
            if frame_count < self.bomb_lifetime:
                # Calculate the positions of the expanding pixels
                for offset in range(bomb_size_scaled):
                    pixel_position = (bomb_position + direction * (offset + frame_count)) % num_pixels
                    pixels[pixel_position] = (r, g, b)

                # Increment the frame count and keep the bomb active
                new_active_bombs.append((bomb_position, frame_count + 1, direction))

        # Update the list of active bombs
        self.active_bombs = new_active_bombs

        # Write the updated pixel data
        pixels.show()


