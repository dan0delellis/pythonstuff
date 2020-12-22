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

fnt = ImageFont.truetype("Charcoal.ttf", 40)

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
layout = Layout(width, height, args.debug)

readout = ImageTk.PhotoImage(image=layout.image)
image_label = tkinter.ttk.Label(root, image = readout)
image_label.place(x=0,y=0)
#i=0
#while (i<100):
#    image = Image.new('RGB', (100,100), "pink")
#    draw = ImageDraw.Draw(image, 'RGB')
#    draw.text((0,0), text=f"{i}", font=fnt, fill="black")
#    readout.paste(image)
#    i+=1
#    root.update()
#    time.sleep(1)

data = {
#this would be better if I made a 'BoxItem' class and wrote a constructor
    'temp': {},
    'humid': {},
    }

for i in data.keys():
    print(i)
    data[i]['reading'] = getDataFromMysql(host="10.0.0.2", user="readonly", database="climate", lookback=5, dataSet=i)


data['clock'] = {'reading': datetime.now().strftime("%H:%M")}

for i in data.keys():
    tempImg = Image.new('1',(1,1), color=0)
    tempDraw = ImageDraw.Draw(tempImg)
    data[i]['dimensions'] = tempDraw.textsize(f"{data[i]['reading']}", fnt)
    data[i]['img'] = #write a function that will generate a text image object

root.update()
root.mainloop()
