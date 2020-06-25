from crop_line import *

class CropBoxManager():
    def __init__(self, parent, label, menubaroffset, bottombaroffset):
        self.parent = parent
        self.label = label
        self.labelx = self.label.winfo_x()
        self.labely = self.label.winfo_y()
        self.labelheight = self.label.winfo_height()
        self.labelwidth = self.label.winfo_width()
        self.photo = self.label.image
        self.labeloffsetx = self.labelwidth - self.photo.width()
        self.labeloffsety = self.labelheight - self.photo.height()
        self.bottombroffset = bottombaroffset
        self.menubaroffset = menubaroffset
        self.croplineoffset = 4

        #min and max values for croplines
        self.set_max_and_min()

        self.croplineL = CropLine(parent=parent,\
                                  position="L",\
                                  x=self.minx,\
                                  y=self.labely + menubaroffset + self.labeloffsety / 2,\
                                  length=self.photo.height(),\
                                  croplineoffset=self.croplineoffset)
        self.croplineR = CropLine(parent=parent,\
                                  position="R",\
                                  x=self.maxx,\
                                  y=self.labely + menubaroffset + self.labeloffsety / 2,\
                                  length=self.photo.height(),\
                                  croplineoffset=self.croplineoffset)
        self.croplineT = CropLine(parent=parent,\
                                  position="T",\
                                  x=self.labelx + self.labeloffsety / 2,\
                                  y=self.miny,\
                                  length=self.photo.width(),\
                                  croplineoffset=self.croplineoffset)
        self.croplineB = CropLine(parent=parent,\
                                  position="B",\
                                  x=self.labelx + self.labeloffsety / 2,\
                                  y=self.maxy,\
                                  length=self.photo.width(),\
                                  croplineoffset=self.croplineoffset)

        self.applylisteners(self.croplineL)
        self.applylisteners(self.croplineR)
        self.applylisteners(self.croplineT)
        self.applylisteners(self.croplineB)

        self.var = StringVar()
        self.var.set("x=0,y=0,h=" + str(self.photo.height()) + ",w=" \
                     + str(self.photo.width()))
        l = Label(parent, textvariable=self.var)
        l.place(x=7, y=30)

    def applylisteners(self, cropline):
        cropline.bind("<Button-1>", self.on_start)
        cropline.bind("<B1-Motion>", self.on_drag)

    def move_crop_lines(self):
        changex = self.labelx - self.label.winfo_x()
        changey = self.labely - self.label.winfo_y()
        self.labelx = self.label.winfo_x()
        self.labely = self.label.winfo_y()

        self.set_max_and_min()

        self.croplineR.place(x=(self.croplineR.winfo_x() - changex), y=(self.croplineR.winfo_y() - changey))
        self.croplineL.place(x=(self.croplineL.winfo_x() - changex), y=(self.croplineL.winfo_y() - changey))
        self.croplineT.place(x=(self.croplineT.winfo_x() - changex), y=(self.croplineT.winfo_y() - changey))
        self.croplineB.place(x=(self.croplineB.winfo_x() - changex), y=(self.croplineB.winfo_y() - changey))

    def set_max_and_min(self):
        self.minx = self.labelx + self.labeloffsetx / 2 - self.croplineoffset
        self.maxx = self.labelx + self.labelwidth - self.labeloffsetx / 2
        self.miny = self.labely + self.menubaroffset + self.labeloffsety / 2 - self.croplineoffset
        self.maxy = self.labely + self.labelheight + self.menubaroffset - self.labeloffsety / 2

    def on_start(self, event):
        widget = event.widget
        widget._drag_start_x = event.x
        widget._drag_start_y = event.y

    def on_drag(self, event):
        widget = event.widget
        if widget.position == "L":
            x = widget.winfo_x() - widget._drag_start_x + event.x
            Rx = self.croplineR.winfo_x()
            x = x if x >= self.minx else self.minx
            x = x if x <= Rx - self.croplineoffset - 2 else Rx - self.croplineoffset - 2
            y = widget.winfo_y()
        elif widget.position == "R":
            x = widget.winfo_x() - widget._drag_start_x + event.x
            Lx = self.croplineL.winfo_x()
            x = x if x >= Lx + self.croplineoffset + 2 else Lx + self.croplineoffset + 2
            x = x if x <= self.maxx else self.maxx
            y = widget.winfo_y()
        elif widget.position == "T":
            x = widget.winfo_x()
            y = widget.winfo_y() - widget._drag_start_y + event.y
            By = self.croplineB.winfo_y()
            y = y if y >= self.miny else self.miny
            y = y if y <= By - self.croplineoffset - 2 else By - self.croplineoffset - 2
        else:
            x = widget.winfo_x()
            y = widget.winfo_y() - widget._drag_start_y + event.y
            Ty = self.croplineT.winfo_y()
            y = y if y >= Ty + self.croplineoffset + 2 else Ty + self.croplineoffset + 2
            y = y if y <= self.maxy else self.maxy
        self.var.set("x=" + str(self.croplineL.winfo_x() + self.croplineoffset - int(((self.parent.winfo_width() - self.photo.width()) / 2))) \
                     + ",y=" + str(self.croplineT.winfo_y() + self.croplineoffset - int(((self.parent.winfo_height() - self.photo.height() + self.menubaroffset - self.bottombroffset) / 2))) \
                     + ",w=" + str((self.croplineR.winfo_x() - self.croplineL.winfo_x() - self.croplineoffset)) \
                     + ",h=" + str((self.croplineB.winfo_y() - self.croplineT.winfo_y() - self.croplineoffset)))
        self.parent.update_idletasks()
        widget.place(x=x, y=y)
