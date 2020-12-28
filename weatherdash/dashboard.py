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


fnt = ImageFont.truetype("coda.regular.ttf", 40)

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

#do this before root.update()

#def generateDisplayData(keys):
##get this working, then move it to a different source file
#    data = {}
#
#    for i in keys:
#        data[i] = {}
#        data[i]['reading'] = getDataFromMysql(host="10.0.0.2", user="readonly", database="climate", lookback=5, dataSet=i)
#        print(data[i]['reading'])
#
#    data['temp']['display'] = "{}°F".format(tempConvert(temp=data['temp']['reading']))
#    data['humid']['display'] = "{}%".format(round(data['humid']['reading']))
#    data['clock'] = {'display': datetime.now().strftime("%H:%M")}
#
#
#    for i in data.keys():
#        txt = data[i]['display']
#        tmpLayer = Image.new('1', (0,0), 1)
#        tmpDraw  = ImageDraw.Draw(tmpLayer, '1')
#        dimensions = tmpDraw.textsize(txt, font=fnt)
#        data[i]['img'] = generateDisplayImg(data=txt, font=fnt, size=dimensions)
#    return data

data = generateDisplayData(keys=['temp', 'humid'], font=fnt)

for i in data.keys():
    data[i]['boxCoordinates'] = layout.coords[i]
    data[i]['textArea'] = getTextArea(layout, data[i]['boxCoordinates'])
    data[i]['pasteCoordinates'] = (data[i]['textArea'][0], data[i]['textArea'][1]) #this is maximum barf. Write a function to return this based on the boxCoordinates
    print(data[i]['pasteCoordinates'])
    if args.debug:
        layout.draw.rectangle(data[i]['boxCoordinates'], outline='black', fill='white')
        layout.draw.rectangle(data[i]['textArea'], outline='black', fill='cadetblue')
    layout.image.alpha_composite(data[i]['img'], dest=data[i]['pasteCoordinates'])


readout = ImageTk.PhotoImage(image=layout.image)
image_label = tkinter.ttk.Label(root, image = readout)
image_label.place(x=0,y=0)


root.update()
root.mainloop()
