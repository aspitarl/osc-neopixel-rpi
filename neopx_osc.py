"""Small example OSC server

This program listens to several addresses, and prints some information about
received packets.
"""
import argparse
import math

from pythonosc import dispatcher
from pythonosc import osc_server

import board
import neopixel
import colorsys

import asyncio
import socket

class MyStrip():
    def __init__(self):
        self.h = 0
        self.s = 1
        self.v = 1
        self.pixels = neopixel.NeoPixel(board.D18,30)


    def set_hsv(self, address: str, val: float, *args):
        #if len(args):
        #    print('got wrong number arguments')
        #    print('val: {}'.format(val))
        #    print('args: {}'.format(args))

        if address == '/hue':
            self.h = val
        if address == '/sat':
            self.s = val
        if address == '/val':
            self.v = val

    def set_pixels(self):
        r,g,b =  colorsys.hsv_to_rgb(self.h, self.s, self.v)
        
        for i in range(len(self.pixels)):
            self.pixels[i] = (r*255,g*255,b*255)
        self.pixels.show()


async def main_loop():
    while(True):
        my_strip.set_pixels()
        await asyncio.sleep(0.02)

async def init_loop(ip, port):
 
    server = osc_server.AsyncIOOSCUDPServer(
        (ip, port), dispatcher, asyncio.get_event_loop())


    transport, protocol = await server.create_serve_endpoint()
    
    await main_loop()
    
    transport.close()


def get_default_IP():

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Connect to an external address to determine the local IP
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    


    parser.add_argument("--ip",
                        default=get_default_IP(), help="The ip to listen on")
    parser.add_argument("--port",
                        type=int, default=5000, help="The port to listen on")
    args = parser.parse_args()

    dispatcher = dispatcher.Dispatcher()

    my_strip = MyStrip()
    dispatcher.map("/hue", my_strip.set_hsv)
    dispatcher.map("/sat", my_strip.set_hsv)
    dispatcher.map("/val", my_strip.set_hsv)

    print("Listening on {} port {}".format(args.ip, args.port))

    asyncio.run(init_loop(args.ip, args.port))
