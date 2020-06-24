'''
Tasks:
get new dimensions of image
'''

from crop_line import *

class CropBoxManager():
    def __init__(self, parent, label, menubaroffset):
        self.label = label
        self.labelx = self.label.winfo_x()
        self.labely = self.label.winfo_y()
        self.labelheight = self.label.winfo_height()
        self.labelwidth = self.label.winfo_width()

        self.menubaroffset = menubaroffset
        self.croplineoffset = 3

        #min and max values for croplines
        self.minx = self.labelx
        self.midx = self.labelx + self.labelwidth / 2
        self.maxx = self.labelx + self.labelwidth - self.croplineoffset
        self.miny = self.labely + self.menubaroffset
        self.midy = self.labely + self.menubaroffset + self.labelheight / 2
        self.maxy = self.labely + self.menubaroffset + self.labelheight - self.croplineoffset

        self.croplineL = CropLine(parent, "L", self.labelx, self.labely + menubaroffset, self.labelheight, self.croplineoffset)
        self.croplineR = CropLine(parent, "R", self.labelx + self.labelwidth - self.croplineoffset, self.labely + menubaroffset, self.labelheight, self.croplineoffset)
        self.croplineT = CropLine(parent, "T", self.labelx, self.labely + menubaroffset, self.labelwidth, self.croplineoffset)
        self.croplineB = CropLine(parent, "B", self.labelx, self.labely + self.labelheight + menubaroffset - self.croplineoffset, self.labelwidth, self.croplineoffset)

        self.croplineL.bind("<Button-1>", self.on_start)
        self.croplineL.bind("<B1-Motion>", self.on_drag)
        self.croplineR.bind("<Button-1>", self.on_start)
        self.croplineR.bind("<B1-Motion>", self.on_drag)
        self.croplineT.bind("<Button-1>", self.on_start)
        self.croplineT.bind("<B1-Motion>", self.on_drag)
        self.croplineB.bind("<Button-1>", self.on_start)
        self.croplineB.bind("<B1-Motion>", self.on_drag)

    def move_crop_lines(self):
        changex = self.labelx - self.label.winfo_x()
        changey = self.labely - self.label.winfo_y()
        self.labelx = self.label.winfo_x()
        self.labely = self.label.winfo_y()

        self.minx = self.labelx
        self.midx = self.labelx + self.labelwidth / 2
        self.maxx = self.labelx + self.labelwidth - self.croplineoffset
        self.miny = self.labely + self.menubaroffset
        self.midy = self.labely + self.menubaroffset + self.labelheight / 2
        self.maxy = self.labely + self.menubaroffset + self.labelheight - self.croplineoffset

        self.croplineR.place(x=(self.croplineR.winfo_x() - changex), y=(self.croplineR.winfo_y() - changey))
        self.croplineL.place(x=(self.croplineL.winfo_x() - changex), y=(self.croplineL.winfo_y() - changey))
        self.croplineT.place(x=(self.croplineT.winfo_x() - changex), y=(self.croplineT.winfo_y() - changey))
        self.croplineB.place(x=(self.croplineB.winfo_x() - changex), y=(self.croplineB.winfo_y() - changey))

    def on_start(self, event):
        widget = event.widget
        widget._drag_start_x = event.x
        widget._drag_start_y = event.y

    def on_drag(self, event):
        widget = event.widget
        if widget.position == "L":
            x = widget.winfo_x() - widget._drag_start_x + event.x
            x = x if x >= self.minx else self.minx
            x = x if x <= self.midx - 2 else self.midx - 2
            y = widget.winfo_y()
        elif widget.position == "R":
            x = widget.winfo_x() - widget._drag_start_x + event.x
            x = x if x >= self.midx + self.croplineoffset + 2 else self.midx + self.croplineoffset + 2
            x = x if x <= self.maxx else self.maxx
            y = widget.winfo_y()
        elif widget.position == "T":
            x = widget.winfo_x()
            y = widget.winfo_y() - widget._drag_start_y + event.y
            y = y if y >= self.miny else self.miny
            y = y if y <= self.midy - 2 else self.midy - 2
        else:
            x = widget.winfo_x()
            y = widget.winfo_y() - widget._drag_start_y + event.y
            y = y if y >= self.midy + self.croplineoffset + 2 else self.midy + self.croplineoffset + 2
            y = y if y <= self.maxy else self.maxy
        widget.place(x=x, y=y)
