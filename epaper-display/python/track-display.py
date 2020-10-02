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

totalWidth=250
totalHeight=122

clockSize=36
emojiSize=20
infoSize=20
lenSize=12

#Define fonts
clockFont = ImageFont.truetype(os.path.join(picdir, 'Charcoal.ttf'), clockSize)
emojiFont = ImageFont.truetype(os.path.join(picdir, 'emoji.ttf'), emojiSize)
infoFont = ImageFont.truetype(os.path.join(picdir, 'Charcoal.ttf'), infoSize)
lenFont = ImageFont.truetype(os.path.join(picdir, 'Charcoal.ttf'), lenSize)

w = 5 #buffer


logging.basicConfig(level=logging.DEBUG)
try:
    logging.info("epd2in13_V2 Demo")

    epd = epd2in13_V2.EPD()
    logging.info("init and Clear")
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)

    #Define fonts
    clockFont = ImageFont.truetype(os.path.join(picdir, 'Charcoal.ttf'), clockSize)
    emojiFont = ImageFont.truetype(os.path.join(picdir, 'emoji.ttf'), emojiSize)
    infoFont = ImageFont.truetype(os.path.join(picdir, 'Charcoal.ttf'), infoSize)
    lenFont = ImageFont.truetype(os.path.join(picdir, 'Charcoal.ttf'), lenSize)

    logging.info("1.Drawing on the image...")
    image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(image)

    infoSize=20
    vera = ImageFont.truetype(os.path.join(picdir, 'Vera.ttf'), infoSize)


    clockSize=36

    li='Lorem ipsum dolor sit amet'
    clocktx='23:58'

    durationSize = 12

    (clW, clH) = draw.textsize(clocktx, clockft)

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
    draw.text((250-reW,122-5-reH-3), "-01:24", font=durationFont, fill=0)

    duStart = moW+duW+5+5
    duEnd = 250-reW-5-5
    duLen = duEnd - duStart
    duPct = (1 - (84/217.0) )*duLen
    print("duration bar: W{}".format(duLen))
    print("filled bar: W{}".format(duPct))

    bartop = (122 + clH + 2*moH - 5)/2
    barbottom = 122-5

#    draw.rectangle([(duStart,clH+2*moH+8),(duEnd,122)], outline=0, width=3)
#    draw.rectangle([(duStart,clH+2*moH+8),(duStart+duPct,clH+2*moH+29)], outline=0, width=3, fill=0)
    draw.rectangle([(duStart,bartop),(duEnd,barbottom)], outline=0, width=3)

    epd.display(epd.getbuffer(image))
    time.sleep(2000)

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
