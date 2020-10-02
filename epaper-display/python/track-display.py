#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
resourcePath = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
picdir = os.path.join(resourcePath, 'pic')
libdir = os.path.join(resourcePath, 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in13_V2
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
from datetime import datetime

totalWidth=250
totalHeight=122

#define text sizes
clockSize=36
emojiSize=20
infoSize=20
lenSize=12

#Define fonts
#the numeral glyphs in Charcoal are all the same width
clockFont = ImageFont.truetype(os.path.join(picdir, 'Charcoal.ttf'), clockSize)
emojiFont = ImageFont.truetype(os.path.join(picdir, 'emoji.ttf'), emojiSize)
infoFont = ImageFont.truetype(os.path.join(picdir, 'Charcoal.ttf'), infoSize)
lenFont = ImageFont.truetype(os.path.join(picdir, 'Charcoal.ttf'), lenSize)

w = 5 #buffer

logging.basicConfig(level=logging.INFO)

class Track:
    def __init__(self):
        self.Artist = "Ay I is Artist!"
        self.Title = "Eg herp derp?"
        self.Duration = 384
        self.Position = 123

def main():
    #initialize the display
    logging.info("epd2in13_V2 Demo")
    epd = epd2in13_V2.EPD()
    logging.info("init and Clear")
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)

    logging.info("1.Drawing on the image...")
    image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(image)

    logging.info("Create all of the text objects")

    artMoji = u'🎤'
    titMoji = u'🎼'
    durMoji = u'⏳'

    clockTx = getClockString()
    logging.info("{}".format(clockTx))

    baseInfo = Track()
    logging.info("A:{}\n\tT:{}".format(baseInfo.Artist, baseInfo.Title))
    (durationTx, remainingTx) = getDurationInfo(baseInfo.Duration, baseInfo.Position)
    logging.info("{}, {}".format(durationTx, remainingTx))

    logging.info("Time to start measuring things.")
    (clW, clH) = draw.textsize(clockTx, clockFont)
    (moW, moH) = draw.textSize(artMoji, mojiFont)
    (arW, arH) = draw.textsize(baseInfo.Artist, infoFont)
    (tiW, tiH) = draw.textsize(baseInfo.Title, infoFont)
    (duW, duH) = draw.textsize(durationTx, lenFont)
    (reW, reH) = draw.textsize(remainingTx, lenFont)


    print("clock: W:{} H:{}".format(clW,clH))
    print("headers: W:{} H:{}".format(moW,moH))
    print("artist: W:{} H:{}".format(arW,arH))
    print("title: W:{} H:{}".format(tiW,tiH))
    print("duration: W:{} H:{}".format(duW,duH))
    print("remaining: W:{} H:{}".format(reW,reH))

    #draw row headers
#    moW,moH = draw.textsize(emoji1Line,emojifont)
#    draw.rectangle([(0,clH),(moW,clH+moH)],outline=0)     # mic
#    draw.rectangle([(0,clH),(moW,clH+2*moH+4)],outline=0)  #note
#    draw.rectangle([(0,clH),(moW,clH+3*moH+8)],outline=0)  #timer

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

def getClockString():
    t= datetime.now()
    text = t.strftime("%H:%M")

def check_clock_text(font):
    #basically check to see if the font has monospace numeral glyphs
    image = Image.new('1', (122, 250), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(image)
    i=0
    maxW = 0
    while i < 60:
        j=0
        while j < 60:
            clockTx = "{:02d}:{:02d}".format(i, j)
            (clW, clH) = draw.textsize(clockTx, font)
            maxW = max(clW,maxW)
            print(maxW)
            j+=1
        i+=1

def getDurationInfo(du, po):
    duMin = du // 60
    duSec = du % 60
    durationTx = "{:02d}:{:02d}".format(duMin, duSec)

    remaining = du - po
    reMin = remaining // 60
    reSec = remaining % 60
    remainingTx = "-{:02d}:{:02d}".format(reMin, reSec)
    return (durationTx, remainingTx)

if __name__ == '__main__':
    try:
        main()

    except IOError as e:
        logging.info(e)

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd2in13_V2.epdconfig.module_exit()
        exit()
