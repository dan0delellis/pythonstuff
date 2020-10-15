#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in13_V2
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
import redis

TW = 250
TH = 122

logging.basicConfig(level=logging.DEBUG)

#initialize redis
r = redis.Redis(host='10.0.0.2', port=6379, db=10)

#define fonts
emojiSize = 20
emojiFont = ImageFont.truetype(os.path.join(picdir, 'emoji.ttf'), 20)
emojiText = u'🎤'

infoSize = 20
infoFont = ImageFont.truetype(os.path.join(picdir, 'Charcoal.ttf'), infoSize)

clockSize=36
clockFont = ImageFont.truetype(os.path.join(picdir, 'Charcoal.ttf'), clockSize)
clockText = "88:88"

durationSize = 12
durationFont = ImageFont.truetype(os.path.join(picdir, 'Charcoal.ttf'), durationSize)
durationText = "88:88"
remainingText = "-88:88"

class Layout:
#Layout of display:
# W = buffer width                                      V = buffer height = ((TH-Cy)/3)-MojiH
# Ax = Horizontal Offset of Clock = (TW-clockW)/2;      Bx = End of Clock
# Dx = Horizontal End of Row Headers;                   Gx = Horizontal offset of track info = Dx+W
# Cy = Bottom of Clock                                  Ey = Bottom of First Row = Cy+MojiH+V                   Fy = Bottom of 2nd Row = Ey+MojiH+V     Jy=TH
# Kx = Horizontal Offset of Duration bar = Dx+2W        Mx = Horizontal Offset of remaining = TW-[remain]-W     Nx = End of Prog bar = Mx-W
#                   Ax      Bx
#+-------------------------------------------------+
#|                  | 12:34 |                      |
#|____Dx__Gx________|_______|______________________|Cy
#|arts|   |                                     _V_|
#|____|_W_|_____ARTIST INFO________________________|Ey
#|titl|   |                                     _V_|
#|____|_W_|_____TITLE INFO_________________________|Fy
#|time|   |     |  |                 |  |       _V_|
#|____|_W_|Drtn_|W_[=====PRG BAR=====]_W|__|Rmn_|W_|Jy
#                  Kx              Nx       Mx
    def __init__(self, clockW, clockH, mojiW, mojiH, durationW, remainW, timerH):
        self.bufferW = 5
        self.bufferH = ((TH-clockH)/3) - MojiH

        self.ClockX = (TW - clockW)/2
        self.ClockY = 0
        self.ClockBottom = self.ClockY + clockH
        def drawClockBox(self):
            draw.rectangle([self.ClockX, self.ClockY, (self.ClockX+clockW), self.clockBottom],outline=0)

        self.MojiX = 0
        self.MojiEnd = self.MojiX + mojiW
        self.Row1Y = self.ClockBottom + mojiH + bufferH
        self.Row2Y = Row1Y + bufferH + mojiH
        self.Row3Y = Row2Y + bufferH + mojiH

        def drawHeaderBoxes(self):
            draw.rectangle([self.MojiX, (self.ClockBottom+self.bufferH), self.MojiEnd, self.Row1Y], outline=0) #top header
            draw.rectangle([self.MojiX, (self.Row1Y+self.bufferH), self.mojiEnd, self.Row2Y], outline=0) #middle header
            draw.rectangle([self.MojiX, (self.Row2Y+self.bufferH), self.mojiEnd, self.Row3Y], outline=0) #bottom header

        self.InfoX = self.mojiEnd + bufferW

        def drawInfoBoxes(self):
            draw.rectangle([self.InfoX, (self.ClockY+clockH+self.bufferH), TW-1, self.Row1Y], outline=0) #top info, artist
            draw.rectangle([self.InfoX, (self.Row1Y+bufferH), TW-1, self.Row2Y], outline=0)  #middle info, title
            draw.rectangle([self.InfoX, (self.Row2Y+bufferH), TW-1, self.Row3Y], outline=0) #bottom info, duration info

        self.DrtnX = self.InfoX
        self.PrgSX = self.InfoX + durationW + bufferW
        self.RemnX = TW - remainW - bufferW
        self.PrgEX = self.RemnX - bufferW
        self.PrgH = TH - mojiH - bufferH

try:
    logging.info("epd2in13_V2 Demo")

    epd = epd2in13_V2.EPD()
    logging.info("init and Clear")
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)

    logging.info("1.Drawing on the image...")

    image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(image)

    (clockW, clockH) = draw.textsize(clockText, clockFont)
    (mojiW, mojiH) = draw.textsize(emojiText, emojiFont)
    (durationW, durationH) = draw.textsize(durationText, durationSize)
    (remainingW, remainingH) = draw.textsize(remainingW, remainingH)

    grid = Layout(clockW, clockH, mojiW, mojiH, durationW, remainingW, durationH)

    print("clock: {} {}".format(clW, clH))
    leftBuffer = (totalWidth - clW)/2
    rightBuffer = clW + leftBuffer

    #draw clock
