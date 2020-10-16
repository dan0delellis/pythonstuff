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
import pickle

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
        self.bufferH = ((TH-clockH)/3) - mojiH

        self.ClockL = (TW - clockW)/2
        self.ClockR = self.ClockL + clockW
        self.ClockT = -4
        self.ClockB = self.ClockT + clockH

        self.MojiL = 0
        self.MojiR = self.MojiL + mojiW
        self.Row1T = self.ClockB + self.bufferH
        self.Row1B = self.Row1T + mojiH
        self.Row2T = self.Row1B + self.bufferH 
        self.Row2B = self.Row2T + mojiH  
        self.Row3T = self.Row2B + self.bufferH 
        self.Row3B = self.Row3T + mojiH 

        self.InfoL = self.MojiR + self.bufferW

        self.DrtnL = self.InfoL
        self.DrtnR = self.DrtnL + durationW
        self.DrtnT = self.Row3B - durationH
        self.DrtnB = self.Row3B
        self.RemnR = TW - self.bufferW
        self.RemnL = self.RemnR - remainW
        self.PrgL = self.DrtnR + self.bufferW
        self.PrgR = self.RemnL - self.bufferW
        self.PrgT = self.Row3T + self.bufferH
        self.PrgB = self.Row3B - self.bufferH

    def drawClockBox(self):
        draw.rectangle([self.ClockL, self.ClockT, self.ClockR, self.ClockB], outline=0)

    def drawHeaderBoxes(self):
        draw.rectangle([self.MojiL, self.Row1T, self.MojiR, self.Row1B], outline=0) #top header
        draw.rectangle([self.MojiL, self.Row2T, self.MojiR, self.Row2B], outline=0) #middle header
        draw.rectangle([self.MojiL, self.Row3T, self.MojiR, self.Row3B], outline=0) #bottom header

    def drawInfoBoxes(self):
        draw.rectangle([self.InfoL, self.Row1T, TW-1, self.Row1B], outline=0) #top info, artist
        draw.rectangle([self.InfoL, self.Row2T, TW-1, self.Row2B], outline=0)  #middle info, title
        draw.rectangle([self.InfoL, self.Row3T, TW-1, self.Row3B], outline=0) #bottom info, duration info

    def drawDurationBoxes(self):
        draw.rectangle([self.DrtnL, self.DrtnT, self.DrtnR, self.Row3B], outline=0)
        draw.rectangle([self.RemnL, self.DrtnT, self.RemnR, self.Row3B], outline=0)

    def drawProgressBar(self, ratio):
        self.Size = self.PrgR - self.PrgL
        self.Fill= ( ratio * self.Size ) + self.PrgL
        draw.rectangle([self.PrgL, self.PrgT, self.PrgR, self.PrgB], outline=0)
        draw.rectangle([self.PrgL, self.PrgT, self.Fill, self.PrgB], fill=0)

    def writeClock(self, text, fnt):
        draw.text((self.ClockL, self.ClockT), text, font=fnt, fill=0)

    def writeHeaders(self, artist, title, counter, fnt):
        draw.text((self.MojiL, self.Row1T), artist, font=fnt, fill=0)
        draw.text((self.MojiL, self.Row2T), title, font=fnt, fill=0)
        draw.text((self.MojiL, self.Row3T), counter, font=fnt, fill=0)

    def writeInfo(self, artist, title, fnt):
        draw.text((self.InfoL, self.Row1T), artist, font=fnt, fill=0)
        draw.text((self.InfoL, self.Row2T), title, font=fnt, fill=0)

    def writeDuration(self, length, elapsed, fnt):
        def convertToHMS(duration):
            seconds = duration
            hours = seconds // 3600
            seconds %= 3600 
            minutes = seconds // 60
            seconds %= 60
            if int(duration) >= 3600:
                return "%d:%02d:%02d" % (hours, minutes, seconds) 
            return "%02d:%02d" % (minutes, seconds)
        
        timeString = convertToHMS(int(length))
        draw.text((self.DrtnL, self.DrtnT), timeString, font=fnt, fill=0)
 
        remainString = convertToHMS( int(length) - int(elapsed) )
        remainString = "-{}".format(remainString)
        draw.text((self.RemnL, self.DrtnT), remainString, font=fnt, fill=0)


try:
    logging.info("epd2in13_V2 Demo")

    epd = epd2in13_V2.EPD()
    logging.info("init and Clear")
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)

    logging.info("1.Drawing on the image...")
    image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(image)

    #define element sizes
    (clockW, clockH) = draw.textsize(clockText, clockFont)
    (mojiW, mojiH) = draw.textsize(emojiText, emojiFont)
    (durationW, durationH) = draw.textsize(durationText, durationFont)
    (remainingW, remainingH) = draw.textsize(remainingText, durationFont)

    grid = Layout(clockW, clockH, mojiW, mojiH, durationW, remainingW, durationH)
    #grid.drawClockBox()
    #grid.drawHeaderBoxes()
    #grid.drawInfoBoxes()
    #grid.drawDurationBoxes()

    #draw clock
    timestamp = time.strftime('%H:%M')
    grid.writeClock(timestamp, clockFont)

    #draw row headers
    artist = u'🎤'
    title = u'🎼'
    counter = u'⏳'
    grid.writeHeaders(artist, title, counter, emojiFont)

    #get track info
    trackInfo = r.get('track_info') 
    dataUnpacked = pickle.loads(trackInfo)

    grid.writeInfo(dataUnpacked['artist'], dataUnpacked['title'], infoFont)
    grid.writeDuration(dataUnpacked['length'], dataUnpacked['time'], durationFont)
    grid.drawProgressBar(dataUnpacked['position'])

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
