#!/usr/bin/env python3

from math import floor
import argparse, os, tkinter, time, schedule
from tkinter import ttk
from PIL import Image,ImageDraw,ImageFont,ImageTk
from layout_dashboard import *

parser = argparse.ArgumentParser()
parser.add_argument('--no-fullscreen', '-w', dest='fullscreen', action='store_false')
parser.add_argument('--fullscreen', '-f', dest='fullscreen', action='store_true')
parser.add_argument('--debug', '-d', dest='debug', action='store_true')
parser.set_defaults(fullscreen=False, debug=False)
args = parser.parse_args()

if(args.debug):
    delay = 1
else:
    delay = 60

fnt = ImageFont.truetype("coda.regular.ttf", 100)

#how to do transparencies:
#define a canvass based on width, height as defined above. type RGBA.
#either write directly onto the canvass with an imagedraw.draw type RGBA,
#or, generate a new RGBA image and draw on that, paste it onto a blank layer and do
#canvas = image.composite_alpha(canvass, pasteLayer)

#define display
root = tkinter.Tk()
width = 800
height = 480

screenWidth = root.winfo_screenwidth()
screenHeight = root.winfo_screenheight()

if args.fullscreen:
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
else:
    width = floor(root.winfo_screenwidth() / 2)
    height = floor(root.winfo_screenheight() / 2)

root.geometry(f"{width}x{height}")

#create layout object
layout = Layout(width, height)
data = generateDisplayData(keys=['temp', 'humid'], font=fnt, debug=args.debug)
layout.image = displayDash(layout, data, args.debug)

readout = ImageTk.PhotoImage(image=layout.image)
image_label = tkinter.ttk.Label(root, image = readout)
image_label.place(x=0,y=0)
root.update()

#wait until wallclock time rolls over to update the display the first time
def updateDisplay():
    data = generateDisplayData(keys=['temp', 'humid'], font=fnt, debug=args.debug)
    layout.image = displayDash(layout, data, args.debug)
    readout.paste(layout.image)
    root.update()
    print(time.time())

#This is dumb as hell but honestly it works better than any scheduler so ¯\_(ツ)_/¯
while True:
    if(time.strftime("%S") == "00"):
        updateDisplay()
        time.sleep(50.0)
    else:
        time.sleep(0.9)

root.mainloop()
