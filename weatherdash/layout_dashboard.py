from PIL import Image,ImageDraw,ImageFont,ImageTk
import time
import mysql.connector as sql
from datetime import timedelta, datetime
from math import floor

class displayObject:
    def __init__(self, name, data, location, font):
        def drawText()
            tempImg = Image.new('1',(1,1), color=0)
            tempDraw = ImageDraw.Draw(tempImg)
            self.dimensions = tempDraw.textsize(data, fnt)
            self.img = Image.new('RGBA', self.dimensions, "pink")
            draw = ImageDraw.draw(self.img)
            draw.text((0,0), text=data, font=font, fill="black")


def getDataFromMysql(host="localhost", user="root", password=None, database="data", lookback=1, endTimeStamp=datetime.now(), dataSet="fuck"):
#it would be better if this picked arbitrary data from the database given a time range
    if(password is None):
        db = sql.connect(host=host, user=user, database=database)
    else:
        db = sql.connect(host=host, user=user, database=database, password=password)

    cursor = db.cursor()

    lookbackRange = lookback * timedelta(minutes=1)
    startTimeStamp = endTimeStamp - lookbackRange

    query = f'SELECT {dataSet} FROM readings WHERE timestamp >= "{startTimeStamp}" and timestamp <= "{endTimeStamp}"'
    cursor.execute(query)
    result = cursor.fetchall()
    val = 0
    n = 0
    for i in result:
        val += i[0]
        n += 1

    return ( val / n )

#define a class for display objects
#attributes: name (clock, temp, whatever), data, location (x,y), image data


def getTextArea(self, coords):
    boundryL = coords[0] + self.PadW
    boundryT = coords[1] + self.PadH
    boundryR = coords[2] - self.PadW
    boundryB = coords[3] - self.PadH
    return [boundryL, boundryT, boundryR, boundryB]


class Layout:
    def __init__(self, width, height, debug):

        self.image = Image.new('RGB', (width, height), 'slategrey')
        self.draw = ImageDraw.Draw(self.image)
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
        self.RIGHT = width - self.EdgeX - 1
        self.TOP = self.EdgeY
        self.BOTTOM = height - self.EdgeY - 1

        self.TotalWidth = self.RIGHT - self.LEFT
        self.TotalHeight = self.BOTTOM - self.TOP

        #Find how large each box can be
        self.BoxHeight = ( (self.TotalHeight - ( 2 * self.BufferH )) / 3 )

        #self.LPanW = getTextWidth(draw) + (2 * self.PadW)
        golden = ( 1 + 5 ** 0.5 ) / 2
        self.LPanW = self.BoxHeight * golden
        #Define how large each graph should be
        self.GraphW = self.TotalWidth - self.LPanW - self.BufferW
        self.Graph1H = ( self.TotalHeight / 2 ) - ( 2 * self.BufferH )
        self.Graph2H = ( self.TotalHeight / 3 ) - ( 2 * self.BufferH )
        self.Graph3H = self.TotalHeight - self.Graph1H - self.Graph2H - ( 2 * self.BufferH )

        #define coordinates for each box
        self.LPanL = self.LEFT
        self.LPanR = self.LPanL + self.LPanW
        self.ClockT = self.TOP
        self.ClockB = self.TOP + self.BoxHeight

        self.TempT = self.ClockB + self.BufferH
        self.TempB = self.TempT + self.BoxHeight

        self.HumidT = self.TempB + self.BufferH
        self.HumidB = self.HumidT + self.BoxHeight

        self.RPanL = self.LPanR + self.BufferW
        self.RPanR = self.RIGHT
        self.Graph1T = self.TOP
        self.Graph1B = self.Graph1T + self.Graph1H

        self.Graph2T = self.Graph1B + self.BufferH
        self.Graph2B = self.Graph2T + self.Graph2H

        self.Graph3T = self.Graph2B + self.BufferH
        self.Graph3B = self.BOTTOM

        self.coords = {
            'clock':    [self.LPanL, self.ClockT,  self.LPanR, self.ClockB],
            'temp':     [self.LPanL, self.TempT,   self.LPanR, self.TempB],
            'humid':    [self.LPanL, self.HumidT,  self.LPanR, self.HumidB],
            'graph1':   [self.RPanL, self.Graph1T, self.RPanR, self.Graph1B],
            'graph2':   [self.RPanL, self.Graph2T, self.RPanR, self.Graph2B],
            'graph3':   [self.RPanL, self.Graph3T, self.RPanR, self.BOTTOM],
        }

        boxes = ['clock', 'temp', 'humid', 'graph1', 'graph2', 'graph3']
        if debug:
            for obj in boxes:
                print(f"drawing: {obj}")
                self.draw.rectangle(self.coords[obj], outline="black", fill="white")
                self.draw.rectangle(getTextArea(self, self.coords[obj]), outline="black", fill="green")
