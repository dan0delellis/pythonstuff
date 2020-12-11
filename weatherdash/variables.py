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
