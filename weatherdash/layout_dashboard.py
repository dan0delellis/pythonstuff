from PIL import Image,ImageDraw,ImageFont,ImageTk
import time
import mysql.connector as sql
from datetime import timedelta, datetime
from math import floor

def generateDisplayImg(data, font, size):
#it might be worth it to make this a class instead, like 'DisplayObject', but only if the class contains:
#1) source data
#2) data to be processed for display
#3) display location, including various boxes
#4) type of object (text readout, graph, ext data)
        img = Image.new('RGBA', size, (255,255,255,0))
        draw = ImageDraw.Draw(img, 'RGBA')
        draw.text((0,0), text=data, font=font, fill="black")
        return img

def tempConvert(temp):
    #someday this will convert into whatever format i want
    return round(32 + (9 * temp / 5))

def getDataFromMysql(host="localhost", user="root", password=None, database="data", lookback=1, endTimeStamp=datetime.now(), dataSet="herpderp"):
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
#why is this not just a function of the Layout class? It's used exclusively for Layout objects
    boundryL = coords[0] + self.PadW
    boundryT = coords[1] + self.PadH
    boundryR = coords[2] - self.PadW
    boundryB = coords[3] - self.PadH
    return (boundryL, boundryT, boundryR, boundryB)

def generateDisplayData(keys, font):
#get this working, then move it to a different source file
    data = {}

    for i in keys:
        data[i] = {}
        data[i]['reading'] = getDataFromMysql(host="10.0.0.2", user="readonly", database="climate", lookback=5, dataSet=i)

    data['temp']['display'] = "{}°F".format(tempConvert(temp=data['temp']['reading']))
    data['humid']['display'] = "{}%".format(round(data['humid']['reading']))
    data['clock'] = {'display': datetime.now().strftime("%H:%M")}


    for i in data.keys():
        txt = data[i]['display']
        tmpLayer = Image.new('1', (0,0), 1)
        tmpDraw  = ImageDraw.Draw(tmpLayer, '1')
        dimensions = tmpDraw.textsize(txt, font=font)
        data[i]['img'] = generateDisplayImg(data=txt, font=font, size=dimensions)
    return data

class Layout:
    def __init__(self, width, height):
        self.image = Image.new('RGBA', (width, height), (255,0,255,255))
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
        self.LPanL = floor(self.LEFT)
        self.LPanR = floor(self.LPanL + self.LPanW)
        self.ClockT = floor(self.TOP)
        self.ClockB = floor(self.TOP + self.BoxHeight)

        self.TempT = floor(self.ClockB + self.BufferH)
        self.TempB = floor(self.TempT + self.BoxHeight)

        self.HumidT = floor(self.TempB + self.BufferH)
        self.HumidB = floor(self.HumidT + self.BoxHeight)

        self.RPanL = floor(self.LPanR + self.BufferW)
        self.RPanR = floor(self.RIGHT)
        self.Graph1T = floor(self.TOP)
        self.Graph1B = floor(self.Graph1T + self.Graph1H)

        self.Graph2T = floor(self.Graph1B + self.BufferH)
        self.Graph2B = floor(self.Graph2T + self.Graph2H)

        self.Graph3T = floor(self.Graph2B + self.BufferH)
        self.Graph3B = floor(self.BOTTOM)

        self.coords = {
            'clock':    (self.LPanL, self.ClockT,  self.LPanR, self.ClockB),
            'temp':     (self.LPanL, self.TempT,   self.LPanR, self.TempB),
            'humid':    (self.LPanL, self.HumidT,  self.LPanR, self.HumidB),
            'graph1':   (self.RPanL, self.Graph1T, self.RPanR, self.Graph1B),
            'graph2':   (self.RPanL, self.Graph2T, self.RPanR, self.Graph2B),
            'graph3':   (self.RPanL, self.Graph3T, self.RPanR, self.BOTTOM),
        }

        boxes = ['clock', 'temp', 'humid', 'graph1', 'graph2', 'graph3']
