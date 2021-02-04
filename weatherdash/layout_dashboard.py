from PIL import Image,ImageDraw,ImageFont,ImageTk
import time
from urllib.request import urlopen
import mysql.connector as sql
#pip3 install mysql-connector-python
from datetime import timedelta, datetime
from math import floor

def displayDash(layout, data, debug):
    layout.image = Image.new('RGBA', (layout.image.width, layout.image.height), (255,0,255,255))
    layout.image.paste(layout.background) # = layout.background #Image.new('RGBA', (layout.image.width, layout.image.height), (255,0,255,255))
    for i in data.keys():
        data[i]['boxCoordinates'] = layout.coords[i]
        data[i]['textArea'] = getTextArea(layout, data[i]['boxCoordinates'])
        data[i]['pasteCoordinates'] = getCenteredPasteCoords(data[i]['textArea'], data[i]['img'])
        print(data[i])
        if debug:
            print("drawin box")
            layout.draw.rectangle(data[i]['boxCoordinates'], outline='black', fill=(255,255,255,255))
            print("drawin box2")
            layout.draw.rectangle(data[i]['textArea'], outline='black', fill=(255,255,0,255))
        layout.image.alpha_composite(data[i]['img'], dest=data[i]['pasteCoordinates'])
    return layout.image

def generateGraphUrl(key, coords):
    graphMetadata = {
        'graph1': {},
        'graph2': {},
        'graph3': {}
    }

    graphMetadata['graph1']['name'] = 'temp'
    graphMetadata['graph1']['dashId'] = '0PZFMkLMz'
    graphMetadata['graph1']['dashname'] = 'graph1'
    graphMetadata['graph1']['panelId'] = '2'

    graphMetadata['graph2']['name'] = 'temp'
    graphMetadata['graph2']['dashId'] = '44IpGkYMk'
    graphMetadata['graph2']['dashname'] = 'graph2'
    graphMetadata['graph2']['panelId'] = '2'

    graphMetadata['graph3']['name'] = 'temp'
    graphMetadata['graph3']['dashId'] = 'wQmTGkYGk'
    graphMetadata['graph3']['dashname'] = 'graph3'
    graphMetadata['graph3']['panelId'] = '2'

    height = coords[3]-coords[1]
    width = coords[2] - coords[0]

    grafanaUrl = "grafana.apartment:3000"
    tz = "America%2FLos_Angeles"
    orgId = '1'

    end = floor(time.time())
    start = end - 86400


    d = graphMetadata[key]

    url = "http://" \
        + grafanaUrl \
        + "/render/d-solo/" \
        + d['dashId'] \
        + "/" \
        + d['dashname'] \
        + "?orgId=" \
        + orgId \
        + "&from="\
        + f"{start*1000}" \
        + "&to=" \
        + f"{end*1000}" \
        + "&theme=light&panelId=" \
        + d['panelId'] \
        + "&width=" \
        + f"{width}" \
        + "&height=" \
        + f"{height}" \
        + "&tz=" \
        + tz
    return url

def generateDisplayData(keys, font, debug, coords):
    data = {}

    for i in keys:
        data[i] = {}
        if (i == "temp" or i == "humid"):
            data[i]['reading'] = getDataFromMysql(host="mysql.apartment", user="readonly", database="climate", lookback="live", dataSet=i, table="readings")
        if ( 'graph' in i):
            data[i]['url'] = generateGraphUrl(i, coords[i])

    if(debug):
        #temp, humidity are rounded to 2 decimal places, time is displayed with seconds
        data['temp']['display'] = "{}°F".format(round(tempConvert(temp=data['temp']['reading']),2))
        data['humid']['display'] = "{}%".format(round(data['humid']['reading'],2))
        data['clock'] = {'display': datetime.now().strftime("%H:%M:%S")}
    else:
        #temp, humidty are rounded to integer, time is HH:MM
        data['temp']['display'] = "{}°F".format(round(tempConvert(temp=data['temp']['reading'])))
        data['humid']['display'] = "{}%".format(round(data['humid']['reading']))
        data['clock'] = {'display': datetime.now().strftime("%H:%M")}

    for i in data.keys():
        tmpLayer = Image.new('1', (0,0), 1)
        tmpDraw  = ImageDraw.Draw(tmpLayer, '1')
        if (i == 'temp' or i == 'humid' or i == 'clock'):
            txt = data[i]['display']
            dimensions = tmpDraw.textsize(txt, font=font, stroke_width=1)
            data[i] = generateDisplayImg(data=txt, font=font, size=dimensions)
        if ('graph' in i):
            dimensions = [coords[i][2] - coords[i][0], coords[i][3] - coords[i][1]]
            print(f"attempting to curl {data[i]['url']}")
            data[i] = Image.open(urlopen(data[i]['url']))

    return data

def generateDisplayImg(data, font, size):
#it might be worth it to make this a class instead, like 'DisplayObject', but only if the class contains:
#1) source data
#2) data to be processed for display
#3) display location, including various boxes
#4) type of object (text readout, graph, ext data)
        img = Image.new('RGBA', size, (255,255,255,0))
        draw = ImageDraw.Draw(img, 'RGBA')
        draw.text((0,0), text=data, font=font, fill="black", stroke_width=1, stroke_fill="white")
        imgbox = img.getbbox()
        cropped = img.crop(imgbox)
        return cropped

def tempConvert(temp):
    #someday this will convert into whatever format i want
    return 32 + (9 * temp / 5)

def getCenteredPasteCoords(coords, obj):
    #dimensions of object to be pasted
    w2, h2 = obj.size

    #total width of text area
    w1 = coords[2] - coords[0]

    #total height of text area
    h1 = coords[3] - coords[1]

    x = floor(coords[0] + (w1 - w2) / 2)
    y = floor(coords[1] + (h1 - h2) / 2)
    return (max(x,0), max(y,0))

def getDataFromMysql(host="localhost", user="root", password=None, database="data", lookback=1, endTimeStamp=datetime.now(), dataSet="herpderp", table="data"):
#it would be better if this picked arbitrary data from the database given a time range
    if(password is None):
        db = sql.connect(host=host, user=user, database=database)
    else:
        db = sql.connect(host=host, user=user, database=database, password=password)

    cursor = db.cursor()
    if(lookback == "live"):
        query = f'SELECT {dataSet} FROM {table} order by id desc limit 1'
    else:
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


class Layout:
    def __init__(self, width, height):
        self.image = Image.new('RGBA', (width, height), (0,0,0,0))
        load = Image.open("bliss.jpg")
        load = load.resize((width, height), Image.ANTIALIAS)
        self.background = load.convert("RGBA")
        self.image = self.background
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
        #this should be a dict to make it easier to send to other functions
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
