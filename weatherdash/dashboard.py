#!/usr/bin/env python3
from math import floor
import argparse, os, tkinter
from tkinter import ttk
from tkinter.font import Font
from PIL import Image,ImageDraw,ImageFont,ImageTk
from layout_dashboard import Layout

parser = argparse.ArgumentParser()
parser.add_argument('--no-fullscreen', '-w', dest='fullscreen', action='store_false')
parser.add_argument('--fullscreen', '-f', dest='fullscreen', action='store_true')
parser.set_defaults(fullscreen=False)
args = parser.parse_args()

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

layout = Layout(width, height)

readout = ImageTk.PhotoImage(image=layout.image)
image_label = tkinter.ttk.Label(root, image = readout)
image_label.place(x=0,y=0)
root.mainloop()
