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

        self.croplineL = CropLine(parent, True, self.labelx, self.labely + menubaroffset, self.labelheight, self.croplineoffset)
        self.croplineR = CropLine(parent, True, self.labelx + self.labelwidth - self.croplineoffset, self.labely + menubaroffset, self.labelheight, self.croplineoffset)
        self.croplineT = CropLine(parent, False, self.labelx, self.labely + menubaroffset, self.labelwidth, self.croplineoffset)
        self.croplineB = CropLine(parent, False, self.labelx, self.labely + self.labelheight + menubaroffset - self.croplineoffset, self.labelwidth, self.croplineoffset)

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
        """
        if x > 202:
            x = 202
        elif x < 0:
            x = 0
        print(x)
        """
        if (widget.isVertical):
            x = widget.winfo_x() - widget._drag_start_x + event.x
            y = widget.winfo_y()
        else:
            x = widget.winfo_x()
            y = widget.winfo_y() - widget._drag_start_y + event.y
        print(y)
        widget.place(x=x, y=y)
