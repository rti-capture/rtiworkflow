from crop_line import *


class CropBoxManager:
    def __init__(self, parent, label, menubar_offset, bottom_bar_offset):
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
        self.scale_x = 1000 / self.label.winfo_width()
        self.scale_y = 1000 / self.label.winfo_height()
        self.crop_line_offset = 4
        self.min_x = None
        self.max_x = None
        self.min_y = None
        self.max_y = None

        # sets initial min and max values for crop lines
        self.set_max_and_min()

        self.crop_line_L = CropLine(parent=parent, \
                                    position='L', \
                                    x=self.min_x, \
                                    y=self.label_y + menubar_offset + self.label_offset_y / 2, \
                                    length=self.photo.height(), \
                                    croplineoffset=self.crop_line_offset)
        self.crop_line_R = CropLine(parent=parent, \
                                    position='R', \
                                    x=self.max_x, \
                                    y=self.label_y + menubar_offset + self.label_offset_y / 2, \
                                    length=self.photo.height(), \
                                    croplineoffset=self.crop_line_offset)
        self.crop_line_T = CropLine(parent=parent, \
                                    position='T', \
                                    x=self.label_x + self.label_offset_y / 2, \
                                    y=self.min_y, \
                                    length=self.photo.width(), \
                                    croplineoffset=self.crop_line_offset)
        self.crop_line_B = CropLine(parent=parent, \
                                    position='B', \
                                    x=self.label_x + self.label_offset_y / 2, \
                                    y=self.max_y, \
                                    length=self.photo.width(), \
                                    croplineoffset=self.crop_line_offset)

        self.applylisteners(self.crop_line_L)
        self.applylisteners(self.crop_line_R)
        self.applylisteners(self.crop_line_T)
        self.applylisteners(self.crop_line_B)

        self.var = StringVar()
        self.var.set('x=0,y=0,w=' + str(self.photo.width()) + ',h=' + str(self.photo.height()))
        self.crop = '0 0 ' + str(int(self.photo.width() * self.scale_x)) + ' ' + str(int(self.photo.height() * self.scale_y))
        self.values = Label(parent, textvariable=self.var)
        self.values.place(x=7, y=30)

    def applylisteners(self, crop_line):
        crop_line.bind('<Button-1>', self.on_start)
        crop_line.bind('<B1-Motion>', self.on_drag)

    def move_crop_lines(self):
        change_x = self.label_x - self.label.winfo_x()
        change_y = self.label_y - self.label.winfo_y()
        self.label_x = self.label.winfo_x()
        self.label_y = self.label.winfo_y()

        self.set_max_and_min()

        self.crop_line_R.place(x=(self.crop_line_R.winfo_x() - change_x), y=(self.crop_line_R.winfo_y() - change_y))
        self.crop_line_L.place(x=(self.crop_line_L.winfo_x() - change_x), y=(self.crop_line_L.winfo_y() - change_y))
        self.crop_line_T.place(x=(self.crop_line_T.winfo_x() - change_x), y=(self.crop_line_T.winfo_y() - change_y))
        self.crop_line_B.place(x=(self.crop_line_B.winfo_x() - change_x), y=(self.crop_line_B.winfo_y() - change_y))

    def set_max_and_min(self):
        self.min_x = self.label_x + self.label_offset_x / 2 - self.crop_line_offset
        self.max_x = self.label_x + self.label_width - self.label_offset_x / 2
        self.min_y = self.label_y + self.menubar_offset + self.label_offset_y / 2 - self.crop_line_offset
        self.max_y = self.label_y + self.label_height + self.menubar_offset - self.label_offset_y / 2

    def on_start(self, event):
        widget = event.widget
        widget.drag_start_x = event.x
        widget.drag_start_y = event.y

    def on_drag(self, event):
        widget = event.widget
        offset = 2
        if widget.position == 'L':
            x = widget.winfo_x() - widget.drag_start_x + event.x
            r_x = self.crop_line_R.winfo_x()
            x = x if x >= self.min_x else self.min_x
            x = x if x <= r_x - self.crop_line_offset - offset else r_x - self.crop_line_offset - offset
            y = widget.winfo_y()
        elif widget.position == 'R':
            x = widget.winfo_x() - widget.drag_start_x + event.x
            l_x = self.crop_line_L.winfo_x()
            x = x if x >= l_x + self.crop_line_offset + offset else l_x + self.crop_line_offset + offset
            x = x if x <= self.max_x else self.max_x
            y = widget.winfo_y()
        elif widget.position == 'T':
            x = widget.winfo_x()
            y = widget.winfo_y() - widget.drag_start_y + event.y
            b_y = self.crop_line_B.winfo_y()
            y = y if y >= self.min_y else self.min_y
            y = y if y <= b_y - self.crop_line_offset - offset else b_y - self.crop_line_offset - offset
        else:
            x = widget.winfo_x()
            y = widget.winfo_y() - widget.drag_start_y + event.y
            t_y = self.crop_line_T.winfo_y()
            y = y if y >= t_y + self.crop_line_offset + offset else t_y + self.crop_line_offset + offset
            y = y if y <= self.max_y else self.max_y
        crop_x = str(self.crop_line_L.winfo_x() + self.crop_line_offset - int(
            ((self.parent.winfo_width() - self.photo.width()) / 2)))
        crop_y = str(self.crop_line_T.winfo_y() + self.crop_line_offset - int(
            ((self.parent.winfo_height() - self.photo.height() + self.menubar_offset - self.bottom_bar_offset) / 2)))
        crop_w = str((self.crop_line_R.winfo_x() - self.crop_line_L.winfo_x() - self.crop_line_offset))
        crop_h = str((self.crop_line_B.winfo_y() - self.crop_line_T.winfo_y() - self.crop_line_offset))
        self.var.set('x=' + crop_x + ',y=' + crop_y + ',w=' + crop_w + ',h=' + crop_h)
        self.crop = str(int(int(crop_x) * self.scale_x)) + ' ' + str(int(int(crop_y) * self.scale_y)) + ' ' + str(
            int(int(crop_w) * self.scale_x)) + ' ' + str(int(int(crop_h) * self.scale_y))
        # updates string var
        self.parent.update_idletasks()
        widget.place(x=x, y=y)

    def clear_cropping(self):
        self.values.destroy()
        self.label.destroy()
        self.crop_line_L.destroy()
        self.crop_line_R.destroy()
        self.crop_line_T.destroy()
        self.crop_line_B.destroy()

    def return_crop(self):
        return self.crop
