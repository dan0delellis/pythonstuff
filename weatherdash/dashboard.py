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


#define display
root = tkinter.Tk()
width = 800
height = 480

fnt = ImageFont.truetype("coda.regular.ttf", 40)

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

readout = ImageTk.PhotoImage(image=layout.image)
image_label = tkinter.ttk.Label(root, image = readout)
image_label.place(x=0,y=0)

data = {
#this would be better if I made a 'BoxItem' class and wrote a constructor
    'temp': {},
    'humid': {},
    }

for i in data.keys():
    data[i]['reading'] = getDataFromMysql(host="10.0.0.2", user="readonly", database="climate", lookback=5, dataSet=i)


data['temp']['display'] = "{}°F".format(tempConvert(temp=data['temp']['reading']))
data['humid']['display'] = "{}%".format(round(data['humid']['reading']))
data['clock'] = {'display': datetime.now().strftime("%H:%M")}

#make a paste layer because PhotoImage doesn't support locational pasting
pasteLayer = Image.new('RGB', (readout.width(), readout.height()), (0,0,255))
pasteDraw = ImageDraw.Draw(pasteLayer)

if args.debug:
     boxes = ['clock', 'temp', 'humid', 'graph1', 'graph2', 'graph3']
     for obj in boxes:
        print(f"drawing: {obj}")
        coords = layout.coords[obj]
        pasteDraw.rectangle(coords, outline="black", fill="white")
        pasteDraw.rectangle(getTextArea(layout, coords), outline="black", fill="green")
     readout.paste(pasteLayer, (0,0))

for i in data.keys():
    data[i]['obj'] = displayObject(name=i, data=data[i]['display'], font=fnt, img=pasteLayer)
    pasteLayer = Image.alpha_composite(pasteLayer, data[i]['obj'])

readout.paste(pasteLayer, (0,0))


root.update()
root.mainloop()
