#!/usr/bin/env python3

import tkinter
from tkinter.font import Font
from PIL import Image, ImageTk
fontdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'fonts')

clockTx = "88:88"
clockSz=36
clockFt = ImageFont.truetype(os.path.join(fontdir, 'Charcoal.ttf'), clockSz)

tempTx = "188F"
tempSz = clockSz
tempFt = ClockFt

humidTx = "100%"


root = tkinter.Tk()
width = root.winfo_screenwidth()
height = root.winfo_screenheight()


root.mainloop()
