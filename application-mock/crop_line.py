from tkinter import *


class CropLine(Canvas):
    def __init__(self, parent, position, x, y, length, croplineoffset):
        if position == 'L' or position == 'R':
            Canvas.__init__(self, parent, background='red', width=croplineoffset, height=length, highlightthickness=0)
        else:
            Canvas.__init__(self, parent, background='red', width=length, height=croplineoffset, highlightthickness=0)
        self.position = position
        self.place(x=x, y=y)
