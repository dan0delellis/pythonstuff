def getTextWidth(draw):
    clockTx = "88:88"
    clockSz = 36
    clockFt = ImageFont.truetype('Charcoal.ttf', clockSz)

    tempTx = "888F"
    tempSz = clockSz
    tempFt = clockFt

    humidTx = "888%"
    humidSz = clockSz
    humidFt = clockFt

    (cW, cH) = draw.textsize(clockTx, clockFt)
    (tW, tH) = draw.textsize(tempTx, tempFt)
    (hW, hT) = draw.textsize(humidTx, humidFt)
    return max(cW, tW, hW)

def getCoords(obj):
    coords = {
        'clock':    [self.LPanL, self.ClockT,  self.LPanR, self.ClockB],
        'temp':     [self.LPanL, self.TempT,   self.LPanR, self.TempB],
        'humid':    [self.LPanL, self.HumidT,  self.LPanR, self.HumidB],
        'graph1':   [self.RPanL, self.Graph1T, self.RPanR, self.Graph1B],
        'graph2':   [self.RPanL, self.Graph2T, self.RPanR, self.Graph2B],
        'graph3':   [self.RPanL, self.Graph3T, self.RPanR, self.BOTTOM],
    }
    return coords[obj]

