"""Small example OSC server

This program listens to several addresses, and prints some information about
received packets.
"""
import argparse

from pythonosc import dispatcher
from pythonosc import osc_server

import asyncio
import socket

from strip import MyStrip


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
