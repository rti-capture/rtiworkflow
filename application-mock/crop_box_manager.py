from crop_line import *

class CropBoxManager():
    def __init__(self, parent, label, menubar_offset, bottom_bar_offset, scale):
        self.parent = parent
        self.label = label
        self.label_x = self.label.winfo_x()
        self.label_y = self.label.winfo_y()
        self.label_height = self.label.winfo_height()
        self.label_width = self.label.winfo_width()
        self.photo = self.label.image
        self.label_offset_x = self.label_width - self.photo.width()
        self.label_offset_y = self.label_height - self.photo.height()
        self.bottom_bar_offset = bottom_bar_offset
        self.menubar_offset = menubar_offset
        self.scale = scale
        self.cropline_offset = 4

        #sets intial min and max values for croplines
        self.set_max_and_min()

        self.cropline_L = CropLine(parent=parent,\
                                  position='L',\
                                  x=self.min_x,\
                                  y=self.label_y + menubar_offset + self.label_offset_y / 2,\
                                  length=self.photo.height(),\
                                  croplineoffset=self.cropline_offset)
        self.cropline_R = CropLine(parent=parent,\
                                  position='R',\
                                  x=self.max_x,\
                                  y=self.label_y + menubar_offset + self.label_offset_y / 2,\
                                  length=self.photo.height(),\
                                  croplineoffset=self.cropline_offset)
        self.cropline_T = CropLine(parent=parent,\
                                  position='T',\
                                  x=self.label_x + self.label_offset_y / 2,\
                                  y=self.min_y,\
                                  length=self.photo.width(),\
                                  croplineoffset=self.cropline_offset)
        self.cropline_B = CropLine(parent=parent,\
                                  position='B',\
                                  x=self.label_x + self.label_offset_y / 2,\
                                  y=self.max_y,\
                                  length=self.photo.width(),\
                                  croplineoffset=self.cropline_offset)

        self.applylisteners(self.cropline_L)
        self.applylisteners(self.cropline_R)
        self.applylisteners(self.cropline_T)
        self.applylisteners(self.cropline_B)

        self.var = StringVar()
        self.var.set('x=0,y=0,w=' + str(self.photo.width()) + ',h=' + str(self.photo.height()))
        self.crop = '0 0 ' + str(int(self.photo.width() / scale)) + ' ' + str(int(self.photo.height() / scale))
        self.values = Label(parent, textvariable=self.var)
        self.values.place(x=7, y=30)

    def applylisteners(self, cropline):
        cropline.bind('<Button-1>', self.on_start)
        cropline.bind('<B1-Motion>', self.on_drag)

    def move_crop_lines(self):
        change_x = self.label_x - self.label.winfo_x()
        change_y = self.label_y - self.label.winfo_y()
        self.label_x = self.label.winfo_x()
        self.label_y = self.label.winfo_y()

        self.set_max_and_min()

        self.cropline_R.place(x=(self.cropline_R.winfo_x() - change_x), y=(self.cropline_R.winfo_y() - change_y))
        self.cropline_L.place(x=(self.cropline_L.winfo_x() - change_x), y=(self.cropline_L.winfo_y() - change_y))
        self.cropline_T.place(x=(self.cropline_T.winfo_x() - change_x), y=(self.cropline_T.winfo_y() - change_y))
        self.cropline_B.place(x=(self.cropline_B.winfo_x() - change_x), y=(self.cropline_B.winfo_y() - change_y))

    def set_max_and_min(self):
        self.min_x = self.label_x + self.label_offset_x / 2 - self.cropline_offset
        self.max_x = self.label_x + self.label_width - self.label_offset_x / 2
        self.min_y = self.label_y + self.menubar_offset + self.label_offset_y / 2 - self.cropline_offset
        self.max_y = self.label_y + self.label_height + self.menubar_offset - self.label_offset_y / 2

    def on_start(self, event):
        widget = event.widget
        widget._drag_start_x = event.x
        widget._drag_start_y = event.y

    def on_drag(self, event):
        widget = event.widget
        offset = 2
        if widget.position == 'L':
            x = widget.winfo_x() - widget._drag_start_x + event.x
            Rx = self.cropline_R.winfo_x()
            x = x if x >= self.min_x else self.min_x
            x = x if x <= Rx - self.cropline_offset - offset else Rx - self.cropline_offset - offset
            y = widget.winfo_y()
        elif widget.position == 'R':
            x = widget.winfo_x() - widget._drag_start_x + event.x
            Lx = self.cropline_L.winfo_x()
            x = x if x >= Lx + self.cropline_offset + offset else Lx + self.cropline_offset + offset
            x = x if x <= self.max_x else self.max_x
            y = widget.winfo_y()
        elif widget.position == 'T':
            x = widget.winfo_x()
            y = widget.winfo_y() - widget._drag_start_y + event.y
            By = self.cropline_B.winfo_y()
            y = y if y >= self.min_y else self.min_y
            y = y if y <= By - self.cropline_offset - offset else By - self.cropline_offset - offset
        else:
            x = widget.winfo_x()
            y = widget.winfo_y() - widget._drag_start_y + event.y
            Ty = self.cropline_T.winfo_y()
            y = y if y >= Ty + self.cropline_offset + offset else Ty + self.cropline_offset + offset
            y = y if y <= self.max_y else self.max_y
        crop_x = str(self.cropline_L.winfo_x() + self.cropline_offset - int(((self.parent.winfo_width() - self.photo.width()) / 2)))
        crop_y = str(self.cropline_T.winfo_y() + self.cropline_offset - int(((self.parent.winfo_height() - self.photo.height() + self.menubar_offset - self.bottom_bar_offset) / 2)))
        crop_w = str((self.cropline_R.winfo_x() - self.cropline_L.winfo_x() - self.cropline_offset))
        crop_h = str((self.cropline_B.winfo_y() - self.cropline_T.winfo_y() - self.cropline_offset))
        self.var.set('x=' + crop_x + ',y=' + crop_y + ',w=' + crop_w + ',h=' + crop_h)
        self.crop = str(int(int(crop_x) / self.scale)) + ' ' + str(int(int(crop_y) / self.scale)) + ' ' + str(int(int(crop_w) / self.scale)) + ' ' + str(int(int(crop_h) / self.scale))
        #updates string var
        self.parent.update_idletasks()
        widget.place(x=x, y=y)

    def clear_cropping(self):
        self.values.destroy()
        self.label.destroy()
        self.cropline_L.destroy()
        self.cropline_R.destroy()
        self.cropline_T.destroy()
        self.cropline_B.destroy()

    def return_crop(self):
        return self.crop
