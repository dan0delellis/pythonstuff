    #####################################################
    #                                                   #
    #     Yx      Ax  Bx                          Zx    #
    #    +----------------------------------------+Uy   #
    #    |       |_W_|                            |     #
    #    | 12:34 |   |                            |     #
    #  Cy|_______|   |      graph                 |     #
    #  Dy|-------|   |____________________________|Gy   #
    #    | 123F  |   |----------------------------|Hy   #
    #  Ey|_______|   |         graph?             |     #
    #  Fy|-------|   |____________________________|Iy   #
    #    | 23%   |   |----------------------------|Jy   #
    #    |       |   |           ?????            |     #
    #    +----------------------------------------+Vy   #
    #                                                   #
    #####################################################

Yx = left edge + edge buffer width                         (LEFT)      =   (LPanL)

Ax = edge of left panel                                    (LPanR)

Bx = edge of left panel + buffer width                     (RPanL)

Zx = right edge - edge buffer width                        (RIGHT)     =   (RPanR)

Uy = top + edge buffer height                              (TOP)       =   (ClockT)    =   (Graph1T)

Cy = bottom of clock area                                  (ClockB)

Dy = top of temp area = Cy+vbuffer height                  (TempT)

Ey = bottom of temp area                                   (TempB)

Fy = top of humidty area  = Ey + vbuffer height            (HumidT)

Gy = bottom of top graph                                   (Graph1B)

Hy = top of middle graph = Gy + vbuffer                    (Graph2T)

Iy = bottom of middle graph                                (Graph2B)

Jy = top of bottom area                                    (Graph3T)

Vy = bottom - edge buffer height                           (BOTTOM)    =   (HumidB)    =   (Graph3B)
