"""Small example OSC server

This program listens to several addresses, and prints some information about
received packets.
"""
import argparse

from pythonosc import dispatcher
from pythonosc import osc_server

import asyncio
import socket

from strip import StripOSCBridge


async def main_loop():
    while(True):
        my_strip.preset.set_pixels()
        await asyncio.sleep(0.03)

async def init_loop(ip, port):
    def set_preset_osc(self, address: str, val: str, *args):
        self.set_preset(val)
        print(f"Preset set to {val}") 
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
    parser.add_argument("--preset",
                        default="monochrome", help="The preset to use")
    ## TODO: how to get this dynamically? e.g. board.D18
    # parser.add_argument("--board_pin",
    #                     type=int, default=18, help="The GPIO pin to use")
    parser.add_argument("--num_pixels", '-n',
                        type=int, default=410, help="The number of pixels")
    args = parser.parse_args()

    dispatcher = dispatcher.Dispatcher()

    my_strip = StripOSCBridge(
                            dispatcher=dispatcher, 
                            preset=args.preset,
                            num_pixels=args.num_pixels
                            )

    print("Listening on {} port {}".format(args.ip, args.port))

    asyncio.run(init_loop(args.ip, args.port))