#    draw.rectangle([(0,0),(249, clH)],outline=0)
#    draw.rectangle([(0,0),(leftBuffer,clH)],outline=0)
#    draw.rectangle([(rightBuffer,0),(totalWidth,clH)],outline=0)
    draw.text((leftBuffer,-4),clocktx, font = clockft, fill=0)

    #draw row headers
    emoji1Line = u'🎤'
    moW,moH = draw.textsize(emoji1Line,emojifont)
#    draw.rectangle([(0,clH),(moW,clH+moH)],outline=0)     # mic
#    draw.rectangle([(0,clH),(moW,clH+2*moH+4)],outline=0)  #note
#    draw.rectangle([(0,clH),(moW,clH+3*moH+8)],outline=0)  #timer

    headersTx = u'🎤\n🎼\n⏳'
    hdW, hdH = draw.textsize(headersTx, emojifont)
    print("1 emoji: w{}  h{}".format(moW, moH))
    print("all head: w{} h{}".format(hdW, hdH))

#    draw.rectangle([(0,clH),(hdW,121)],outline=0)


    draw.text((0, clH-2), u'🎤\n🎼\n⏳', font = emojifont, fill = 0)

    #write info:
    (ifW,ifH) = draw.textsize(li, vera)
    print("Text: W{},H{}".format(ifW,ifH))
#    draw.rectangle([(moW,clH),(249,clH+moH)],outline=0)
#    draw.rectangle([(moW,clH+moH),(249,clH+2*moH+4)],outline=0)
#    draw.rectangle([(moW,clH+2*moH+4),(249,clH+3*moH+10)],outline=0)

    draw.text((moW+4,clH+2),"Beady Eye", font = chicago, fill=0)
    draw.text((moW+4,clH+moH+4), "I need a title with g", font=chicago, fill=0)
    draw.text((moW+4,clH+2*moH+17), "03:37", font=durationFont, fill=0)

    (duW,duH) = draw.textsize("03:37", durationFont)
    print("duration: W{} H{}".format(duW,duH))

    (reW,reH) = draw.textsize("-01:24", durationFont)
    print("remaining: W{} H{}".format(reW,reH))
    draw.text((250-reW-5,clH+2*moH+17), "-01:24", font=durationFont, fill=0)

    duStart = moW+duW+5+5
    duEnd = 250-reW-5-5
    duLen = duEnd - duStart
    duPct = (1 - (84/217.0) )*duLen
    print("duration bar: W{}".format(duLen))
    print("filled bar: W{}".format(duPct))

    draw.rectangle([(duStart,clH+2*moH+8),(duEnd,clH+2*moH+29)], outline=0, width=3)
    draw.rectangle([(duStart,clH+2*moH+8),(duStart+duPct,clH+2*moH+29)], outline=0, width=3, fill=0)

    epd.display(epd.getbuffer(image))
    time.sleep(2000)

    # read bmp file
    logging.info("2.read bmp file...")
    image = Image.open(os.path.join(picdir, '2in13.bmp'))
    epd.display(epd.getbuffer(image))
    time.sleep(2)

    # read bmp file on window
    logging.info("3.read bmp file on window...")
    # epd.Clear(0xFF)
    image1 = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    bmp = Image.open(os.path.join(picdir, '100x100.bmp'))
    image1.paste(bmp, (2,2))
    epd.display(epd.getbuffer(image1))
    time.sleep(2)

    # # partial update
    logging.info("4.show time...")
    time_image = Image.new('1', (epd.height, epd.width), 255)
    time_draw = ImageDraw.Draw(time_image)

    epd.init(epd.FULL_UPDATE)
    epd.displayPartBaseImage(epd.getbuffer(time_image))

    epd.init(epd.PART_UPDATE)
    num = 0
    while (True):
        time_draw.rectangle((120, 80, 220, 105), fill = 255)
        time_draw.text((120, 80), time.strftime('%H:%M:%S'), font = font24, fill = 0)
        epd.displayPartial(epd.getbuffer(time_image))
        num = num + 1
        if(num == 10):
            break

    logging.info("Clear...")
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)

    logging.info("Goto Sleep...")
    epd.sleep()
    epd.Dev_exit()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd2in13_V2.epdconfig.module_exit()
    exit()
