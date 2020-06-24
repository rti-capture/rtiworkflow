from tkinter import *

class CropLine(Canvas):
    def __init__(self, parent, isVertial, x, y, length, croplineoffset):
        if isVertial:
            Canvas.__init__(self, parent, background="red", width=croplineoffset, height=length, highlightthickness=0)
        else:
            Canvas.__init__(self, parent, background="red", width=length, height=croplineoffset, highlightthickness=0)
        self.isVertical = isVertial
        self.place(x=x, y=y)


