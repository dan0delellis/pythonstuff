#!/usr/bin/env python3
import os
import tkinter
from tkinter.font import Font
from PIL import Image,ImageDraw,ImageFont,ImageTk

clockTx = "88:88"
clockSz=36
clockFt = ImageFont.truetype('Charcoal.ttf', clockSz)

tempTx = "888F"
tempSz = clockSz
tempFt = clockFt

humidTx = "888%"
tempSz = clockSz
tempFt = clockFt

#define display
root = tkinter.Tk()
width = root.winfo_screenwidth()
height = root.winfo_screenheight()

class Layout:
    #####################################################
    #                                                   #
    #     Yx      Ax  Bx                          Zx    #
    #    +----------------------------------------+Uy   #
    #    |       |_W_|                            |     #
    #    | 12:34 |   |                            |     #
    #  Cy|_______|   |      graph                 |     #
    #  Dy|-------|   |____________________________|Gy   #
    #    | 123F  |   |----------------------------|Hy   #
    #  Ey|_______|   |         graph?             |     #
    #  Fy|-------|   |____________________________|Iy   #
    #    | 23%   |   |----------------------------|Jy   #
    #    |       |   |           ?????            |     #
    #    +----------------------------------------+Vy   #
    #                                                   #
    #####################################################

#Yx = left edge + edge buffer width                         (LEFT)      =   (LPanL)
#Ax = edge of left panel                                    (LPanR)
#Bx = edge of left panel + buffer width                     (RPanL)
#Zx = right edge - edge buffer width                        (RIGHT)     =   (RPanR)
#Uy = top + edge buffer height                              (TOP)       =   (ClockT)    =   (Graph1T)
#Cy = bottom of clock area                                  (ClockB)
#Dy = top of temp area = Cy+vbuffer height                  (TempT)
#Ey = bottom of temp area                                   (TempB)
#Fy = top of humidty area  = Ey + vbuffer height            (HumidT)
#Gy = bottom of top graph                                   (Graph1B)
#Hy = top of middle graph = Gy + vbuffer                    (Graph2T)
#Iy = bottom of middle graph                                (Graph2B)
#Jy = top of bottom area                                    (Graph3T)
#Vy = bottom - edge buffer height                           (BOTTOM)    =   (HumidB)    =   (Graph3B)

    def __init__(self, clockW, clockH, tempW, tempH, humidW, humidH):
        #define buffer sizes

        #Edge buffer sizes
        self.EdgeX = 5
        self.EdgeY = 5

        #inter-space buffers
        self.BufferW = 10
        self.BufferH = 10

        #Minimum buffers around text
        self.PadW = 20
        self.PadH = 20

        #Edges
        self.LEFT = self.EdgeX
        self.RIGHT = width - self.EdgeX
        self.TOP = self.EdgeY
        self.BOTTOM = height - self.EdgeY

        self.TotalWidth = self.RIGHT - self.LEFT
        self.TotalHeight = self.BOTTOM - self.TOP

        #Find widest of clock, temp, humidity.  That's the left panel width (plus some buffer space around the text and edge buffer)
        self.LPanW = max(clockW, tempW, humidW) + (2 * self.PadW)

        #Find how large each box can be
        self.BoxHeight = (self.TotalHeight / 3 ) - ( 2 * self.BufferH)

        #Define how large each graph should be
        self.GraphW = self.TotalWidth - self.LPanW - self.BufferW
        self.Graph1H = ( self.TotalHeight / 2 ) - ( 2 * self.BufferH )
        self.Graph2H = ( self.TotalHeight / 3 ) - ( 2 * self.BufferH )
        self.Graph3H = self.TotalHeight - self.Graph1 - self.Graph2 - ( 2 * self.BufferH )

        #define coordinates for each box
        self.LPanL = self.LEFT
        self.LPanR = self.LPanL + self.LPanW
        self.ClockT = self.TOP
        self.ClockB = self.TOP + self.BoxHeight

        self.TempT = self.ClockB + self.BufferH
        self.TempB = self.ClockB + self.BoxHeight

        self.HumidT = self.TempB + self.BufferH
        self.HumidB = self.BOTTOM

        self.Graph1T = self.TOP
        self.Graph1B = self.Graph1T + self.Graph1H

        self.Graph2T = self.Graph1B + self.BufferH
        self.Graph2B = self.Graph2T + self.Graph2H

        self.Graph3T = self.Graph2B + self.BufferH
        self.Graph3B = BOTTOM

        #function to return coordinates to make life easier when drawing boxes
        def getCoords(obj):
            coords = {
                'clock':    [self.LPanL, self.ClockT, self.LPanR, self.ClockB],
                'temp':     [self.LPanL, self.TempT, self.LPanR, self.TempB],
                'humid':    [self.LPanL, self.HumidT, self.LPanR, self.HumidB],
                'graph1':   [self.LPanL, self.ClockT, self.LPanR, self.ClockB],
                'graph2':   [self.LPanL, self.ClockT, self.LPanR, self.ClockB],
                'graph3':   [self.LPanL, self.ClockT, self.LPanR, self.ClockB],
            }
            return coords[obj]

        #functions to draw boxes

        #functions to write text

        #functions to generate graphs





root.mainloop()
