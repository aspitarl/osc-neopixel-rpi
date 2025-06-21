import csv

# Define the letter lookup dict as in presets.py
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

# Assign a unique color to each letter (cycling through a palette)
colors = [
    (255,0,0),    # red
    (0,255,0),    # green
    (0,0,255),    # blue
    (255,255,0),  # yellow
    (0,255,255),  # cyan
    (255,0,255),  # magenta
    (255,128,0),  # orange
    (128,0,255),  # purple
    (0,128,255),  # sky blue
    (128,255,0),  # lime
    (255,0,128),  # pink
    (0,255,128),  # aqua
    (128,128,128),# gray
    (255,255,255) # white
]

with open('letter_pixels.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['letter','pixel','r','g','b'])
    for idx, (letter, (start, end)) in enumerate(letter_lookup_dict.items()):
        color = colors[idx % len(colors)]
        for p in range(end-start):
            writer.writerow([letter, p, *color])
