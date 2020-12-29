#!/usr/bin/env python3
from math import floor
import argparse, os, tkinter
from tkinter import ttk
from PIL import Image,ImageDraw,ImageFont,ImageTk
from layout_dashboard import *
import time

parser = argparse.ArgumentParser()
parser.add_argument('--no-fullscreen', '-w', dest='fullscreen', action='store_false')
parser.add_argument('--fullscreen', '-f', dest='fullscreen', action='store_true')
parser.add_argument('--debug', '-d', dest='debug', action='store_true')
parser.set_defaults(fullscreen=False, debug=False)
args = parser.parse_args()


fnt = ImageFont.truetype("coda.regular.ttf", 78)

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

data = generateDisplayData(keys=['temp', 'humid'], font=fnt)

for i in data.keys():
#move this to its own display function and make it call itself with a scheduler
    data[i]['boxCoordinates'] = layout.coords[i]
    data[i]['textArea'] = getTextArea(layout, data[i]['boxCoordinates'])
    data[i]['pasteCoordinates'] = getCenteredPasteCoords(data[i]['textArea'], data[i]['img'])
    if args.debug:
        layout.draw.rectangle(data[i]['boxCoordinates'], outline='black', fill='white')
        layout.draw.rectangle(data[i]['textArea'], outline='black', fill='cadetblue')
    layout.image.alpha_composite(data[i]['img'], dest=data[i]['pasteCoordinates'])


readout = ImageTk.PhotoImage(image=layout.image)
image_label = tkinter.ttk.Label(root, image = readout)
image_label.place(x=0,y=0)

derp =ImageDraw.Draw(layout.image)
stuff = ['herp', 'derp', 'ooga', 'booga']

for i in stuff:
    derp.drawtext((500,500), text=i, font=fnt)
    time.sleep(1)
    root.update()

root.update()
root.mainloop()
