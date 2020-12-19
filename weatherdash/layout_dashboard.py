from PIL import Image,ImageDraw,ImageFont,ImageTk
import time

class Layout:
    def __init__(self, width, height, debug):
        def getTextArea(self, coords):
            boundryL = coords[0] + self.PadW
            boundryT = coords[1] + self.PadH
            boundryR = coords[2] - self.PadW
            boundryB = coords[3] - self.PadH
            return [boundryL, boundryT, boundryR, boundryB]

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
