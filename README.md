This is a script that listens to osc messages with names hue sat val and sets the color of a neopixels strip

to run:
`sudo .venv/bin/python neopx_osc.py --ip <RPI ip address> --port <OSC Port>`

find the raspberry pi address with `ifconfig`


## auto start

autostart file in /etc/systemd/system/neopx.service

sudo systemctl start neopx.service